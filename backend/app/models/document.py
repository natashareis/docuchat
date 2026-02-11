from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
import enum
from app.core.database import Base


class DocumentStatus(str, enum.Enum):
    """Document processing status enum."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """Document model."""
    
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADING)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
