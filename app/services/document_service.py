import logging
import uuid
import pdfplumber
from typing import List
from app.core.config import settings
from app.storage.database import AsyncSessionLocal
from app.core.exceptions import DocumentProcessingError
from app.storage.document_repository import DocumentRepository
from app.storage.vector_store import vector_store

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self):
        self.vector_store = vector_store
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    async def process_document(self, message, file_path: str, filename: str, user_id: int) -> str:
        try:
            document_id = str(uuid.uuid4())
            
            await message.answer("📖 Reading PDF...")
            text = self._extract_text(file_path)
            if not text:
                raise DocumentProcessingError("Could not extract text from PDF")
            
            await message.answer("✂️ Processing text...")
            chunks = self._chunk_text(text)
            
            async with AsyncSessionLocal() as session:
                await DocumentRepository.create_document(
                    session=session,
                    user_id=user_id,
                    file_name=filename,
                    doc_id=document_id,
                    chunk_count=len(chunks),
                    status="processing"
                )
            
            await message.answer("🧠 Creating embeddings...")
            metadatas = [{"filename": filename, "chunk_idx": i} for i in range(len(chunks))]
            self.vector_store.add_documents(user_id, document_id, chunks, metadatas)
            
            async with AsyncSessionLocal() as session:
                await DocumentRepository.update_document_status(
                    session=session,
                    doc_id=document_id,
                    status="completed",
                    chunk_count=len(chunks)
                )
            
            logger.info(f"Successfully processed document {filename} for user {user_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            raise DocumentProcessingError(f"Failed to process document: {str(e)}")

    def _extract_text(self, file_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n"
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise
        return text

    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        if chunk_size is None:
            chunk_size = self.chunk_size
        if overlap is None:
            overlap = self.chunk_overlap
        
        chunks = []
        step = chunk_size - overlap
        if step <= 0:
            step = chunk_size
        
        for i in range(0, len(text), step):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
            
            if i + chunk_size >= len(text):
                break
        
        return chunks


document_service = DocumentService()
