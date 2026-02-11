"""Tests for document routes."""
import pytest
from io import BytesIO
from app.models.document import DocumentStatus


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_document_txt(client, monkeypatch):
    """Test uploading a text document."""
    def mock_process(*args, **kwargs):
        pass
    
    monkeypatch.setattr("app.api.routes.documents._process_document_background", mock_process)
    
    file_content = b"This is a test document content."
    file = BytesIO(file_content)
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", file, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["status"] in [DocumentStatus.UPLOADING, DocumentStatus.PROCESSING]
    assert "id" in data


def test_upload_unsupported_file(client):
    """Test uploading an unsupported file type."""
    file_content = b"fake content"
    file = BytesIO(file_content)
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.xyz", file, "application/xyz")}
    )
    
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"].lower()


def test_get_document_status(client, db_session):
    """Test getting document status."""
    from app.models.document import Document
    
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
    
    response = client.get(f"/api/v1/documents/status/{document.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document.id
    assert data["status"] == DocumentStatus.COMPLETED


def test_get_document_status_not_found(client):
    """Test getting status of non-existent document."""
    response = client.get("/api/v1/documents/status/999")
    assert response.status_code == 404


def test_list_documents(client, db_session):
    """Test listing documents."""
    from app.models.document import Document
    
    doc1 = Document(
        filename="test1.txt",
        file_path="./uploads/test1.txt",
        file_type="text/plain",
        file_size=100,
        status=DocumentStatus.COMPLETED
    )
    doc2 = Document(
        filename="test2.pdf",
        file_path="./uploads/test2.pdf",
        file_type="application/pdf",
        file_size=200,
        status=DocumentStatus.PROCESSING
    )
    db_session.add_all([doc1, doc2])
    db_session.commit()
    
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_delete_document(client, db_session, monkeypatch):
    """Test deleting a document."""
    from app.models.document import Document
    
    def mock_delete(*args):
        pass
    
    monkeypatch.setattr("app.services.vector_store.VectorStoreService.delete_document", mock_delete)
    
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
    
    response = client.delete(f"/api/v1/documents/{document.id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()
    
    check_response = client.get(f"/api/v1/documents/status/{document.id}")
    assert check_response.status_code == 404
