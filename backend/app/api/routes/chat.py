from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.document import Document, DocumentStatus
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse, ChatMessageSchema
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Ask a question about a document."""
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Document is not ready. Current status: {document.status}"
        )
    
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = ChatSession(document_id=request.document_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.question
    )
    db.add(user_message)
    db.commit()
    
    try:
        rag_service = RAGService()
        result = rag_service.answer_question(
            document_id=request.document_id,
            question=request.question
        )
        
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=result['answer']
        )
        db.add(assistant_message)
        db.commit()
        
        return ChatResponse(
            answer=result['answer'],
            session_id=session.id,
            sources=result['sources']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: int, db: Session = Depends(get_db)) -> ChatHistoryResponse:
    """Get chat history for a session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return ChatHistoryResponse(
        session_id=session.id,
        document_id=session.document_id,
        messages=[
            ChatMessageSchema(
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )
