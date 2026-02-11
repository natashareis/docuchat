"""Tests for chat routes."""
import pytest
from app.models.document import Document, DocumentStatus
from app.models.chat import ChatSession


def test_ask_question_document_not_found(client):
    """Test asking question with non-existent document."""
    response = client.post(
        "/api/v1/chat/ask",
        json={
            "document_id": 999,
            "question": "What is this about?"
        }
    )
    assert response.status_code == 404


def test_ask_question_document_not_ready(client, db_session):
    """Test asking question when document is not processed."""
    document = Document(
        filename="test.txt",
        file_path="./uploads/test.txt",
        file_type="text/plain",
        file_size=100,
        status=DocumentStatus.PROCESSING
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    
    response = client.post(
        "/api/v1/chat/ask",
        json={
            "document_id": document.id,
            "question": "What is this about?"
        }
    )
    assert response.status_code == 400
    assert "not ready" in response.json()["detail"].lower()


def test_ask_question_success(client, db_session, monkeypatch):
    """Test successfully asking a question."""
    def mock_answer(*args, **kwargs):
        return {
            'answer': 'This is a test answer.',
            'sources': ['Source 1', 'Source 2']
        }
    
    monkeypatch.setattr("app.services.rag_service.RAGService.answer_question", mock_answer)
    
    document = Document(
        filename="test.txt",
        file_path="./uploads/test.txt",
        file_type="text/plain",
        file_size=100,
        status=DocumentStatus.COMPLETED
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    
    response = client.post(
        "/api/v1/chat/ask",
        json={
            "document_id": document.id,
            "question": "What is this about?"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "session_id" in data
    assert data["answer"] == "This is a test answer."


def test_ask_question_with_existing_session(client, db_session, monkeypatch):
    """Test asking question with existing session."""
    def mock_answer(*args, **kwargs):
        return {
            'answer': 'Another test answer.',
            'sources': []
        }
    
    monkeypatch.setattr("app.services.rag_service.RAGService.answer_question", mock_answer)
    
    document = Document(
        filename="test.txt",
        file_path="./uploads/test.txt",
        file_type="text/plain",
        file_size=100,
        status=DocumentStatus.COMPLETED
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    
    session = ChatSession(document_id=document.id)
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    response = client.post(
        "/api/v1/chat/ask",
        json={
            "document_id": document.id,
            "question": "Follow up question?",
            "session_id": session.id
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session.id


def test_get_chat_history(client, db_session):
    """Test retrieving chat history."""
    from app.models.chat import ChatMessage
    
    document = Document(
        filename="test.txt",
        file_path="./uploads/test.txt",
        file_type="text/plain",
        file_size=100,
        status=DocumentStatus.COMPLETED
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    
    session = ChatSession(document_id=document.id)
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    msg1 = ChatMessage(session_id=session.id, role="user", content="Question 1")
    msg2 = ChatMessage(session_id=session.id, role="assistant", content="Answer 1")
    db_session.add_all([msg1, msg2])
    db_session.commit()
    
    response = client.get(f"/api/v1/chat/history/{session.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session.id
    assert len(data["messages"]) == 2


def test_get_chat_history_not_found(client):
    """Test getting history of non-existent session."""
    response = client.get("/api/v1/chat/history/999")
    assert response.status_code == 404
