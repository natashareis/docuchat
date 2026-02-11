"""Tests for service modules."""
import pytest
from pathlib import Path
from io import BytesIO
from app.services.document_processor import DocumentProcessor


def test_is_supported():
    """Test file extension support check."""
    assert DocumentProcessor.is_supported("document.pdf") is True
    assert DocumentProcessor.is_supported("document.txt") is True
    assert DocumentProcessor.is_supported("document.docx") is True
    assert DocumentProcessor.is_supported("document.xyz") is False
    assert DocumentProcessor.is_supported("document.jpg") is False


def test_save_upload(tmp_path, monkeypatch):
    """Test saving uploaded file."""
    monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(tmp_path))
    
    file_content = b"Test content"
    file = BytesIO(file_content)
    
    saved_path = DocumentProcessor.save_upload(file, "test.txt")
    
    assert Path(saved_path).exists()
    with open(saved_path, "rb") as f:
        assert f.read() == file_content


def test_save_upload_duplicate_filename(tmp_path, monkeypatch):
    """Test saving file with duplicate filename."""
    monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(tmp_path))
    
    file1 = BytesIO(b"Content 1")
    file2 = BytesIO(b"Content 2")
    
    path1 = DocumentProcessor.save_upload(file1, "test.txt")
    path2 = DocumentProcessor.save_upload(file2, "test.txt")
    
    assert path1 != path2
    assert Path(path1).exists()
    assert Path(path2).exists()
    assert "test_1.txt" in path2


def test_extract_text_txt(tmp_path):
    """Test extracting text from txt file."""
    test_file = tmp_path / "test.txt"
    test_content = "This is test content.\nMultiple lines."
    test_file.write_text(test_content)
    
    extracted = DocumentProcessor.extract_text(str(test_file))
    assert "test content" in extracted.lower()


def test_extract_text_unsupported_file(tmp_path):
    """Test extracting text from unsupported file raises error."""
    test_file = tmp_path / "test.xyz"
    test_file.write_text("content")
    
    with pytest.raises(ValueError):
        DocumentProcessor.extract_text(str(test_file))


def test_vector_store_initialization():
    """Test vector store service initialization."""
    from app.services.vector_store import VectorStoreService
    
    vector_store = VectorStoreService()
    assert vector_store.client is not None
    assert vector_store.embeddings is not None
    assert vector_store.text_splitter is not None


def test_rag_service_initialization(monkeypatch):
    """Test RAG service initialization."""
    monkeypatch.setattr("app.core.config.settings.GROQ_API_KEY", "test_key")
    
    from app.services.rag_service import RAGService
    
    rag_service = RAGService()
    assert rag_service.llm is not None
    assert rag_service.vector_store_service is not None
