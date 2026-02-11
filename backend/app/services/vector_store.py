import os
from typing import List, Dict
import lancedb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings


class VectorStoreService:
    """Service for managing vector store operations."""

    def __init__(self):
        """Initialize vector store service."""
        os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        self.db = lancedb.connect(settings.CHROMA_PERSIST_DIRECTORY)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def _get_table_name(self, document_id: int):
        """Get table name for a document."""
        return f"{settings.COLLECTION_NAME}_{document_id}"

    def add_document(self, document_id: int, text: str, metadata: Dict) -> None:
        """Add document to vector store."""
        chunks = self.text_splitter.split_text(text)
        
        if not chunks:
            raise ValueError("No text chunks generated from document")
        
        table_name = self._get_table_name(document_id)
        embeddings_list = self.embeddings.embed_documents(chunks)
        
        data = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
            data.append({
                "id": f"{document_id}_chunk_{i}",
                "text": chunk,
                "vector": embedding,
                "metadata": str(metadata)
            })
        
        self.db.create_table(table_name, data=data, mode="overwrite")

    def search(self, document_id: int, query: str, n_results: int = 4) -> List[Dict]:
        """Search for relevant chunks in document."""
        table_name = self._get_table_name(document_id)
        
        try:
            table = self.db.open_table(table_name)
        except Exception:
            return []
        
        query_embedding = self.embeddings.embed_query(query)
        
        results = table.search(query_embedding).limit(n_results).to_list()
        
        chunks = []
        for result in results:
            chunks.append({
                'content': result.get('text', ''),
                'metadata': result.get('metadata', {}),
                'distance': result.get('_distance', 0)
            })
        
        return chunks

    def delete_document(self, document_id: int) -> None:
        """Delete document from vector store."""
        try:
            table_name = self._get_table_name(document_id)
            self.db.drop_table(table_name)
        except Exception:
            pass
