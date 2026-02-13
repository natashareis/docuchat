from typing import Dict, List
import re
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
    
    def _extract_relevant_sentences(self, text: str, query: str, max_sentences: int = 1) -> str:
        """Extract the most relevant fragment from text based on query."""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        
        if not sentences:
            return text[:100] + "..." if len(text) > 100 else text
        
        # Check if this is a simple entity query (name, date, number, etc.)
        simple_query_patterns = [
            r'\b(who|what|name|when|where|which|how many)\b',
            r'\b(is|are|was|were)\b.*\b(name|called|date|number)\b'
        ]
        is_simple_query = any(re.search(pattern, query.lower()) for pattern in simple_query_patterns)
        
        # Score sentences by keyword overlap
        query_words = set(word.lower() for word in query.split() if len(word) > 2)
        scored_sentences = []
        
        for sentence in sentences:
            sentence_words = set(word.lower() for word in sentence.split())
            overlap = len(query_words & sentence_words)
            if overlap > 0:
                scored_sentences.append((overlap, sentence))
        
        # Sort by relevance
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        if not scored_sentences:
            return sentences[0][:100] + "..." if len(sentences[0]) > 100 else sentences[0]
        
        # Get the most relevant sentence
        best_sentence = scored_sentences[0][1]
        
        # For simple queries, try to extract just the relevant fragment
        if is_simple_query and len(best_sentence) > 120:
            # Find the fragment containing the most query words
            words = best_sentence.split()
            best_fragment = best_sentence
            best_score = 0
            
            # Use sliding window to find best fragment
            for window_size in [10, 15, 20]:
                for i in range(len(words) - window_size + 1):
                    fragment = ' '.join(words[i:i + window_size])
                    fragment_words = set(word.lower() for word in fragment.split())
                    score = len(query_words & fragment_words)
                    if score > best_score:
                        best_score = score
                        best_fragment = fragment
            
            # Add ellipsis if truncated
            if best_fragment != best_sentence:
                return "..." + best_fragment + "..."
        
        # Truncate long sentences
        if len(best_sentence) > 120:
            return best_sentence[:117] + "..."
        
        return best_sentence

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
        
        # Extract relevant excerpts from chunks as sources
        sources = []
        seen_excerpts = set()  # Avoid duplicate sources
        
        for chunk in relevant_chunks[:3]:  # Show up to 3 sources
            relevant_excerpt = self._extract_relevant_sentences(
                chunk['content'], 
                question,
                max_sentences=1
            )
            # Only add if not too similar to existing sources
            if relevant_excerpt and relevant_excerpt not in seen_excerpts:
                sources.append(relevant_excerpt)
                seen_excerpts.add(relevant_excerpt)
                if len(sources) >= 2:  # Limit to 2 unique sources
                    break
        
        return {
            'answer': answer,
            'sources': sources
        }
