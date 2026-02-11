from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os
from app.api.deps import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentProcessingStatus,
    DocumentListResponse
)
from app.services.document_processor import DocumentProcessor, _SUPPORTED_EXTENSIONS
from app.services.vector_store import VectorStoreService
from app.core.config import settings

router = APIRouter()


def _process_document_background(document_id: int, file_path: str) -> None:
    """Background task to process document."""
    db = next(get_db())
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        
        document.status = DocumentStatus.PROCESSING
        db.commit()
        
        text = DocumentProcessor.extract_text(file_path)
        
        vector_store = VectorStoreService()
        vector_store.add_document(
            document_id=document_id,
            text=text,
            metadata={
                'filename': document.filename,
                'file_type': document.file_type
            }
        )
        
        document.status = DocumentStatus.COMPLETED
        document.processed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> DocumentUploadResponse:
    """Upload and process a document."""
    if not DocumentProcessor.is_supported(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Supported types: {', '.join(_SUPPORTED_EXTENSIONS)}"
        )
    
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    try:
        file_path = DocumentProcessor.save_upload(file.file, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    document = Document(
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=file.size or 0,
        status=DocumentStatus.UPLOADING
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    background_tasks.add_task(
        _process_document_background,
        document.id,
        file_path
    )
    
    return document


@router.get("/status/{document_id}", response_model=DocumentProcessingStatus)
async def get_document_status(document_id: int, db: Session = Depends(get_db)) -> DocumentProcessingStatus:
    """Get document processing status."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/", response_model=List[DocumentListResponse])
async def list_documents(db: Session = Depends(get_db)) -> List[DocumentListResponse]:
    """List all documents."""
    documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return documents


@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete a document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    vector_store = VectorStoreService()
    vector_store.delete_document(document_id)
    
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except OSError:
            pass
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
