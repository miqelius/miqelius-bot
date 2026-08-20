import enum
from datetime import datetime, timezone
from sqlalchemy import Column, BigInteger, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DocStatus(enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class User(Base):
    __tablename__ = 'users'
    
    telegram_id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    language_code = Column(String(2), default="ka")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id', ondelete="CASCADE"))
    file_name = Column(String, nullable=False)
    status = Column(Enum(DocStatus), default=DocStatus.PROCESSING)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="documents")
