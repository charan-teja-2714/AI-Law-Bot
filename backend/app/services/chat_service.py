import os
from typing import Dict, Any, List
from fastapi import UploadFile
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

from app.services.faiss_store import faiss_store
from app.services.document_processor import document_processor
from app.services.translation_service import translation_service
from app.services.speech_to_text import speech_to_text_service
from app.services.legal_section_predictor import legal_predictor

load_dotenv()


class ChatService:
    """
    Main chat service for AI Law Bot
    Handles document upload, RAG-based Q&A, legal section prediction
    """

    def __init__(self):
        self.sessions = {}  # session_id -> {doc_name, language}
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.6
        )

    async def process_document(self, file: UploadFile, session_id: str, document_id: str):
        """
        Process PDF/text document and create FAISS index

        Args:
            file: Uploaded document file
            session_id: Unique session ID
            document_id: Unique document ID

        Returns:
            Dict with document info
        """
        # Read file content
        content = await file.read()

        # Create file-like object
        class UploadedFile:
            def __init__(self, name, content):
                self.name = name
                self._content = content

            def read(self):
                return self._content

        uploaded_doc = UploadedFile(file.filename, content)

        # Process document
        texts, metadata = document_processor.process_pdf(uploaded_doc)
        chunks, metas = document_processor.chunk_documents(texts, metadata)

        # Create FAISS index with document_id
        faiss_store.create_index(chunks, metas, session_id, document_id)

        return {"doc_name": file.filename, "chunks_created": len(chunks), "document_id": document_id}

    async def process_audio_video(self, file: UploadFile, session_id: str, document_id: str):
        """
        Process audio/video file, extract text, and create FAISS index

        Args:
            file: Uploaded audio/video file
            session_id: Session ID
            document_id: Document ID

        Returns:
            Dict with transcription info
        """
        # Transcribe audio/video
        result = await speech_to_text_service.process_file(file)

        # Create document from transcript
        doc_text = result["text"]

        # Chunk the transcript
        chunks = document_processor.legal_aware_chunking(doc_text)

        # Create metadata
        metadata = [
            {
                "source": file.filename,
                "type": result["file_type"],
                "language": result["language"],
                "text": chunk
            }
            for chunk in chunks
        ]

        # Create FAISS index with document_id
        faiss_store.create_index(chunks, metadata, session_id, document_id)

        return {
            "doc_name": file.filename,
            "transcription": doc_text,
            "language": result["language"],
            "file_type": result["file_type"],
            "document_id": document_id
        }

    async def generate_response(
        self,
        session_id: str,
        message: str,
        user_language: str = "en",
        structured_output: bool = False,
        chat_history: list = None
    ) -> Dict[str, Any]:
        """
        Generate response to user query

        Args:
            session_id: Session ID
            message: User query
            user_language: User's language (en, hi, te, ta)
            structured_output: Whether to return structured legal analysis
            chat_history: List of previous messages [{"role": "user"/"assistant", "content": "..."}]

        Returns:
            Dict with response and metadata
        """
        # Translate query to English if needed
        if user_language != "en":
            print(f"[TRANSLATION] Translating user query from {user_language} to English")
            translation_result = translation_service.process_user_input(message)
            english_query = translation_result["english_text"]
            print(f"[TRANSLATION] Original: {message[:100]}")
            print(f"[TRANSLATION] English: {english_query[:100]}")
        else:
            english_query = message

        # Rewrite query to fix typos/unclear phrasing before FAISS search.
        # The frontend always shows the original user text — only the search/context uses this.
        search_query = english_query
        try:
            rewrite_prompt = PromptTemplate(
                template="""Fix any spelling errors and rephrase this legal query to be clearer. Return ONLY the corrected query text, nothing else. If the query is already clear and correct, return it unchanged.

Query: {query}

Corrected query:""",
                input_variables=["query"]
            )
            rewritten = (rewrite_prompt | self.llm).invoke({"query": english_query})
            rewritten_text = rewritten.content.strip()
            if rewritten_text:
                search_query = rewritten_text
                if search_query != english_query:
                    print(f"[REWRITE] Original:  {english_query[:120]}")
                    print(f"[REWRITE] Rewritten: {search_query[:120]}")
        except Exception as e:
            print(f"[REWRITE] Skipped ({e})")

        # Retrieve relevant context from FAISS using the cleaned query
        context = ""
        if session_id in self.sessions or True:  # Always try to query
            results = faiss_store.query(
                session_id=session_id,
                query_text=search_query,
                top_k=5,
                document_ids=None  # Query all documents
            )
            if results:
                context = "\n\n".join([r["text"] for r in results])

        # If structured output requested, use legal predictor (only if document uploaded)
        if structured_output and context:
            structured_analysis = legal_predictor.predict_sections(
                english_query,
                context
            )
            return {
                "type": "structured",
                "analysis": structured_analysis,
                "language": user_language
            }

        # Format conversation history for the prompt
        history_text = ""
        if chat_history:
            for msg in chat_history:
                role_label = "User" if msg["role"] == "user" else "Assistant"
                # Truncate long messages to avoid bloating the prompt
                content = msg["content"][:600] if len(msg["content"]) > 600 else msg["content"]
                history_text += f"{role_label}: {content}\n\n"

        # Generate response using LLM with comprehensive legal analysis
        # Works with or without document context
        prompt = PromptTemplate(
                template="""You are an expert AI Legal Assistant specializing in Indian law with deep knowledge of IPC, CrPC, BNS, and Indian legal procedures.

Legal Context (Retrieved from Document):
{context}

Previous Conversation:
{history}

User Question:
{question}

RESPONSE GUIDELINES:

0. **CRITICAL - Document Context Check:**
   - If the user asks to "summarize", "analyze", "explain", "review", or "describe" a document/report/file/case, AND the Legal Context above is empty:
     → Respond ONLY with: "No document has been uploaded. Please upload a PDF or audio/video file first, then ask me to summarize or analyze it."
   - Do NOT use Previous Conversation content to answer document-related requests
   - Only answer from Legal Context when the user references an uploaded document

1. **CRITICAL - Legal Questions ONLY:**
   - Answer questions related to ANY area of Indian law or law in general
   - Valid legal topics include (but are NOT limited to):
     * Criminal law: IPC, BNS, CrPC, BNSS, FIR, bail, arrest, trial
     * Civil law: contracts, property, torts, damages
     * Intellectual Property: Copyright Act 1957, Patents Act 1970, Trademarks Act 1999, Trade Secrets, AI-generated content ownership
     * Employment & Labour: Industrial Disputes Act, Factories Act, POSH Act, wrongful termination
     * Constitutional law: fundamental rights, writs, PIL
     * Cyber law: IT Act 2000, data privacy, online offences
     * Family law: divorce, maintenance, custody, inheritance, succession
     * Corporate/Commercial: Companies Act, SEBI, contracts, mergers
     * Consumer law: Consumer Protection Act
     * Tax law: income tax, GST disputes
     * Environmental law, land acquisition, administrative law
   - If the question has ANY connection to law, rights, legal procedures, or legal concepts → ANSWER IT FULLY
   - ONLY reject if the question is completely unrelated to law: e.g., weather, cooking recipes, sports scores, jokes, pure math
   - When in doubt, ANSWER as a legal question — do not reject borderline queries
   - If truly non-legal, respond: "I can only answer questions related to law and legal matters. Please ask a legal question."

2. **Information Source:**
   - If question relates to the retrieved context: Provide DETAILED analysis using that context
   - If question is general legal (e.g., "What is Section 420?"): Use your comprehensive knowledge of Indian law

3. **CRITICAL - IPC to BNS Mapping:**
   - ALWAYS mention BOTH IPC and corresponding BNS sections
   - Format: "Section 420 IPC (now Section 318 BNS)"
   - Common mappings:
     * IPC 302 → BNS 103 (Murder)
     * IPC 304 → BNS 105 (Culpable homicide)
     * IPC 307 → BNS 109 (Attempt to murder)
     * IPC 376 → BNS 63-70 (Rape/Sexual offenses)
     * IPC 420 → BNS 318 (Cheating)
     * IPC 498A → BNS 84-85 (Cruelty by husband)
   - If you don't know exact BNS mapping, mention: "(BNS equivalent: [approximate section])"

4. **Similar Case Laws (CRITICAL - SEPARATE SECTION):**
   - When user describes a case/incident, suggest 2-3 similar landmark Indian cases
   - IMPORTANT: Put similar cases in a SEPARATE section at the END with marker: "---SIMILAR_CASES---"
   - Format:
   
   ---SIMILAR_CASES---
   • **Case Name v. State (Year)** - [Court]
     Facts: [Brief description]
     Relevance: [Why it's similar]
     Sections: [IPC/BNS sections involved]

5. **Formatting Rules (CRITICAL):**
   - Use 🔹 for main section headings (ONLY ONCE per heading)
   - Add TWO newlines (\n\n) after each section heading
   - Add ONE newline (\n) between paragraphs within a section
   - Use bullet points with • for lists
   - Use **bold** for section numbers, legal terms, and important phrases
   - Add proper spacing between different sections

6. **Content Requirements:**
   - Be COMPREHENSIVE and THOROUGH
   - Include ALL relevant legal sections with BOTH IPC and BNS numbers
   - Explain the COMPLETE legal framework
   - Provide SPECIFIC examples and scenarios
   - Include procedural details (how to file, timelines, jurisdiction)
   - Mention related laws and cross-references
   - Explain legal consequences in detail (imprisonment, fines, bail)
   - Include similar case laws when discussing incidents/cases (ONLY ONCE)

REMEMBER: 
- REJECT non-legal questions immediately
- Use proper spacing (\n\n after headings, \n between paragraphs)
- Keep formatting clean and readable
- Provide DETAILED, COMPREHENSIVE answers
- ALWAYS show IPC and BNS sections together
- Suggest similar cases ONLY ONCE

Answer:""",
                input_variables=["context", "history", "question"]
            )

        response_msg = (prompt | self.llm).invoke({
            "context": context,
            "history": history_text,
            "question": english_query
        })

        response_text = response_msg.content.strip()
        
        # Separate main content from similar cases
        main_content = response_text
        similar_cases = None
        
        if "---SIMILAR_CASES---" in response_text:
            parts = response_text.split("---SIMILAR_CASES---")
            main_content = parts[0].strip()
            similar_cases = parts[1].strip() if len(parts) > 1 else None

        # Translate response back to user's language
        if user_language != "en":
            print(f"[TRANSLATION] Translating AI response from English to {user_language}")
            print(f"[TRANSLATION] English response (first 200 chars): {main_content[:200]}")
            main_content = translation_service.process_response(
                main_content,
                user_language
            )
            if similar_cases:
                similar_cases = translation_service.process_response(
                    similar_cases,
                    user_language
                )
            print(f"[TRANSLATION] Translated response (first 200 chars): {main_content[:200]}")

        return {
            "type": "text",
            "response": main_content,
            "similar_cases": similar_cases,
            "language": user_language,
            "retrieved_chunks": len(context.split("\n\n")) if context else 0
        }

    async def analyze_document(self, session_id: str, document_ids: List[str] = None) -> Dict[str, Any]:
        """
        Perform structured legal analysis on uploaded document(s)

        Args:
            session_id: Session ID
            document_ids: List of document IDs to analyze (None = all)

        Returns:
            Structured legal analysis
        """
        # Get document summary from FAISS
        results = faiss_store.query(
            session_id=session_id,
            query_text="legal sections, case details, charges, offense",
            top_k=10,
            document_ids=document_ids
        )

        if not results:
            return {"error": "No content found in document(s)"}

        # Combine context
        context = "\n\n".join([r["text"] for r in results])

        # Use legal predictor
        analysis = legal_predictor.predict_sections(context, context)

        return analysis


# Global instance
chat_service = ChatService()
