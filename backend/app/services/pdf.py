import os, io, tempfile, re
import numpy as np
from dotenv import load_dotenv

load_dotenv()


from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "medisense-rag"

bm25 = BM25Encoder().default()


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

embeddings = get_embeddings()
EMBEDDING_DIM = len(embeddings.embed_query("dimension_check"))


def process_pdf(uploaded_pdf):
    if isinstance(uploaded_pdf, list):
        uploaded_pdf = uploaded_pdf[0]

    pdf_stream = io.BytesIO(uploaded_pdf.read())
    reader = PdfReader(pdf_stream)

    texts, metadata = [], []

    for page_num, page in enumerate(reader.pages):
        try:
            text = page.extract_text()
        except Exception:
            continue

        if text and text.strip():
            texts.append(text)
            metadata.append({"source": uploaded_pdf.name, "page": page_num})
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_stream.getbuffer())
                tmp.close()
                images = convert_from_path(
                    tmp.name, first_page=page_num + 1, last_page=page_num + 1
                )
                for img in images:
                    ocr_text = pytesseract.image_to_string(img)
                    texts.append(ocr_text)
                    metadata.append(
                        {"source": uploaded_pdf.name, "page": page_num, "ocr": True}
                    )
                os.remove(tmp.name)

    return texts, metadata


LAB_LINE = re.compile(
    r"([A-Za-z\s]+)\s*[:\-]\s*([\d\.]+)\s*([a-zA-Z/%]+)?",
    re.IGNORECASE
)

def medical_aware_chunking(text):
    lines = text.split("\n")
    buffer, chunks = [], []

    for line in lines:
        buffer.append(line)

        if LAB_LINE.search(line):
            continue

        if len(" ".join(buffer)) > 700:
            chunks.append(" ".join(buffer))
            buffer = []

    if buffer:
        chunks.append(" ".join(buffer))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    final_chunks = []
    for chunk in chunks:
        final_chunks.extend(splitter.split_text(chunk))

    return final_chunks

def chunk_text(text_list, metadata_list):
    all_chunks, all_meta = [], []

    for text, meta in zip(text_list, metadata_list):
        chunks = medical_aware_chunking(text)
        all_chunks.extend(chunks)
        all_meta.extend([meta] * len(chunks))
    return all_chunks, all_meta


def create_pinecone_index(chunks, metas):
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="dotproduct",
            spec=ServerlessSpec(
                cloud="aws",
                region=os.getenv("PINECONE_ENVIRONMENT")
            )
        )

    index = pc.Index(INDEX_NAME)

    source_name = metas[0]["source"]
    index.delete(filter={"source": metas[0]["source"]})


    vectors = []
    for i, (text, meta) in enumerate(zip(chunks, metas)):
        vectors.append({
            "id": f"{meta['source']}_{meta['page']}_{i}",
            "values": embeddings.embed_query(text),
            "sparse_values": bm25.encode_documents([text])[0],
            "metadata": meta | {"text": text}
        })

    index.upsert(vectors)
    return index



def rewrite_query(query):
    prompt = PromptTemplate(
        template="Refine the following question for better document retrieval:\n{query}",
        input_variables=["query"]
    )
    return LLMChain(llm=llm, prompt=prompt).run(query)

def retrieve_with_rerank(query, index, pdf_name, top_k=12, final_k=5):
    dense_vec = embeddings.embed_query(query)
    sparse_vec = bm25.encode_queries([query])[0]

    response = index.query(
        vector=dense_vec,
        sparse_vector=sparse_vec,
        top_k=top_k,
        include_metadata=True,
        filter={"source": pdf_name}
    )


    docs = [m["metadata"]["text"] for m in response["matches"]]

    scored = []
    for doc in docs:
        doc_emb = embeddings.embed_query(doc)
        score = np.dot(dense_vec, doc_emb) / (
            np.linalg.norm(dense_vec) * np.linalg.norm(doc_emb)
        )
        scored.append((score, doc))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [d for _, d in scored[:final_k]]

def generate_pdf_response(user_query, index, pdf_name, role="patient"):
    if not index:
        return "❌ Upload a PDF first."

    optimized_query = rewrite_query(user_query)
    docs = retrieve_with_rerank(optimized_query, index, pdf_name)

    context = "\n\n".join(docs)

    # prompt = PromptTemplate(
    #     template="""
    # You are a **patient-friendly medical report explanation assistant**.

    # Your goal is to help a **normal person with no medical background**
    # clearly understand their medical report without confusion or fear.

    # --------------------------------
    # 📄 Medical Context:
    # {context}

    # ❓ Patient Question:
    # {question}

    # --------------------------------
    # 🧠 How to respond:

    # Tone:
    # - Calm, friendly, reassuring
    # - Natural, human (like ChatGPT)
    # - Simple everyday language

    # Structure (IMPORTANT):
    # - Avoid long paragraphs
    # - Prefer **short bullet points** for explanations
    # - Use **bold text** for important terms or values
    # - If a medical term appears, explain it briefly in brackets (only once)

    # How to explain:
    # - Focus on **what the report is about**
    # - Explain **only important numbers**
    # - Do NOT diagnose or suggest treatment
    # - Do NOT overwhelm the user

    # 1.**Start with ONE clear heading**
    # - The heading should reflect the user’s question or topic
    # - Keep it short and natural (not technical)

    # 2.**Main explanation**
    # - Explain the answer in short, smooth paragraphs
    # - Highlight important ideas using **bold text**
    # - If a medical term appears, explain it briefly in brackets

    # 3.**Focused explanation (ONLY if applicable)**
    # - If the question is about a specific test, condition, or value,
    #     add a small section like:
    #     **“What this means”** or **“About this test”**
    # - Explain it in 2–4 simple lines or a few gentle bullet points
    # - Skip this section if it is not needed

    # 4. **Summary (end with this)**
    # - End with a short **Summary** (2–3 lines)
    # - Clearly state the main takeaway in simple words
    # - Be reassuring
    # - If relevant, gently suggest discussing with a doctor

    # --------------------------------
    # 🧾 Answer:
    # """,
    #     input_variables=["context", "question"]
    # )


    prompt = PromptTemplate(
        template="""
    You are a medical report explanation assistant.

    --------------------------------
    📄 Medical Context:
    {context}

    ❓ User Question:
    {question}

    --------------------------------
    ROLE MODE: {role}

    Response Rules (STRICT):
    - Do NOT diagnose
    - Do NOT suggest treatment or medication
    - Do NOT predict diseases
    - Do NOT use alarming language

    If ROLE MODE = patient:
    - Use very simple language
    - Explain medical terms in brackets (once)
    - Avoid technical jargon
    - Be calm and reassuring

    If ROLE MODE = doctor:
    - Use slightly technical language
    - Be structured and factual
    - Mention reference ranges if available
    - Still NO diagnosis or treatment

    Response Structure:
    1. One clear heading
    2. Main explanation (short paragraphs or bullets)
    3. Optional “What this means” section (only if relevant)
    4. Short summary (2–3 lines, reassuring)

    --------------------------------
    🧾 Answer:
    """,
        input_variables=["context", "question", "role"]
    )




    response_msg = (prompt | llm).invoke({
        "context": context,
        "question": user_query,
        "role": role
    })

    response_text = response_msg.content.strip()

    return response_text
