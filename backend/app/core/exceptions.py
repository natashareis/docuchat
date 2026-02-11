"""Custom exceptions for the application."""


class DocumentProcessingError(Exception):
    """Raised when document processing fails."""
    pass


class VectorStoreError(Exception):
    """Raised when vector store operations fail."""
    pass


class RAGServiceError(Exception):
    """Raised when RAG service operations fail."""
    pass
