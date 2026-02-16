import os
import pickle
from typing import List, Dict, Any
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
from langchain.docstore.document import Document


class FAISSVectorStore:
    """
    FAISS-based vector store with simple embeddings (for testing)
    This version avoids the torch/torchvision conflict
    """

    def __init__(self, persist_directory: str = "faiss_indexes"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        # Use fake embeddings for now (simple, no dependencies)
        self._embeddings = None

        self.vector_stores = {}  # session_id -> FAISS index

    @property
    def embeddings(self):
        """Use simple embeddings to avoid torch conflicts"""
        if self._embeddings is None:
            # Use FakeEmbeddings (random vectors) for testing
            # This works but isn't production-ready
            self._embeddings = FakeEmbeddings(size=768)
        return self._embeddings

    def create_index(self, documents: List[str], metadatas: List[Dict], session_id: str):
        """
        Create FAISS index from documents and metadata
        """
        # Convert to LangChain Document objects
        docs = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(documents, metadatas)
        ]

        # Create FAISS index
        vector_store = FAISS.from_documents(docs, self.embeddings)

        # Store in memory
        self.vector_stores[session_id] = vector_store

        # Persist to disk
        self._save_index(session_id)

        return vector_store

    def query(
        self,
        session_id: str,
        query_text: str,
        top_k: int = 5,
        filter_dict: Dict = None
    ) -> List[Dict]:
        """
        Query FAISS index for similar documents
        """
        if session_id not in self.vector_stores:
            # Try to load from disk
            self._load_index(session_id)

        if session_id not in self.vector_stores:
            return []

        vector_store = self.vector_stores[session_id]

        # Perform similarity search
        if filter_dict:
            results = vector_store.similarity_search_with_score(
                query_text,
                k=top_k,
                filter=filter_dict
            )
        else:
            results = vector_store.similarity_search_with_score(
                query_text,
                k=top_k
            )

        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })

        return formatted_results

    def delete_index(self, session_id: str):
        """Delete index from memory and disk"""
        if session_id in self.vector_stores:
            del self.vector_stores[session_id]

        # Delete from disk
        index_path = os.path.join(self.persist_directory, f"{session_id}.faiss")
        pkl_path = os.path.join(self.persist_directory, f"{session_id}.pkl")

        if os.path.exists(index_path):
            os.remove(index_path)
        if os.path.exists(pkl_path):
            os.remove(pkl_path)

    def _save_index(self, session_id: str):
        """Save FAISS index to disk"""
        if session_id not in self.vector_stores:
            return

        save_path = os.path.join(self.persist_directory, session_id)
        self.vector_stores[session_id].save_local(save_path)

    def _load_index(self, session_id: str):
        """Load FAISS index from disk"""
        load_path = os.path.join(self.persist_directory, session_id)

        if not os.path.exists(f"{load_path}/index.faiss"):
            return

        try:
            vector_store = FAISS.load_local(
                load_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            self.vector_stores[session_id] = vector_store
        except Exception as e:
            print(f"Error loading index {session_id}: {e}")

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return 768  # FakeEmbeddings dimension


# Global instance
faiss_store = FAISSVectorStore()
