from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document


class DocumentRepository:
    @staticmethod
    async def create_document(
        session: AsyncSession,
        user_id: int,
        file_name: str,
        doc_id: str,
        chunk_count: int = 0,
        status: str = "processing",
        file_size: int = 0,
    ) -> Document:
        doc = Document(
            doc_id=doc_id,
            user_id=user_id,
            file_name=file_name,
            file_size=file_size,
            status=status,
            chunk_count=chunk_count,
        )
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        return doc

    @staticmethod
    async def update_document_status(
        session: AsyncSession,
        doc_id: str,
        status: str,
        chunk_count: Optional[int] = None,
    ):
        stmt = select(Document).where(Document.doc_id == doc_id)
        result = await session.execute(stmt)
        doc = result.scalar_one_or_none()
        if doc:
            doc.status = status
            if chunk_count is not None:
                doc.chunk_count = chunk_count
            await session.commit()

    @staticmethod
    async def get_document_by_id(
        session: AsyncSession,
        doc_id: str,
    ) -> Optional[Document]:
        stmt = select(Document).where(Document.doc_id == doc_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_documents(
        session: AsyncSession,
        user_id: int,
    ) -> List[Document]:
        stmt = select(Document).where(Document.user_id == user_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_document(
        session: AsyncSession,
        doc_id: str,
        user_id: int,
    ):
        stmt = delete(Document).where(
            (Document.doc_id == doc_id) & (Document.user_id == user_id)
        )
        await session.execute(stmt)
        await session.commit()
