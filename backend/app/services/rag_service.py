from typing import Dict, List
from langchain_groq import ChatGroq
from app.core.config import settings
from app.services.vector_store import VectorStoreService


class RAGService:
    """Service for Retrieval Augmented Generation."""

    def __init__(self):
        """Initialize RAG service."""
        self.vector_store_service = VectorStoreService()
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )

    def answer_question(self, document_id: int, question: str) -> Dict:
        """Answer question based on document content."""
        relevant_chunks = self.vector_store_service.search(
            document_id=document_id,
            query=question,
            n_results=4
        )
        
        if not relevant_chunks:
            return {
                'answer': "I couldn't find relevant information in the document to answer your question.",
                'sources': []
            }
        
        context = "\n\n".join([chunk['content'] for chunk in relevant_chunks])
        
        prompt = f"""You are a helpful assistant answering questions based solely on the provided document context.

Context from the document:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the context provided above
- If the context doesn't contain enough information, say so
- Be concise and accurate
- Do not make up information

Answer:"""

        try:
            response = self.llm.invoke(prompt)
            answer = response.content
        except Exception as e:
            raise ValueError(f"Failed to generate answer: {str(e)}") from e
        
        sources = [chunk['content'][:200] + "..." for chunk in relevant_chunks[:2]]
        
        return {
            'answer': answer,
            'sources': sources
        }
