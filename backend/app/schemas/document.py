from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.document import DocumentStatus


class DocumentUploadResponse(BaseModel):
    """Document upload response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    uploaded_at: datetime


class DocumentProcessingStatus(BaseModel):
    """Document processing status schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    filename: str
    status: DocumentStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Document list response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    uploaded_at: datetime
