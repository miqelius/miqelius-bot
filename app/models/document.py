from typing import Optional
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    doc_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="processing")
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user = relationship("User", back_populates="documents")
