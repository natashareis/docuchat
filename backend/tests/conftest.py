"""Test configuration and fixtures."""
import pytest
import os
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create engine with StaticPool to share connection
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create scoped session factory
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Session = scoped_session(session_factory)
    
    session = Session()
    
    yield session
    
    session.close()
    Session.remove()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_vector_store(monkeypatch, tmp_path):
    """Mock vector store directory for all tests."""
    monkeypatch.setattr("app.core.config.settings.CHROMA_PERSIST_DIRECTORY", str(tmp_path / "test_vectors"))


@pytest.fixture(autouse=True)
def mock_upload_dir(monkeypatch, tmp_path):
    """Mock upload directory for all tests."""
    upload_dir = tmp_path / "test_uploads"
    upload_dir.mkdir(exist_ok=True)
    monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(upload_dir))
