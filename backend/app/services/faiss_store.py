import os
import pickle
from typing import List, Dict, Any
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document


class FAISSVectorStore:
    """
    FAISS-based vector store for local embeddings storage
    Replaces Pinecone for demo/local usage
    """

    def __init__(self, persist_directory: str = "faiss_indexes"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        # Lazy load embeddings to avoid startup issues
        self._embeddings = None

        self.vector_stores = {}  # session_id -> FAISS index

    @property
    def embeddings(self):
        """Lazy load embeddings only when needed"""
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )
        return self._embeddings

    def create_index(self, documents: List[str], metadatas: List[Dict], session_id: str, document_id: str = None):
        """
        Create FAISS index from documents and metadata

        Args:
            documents: List of text chunks
            metadatas: List of metadata dicts for each chunk
            session_id: Unique session identifier
            document_id: Unique document identifier (for multi-doc support)
        """
        # Convert to LangChain Document objects
        docs = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(documents, metadatas)
        ]

        # Create unique key for this document
        index_key = f"{session_id}_{document_id}" if document_id else session_id

        # Create FAISS index
        vector_store = FAISS.from_documents(docs, self.embeddings)

        # Store in memory
        self.vector_stores[index_key] = vector_store

        # Persist to disk
        self._save_index(index_key)

        return vector_store

    def query(
        self,
        session_id: str,
        query_text: str,
        top_k: int = 5,
        filter_dict: Dict = None,
        document_ids: List[str] = None
    ) -> List[Dict]:
        """
        Query FAISS index for similar documents

        Args:
            session_id: Session identifier
            query_text: Query string
            top_k: Number of results to return
            filter_dict: Metadata filter
            document_ids: List of document IDs to search (None = all docs in session)

        Returns:
            List of dicts with 'text' and 'metadata'
        """
        all_results = []
        
        # If document_ids specified, search only those
        if document_ids:
            index_keys = [f"{session_id}_{doc_id}" for doc_id in document_ids]
        else:
            # Search all documents in session
            index_keys = [key for key in self.vector_stores.keys() if key.startswith(f"{session_id}_")]
            # Also try to load from disk
            import os
            for item in os.listdir(self.persist_directory):
                if item.startswith(f"{session_id}_") and os.path.isdir(os.path.join(self.persist_directory, item)):
                    if item not in self.vector_stores:
                        self._load_index(item)
                        if item in self.vector_stores:
                            index_keys.append(item)
        
        # Query each index
        for index_key in index_keys:
            if index_key not in self.vector_stores:
                self._load_index(index_key)
            
            if index_key not in self.vector_stores:
                continue

            vector_store = self.vector_stores[index_key]

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
            for doc, score in results:
                all_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
        
        # Sort by score and return top_k
        all_results.sort(key=lambda x: x["score"])
        return all_results[:top_k]

    def delete_index(self, session_id: str, document_id: str = None):
        """Delete index from memory and disk"""
        if document_id:
            # Delete specific document
            index_key = f"{session_id}_{document_id}"
            if index_key in self.vector_stores:
                del self.vector_stores[index_key]
            
            # Delete from disk
            index_path = os.path.join(self.persist_directory, index_key)
            if os.path.exists(index_path):
                import shutil
                shutil.rmtree(index_path)
        else:
            # Delete all documents in session
            keys_to_delete = [key for key in self.vector_stores.keys() if key.startswith(f"{session_id}_")]
            for key in keys_to_delete:
                del self.vector_stores[key]
            
            # Delete from disk
            import shutil
            for item in os.listdir(self.persist_directory):
                if item.startswith(f"{session_id}_"):
                    item_path = os.path.join(self.persist_directory, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)

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
        test_embedding = self.embeddings.embed_query("test")
        return len(test_embedding)


# Global instance
faiss_store = FAISSVectorStore()
