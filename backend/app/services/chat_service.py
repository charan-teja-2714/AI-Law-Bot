import os
import io
from fastapi import UploadFile
from app.services.pdf import process_pdf, chunk_text, create_pinecone_index, generate_pdf_response, embeddings
from app.services.question_recommender import generate_doctor_questions as gen_questions
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        self.sessions = {}  # session_id -> {pinecone_index, pdf_name}
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.6
        )
    
    async def process_pdf(self, file: UploadFile, session_id: str):
        # Read file content
        content = await file.read()
        
        # Create a file-like object for existing process_pdf function
        class UploadedFile:
            def __init__(self, name, content):
                self.name = name
                self._content = content
            
            def read(self):
                return self._content
        
        uploaded_pdf = UploadedFile(file.filename, content)
        
        # REUSE existing logic
        texts, meta = process_pdf(uploaded_pdf)
        chunks, metas = chunk_text(texts, meta)
        index = create_pinecone_index(chunks, metas)
        
        # Store in session
        self.sessions[session_id] = {
            "pinecone_index": index,
            "pdf_name": file.filename
        }
        
        return {"pdf_name": file.filename}
    
    async def generate_response(self, session_id: str, message: str, role: str):
        if session_id not in self.sessions:
            return "❌ Please upload a PDF first."
        
        session = self.sessions[session_id]
        
        # Call existing function with required parameters
        response = generate_pdf_response(
            user_query=message,
            index=session["pinecone_index"],
            pdf_name=session["pdf_name"],
            role=role
        )
        return response
    
    async def generate_doctor_questions(self, session_id: str):
        if session_id not in self.sessions:
            raise Exception("No PDF uploaded for this session")
        
        session = self.sessions[session_id]
        
        # Query Pinecone for context
        query_vec = embeddings.embed_query("important findings in this medical report")
        
        retrieved = session["pinecone_index"].query(
            vector=query_vec,
            top_k=5,
            include_metadata=True,
            filter={"source": session["pdf_name"]}
        )
        
        context = "\n\n".join(
            m["metadata"]["text"] for m in retrieved["matches"]
        )
        
        # REUSE existing question generation logic
        questions = gen_questions(context=context, llm=self.llm)
        return questions
