import os
import io
import tempfile
import re
from typing import List, Dict, Tuple
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class DocumentProcessor:
    """
    Process legal documents (PDFs, text files)
    Extract text, chunk intelligently for legal content
    """

    def __init__(self):
        pass

    def process_pdf(self, uploaded_pdf) -> Tuple[List[str], List[Dict]]:
        """
        Extract text from PDF with OCR fallback

        Args:
            uploaded_pdf: Uploaded PDF file object

        Returns:
            Tuple of (texts, metadata)
        """
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
                # Use OCR for scanned documents
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

    def legal_aware_chunking(self, text: str) -> List[str]:
        """
        Intelligent chunking for legal documents
        Preserves section boundaries, case references, etc.

        Args:
            text: Input text

        Returns:
            List of text chunks
        """
        # Patterns for legal content
        SECTION_PATTERN = re.compile(
            r"(Section\s+\d+[A-Z]?|IPC\s+\d+|CrPC\s+\d+|BNS\s+\d+)",
            re.IGNORECASE
        )
        CASE_REFERENCE = re.compile(
            r"(v\.|vs\.|versus|AIR\s+\d+|SCC\s+\d+)",
            re.IGNORECASE
        )

        lines = text.split("\n")
        buffer, chunks = [], []

        for line in lines:
            buffer.append(line)

            # Keep section references together
            if SECTION_PATTERN.search(line) or CASE_REFERENCE.search(line):
                continue

            # Chunk when buffer gets large
            if len(" ".join(buffer)) > 800:
                chunks.append(" ".join(buffer))
                buffer = []

        if buffer:
            chunks.append(" ".join(buffer))

        # Use RecursiveCharacterTextSplitter for final refinement
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        final_chunks = []
        for chunk in chunks:
            if chunk.strip():
                final_chunks.extend(splitter.split_text(chunk))

        return final_chunks

    def chunk_documents(self, text_list: List[str], metadata_list: List[Dict]) -> Tuple[List[str], List[Dict]]:
        """
        Chunk multiple documents with metadata preservation

        Args:
            text_list: List of document texts
            metadata_list: List of metadata dicts

        Returns:
            Tuple of (all_chunks, all_metadata)
        """
        all_chunks, all_meta = [], []

        for text, meta in zip(text_list, metadata_list):
            chunks = self.legal_aware_chunking(text)
            all_chunks.extend(chunks)

            # Add metadata with text content
            for chunk in chunks:
                meta_with_text = meta.copy()
                meta_with_text["text"] = chunk
                all_meta.append(meta_with_text)

        return all_chunks, all_meta

    def extract_key_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract key legal entities from text

        Args:
            text: Input text

        Returns:
            Dict with entity types and values
        """
        entities = {
            "ipc_sections": [],
            "crpc_sections": [],
            "bns_sections": [],
            "case_references": [],
            "dates": []
        }

        # IPC sections
        ipc_matches = re.findall(r"IPC\s+(\d+[A-Z]?)|Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?IPC", text, re.IGNORECASE)
        entities["ipc_sections"] = [m[0] or m[1] for m in ipc_matches if m[0] or m[1]]

        # CrPC sections
        crpc_matches = re.findall(r"CrPC\s+(\d+[A-Z]?)|Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?CrPC", text, re.IGNORECASE)
        entities["crpc_sections"] = [m[0] or m[1] for m in crpc_matches if m[0] or m[1]]

        # BNS sections
        bns_matches = re.findall(r"BNS\s+(\d+[A-Z]?)|Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?BNS", text, re.IGNORECASE)
        entities["bns_sections"] = [m[0] or m[1] for m in bns_matches if m[0] or m[1]]

        # Case references
        case_matches = re.findall(r"(\w+\s+v\.\s+\w+|AIR\s+\d+|SCC\s+\d+)", text, re.IGNORECASE)
        entities["case_references"] = case_matches

        # Dates
        date_matches = re.findall(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}", text)
        entities["dates"] = date_matches

        return entities


# Global instance
document_processor = DocumentProcessor()
