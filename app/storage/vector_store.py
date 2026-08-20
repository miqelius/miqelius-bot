import chromadb
from typing import List, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY
        )
        self.embedding_model = settings.EMBEDDING_MODEL

    def _get_collection(self, user_id: int):
        collection_name = f"user_{user_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        user_id: int,
        document_id: str,
        chunks: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        collection = self._get_collection(user_id)
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]

        collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )
        logger.info(f"Added {len(chunks)} chunks to vector store for user {user_id}")

    def search_chunks(
        self,
        user_id: int,
        query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        collection = self._get_collection(user_id)

        try:
            results = collection.query(
                query_texts=[query],
                n_results=top_k
            )

            if not results["documents"] or not results["documents"][0]:
                return []

            chunks = []
            for i, doc in enumerate(results["documents"][0]):
                chunks.append({
                    "text": doc,
                    "distance": results["distances"][0][i] if results.get("distances") else 0,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {}
                })
            return chunks
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []

    def delete_document(self, user_id: int, document_id: str):
        collection = self._get_collection(user_id)
        try:
            all_ids = collection.get()["ids"]
            doc_ids = [cid for cid in all_ids if cid.startswith(f"{document_id}_")]
            if doc_ids:
                collection.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} chunks for document {document_id}")
        except Exception as e:
            logger.error(f"Error deleting document from vector store: {e}")


vector_store = VectorStore()
