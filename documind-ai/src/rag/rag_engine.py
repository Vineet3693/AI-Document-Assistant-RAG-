"""
RAG Engine Module
The core Retrieval-Augmented Generation pipeline controller.
This is the most important file in the project.
"""

from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
import uuid
from datetime import datetime

from .context_builder import ContextBuilder, get_context_builder
from .prompt_builder import PromptBuilder, get_prompt_builder, Message
from .citation_tracker import CitationTracker, get_citation_tracker, CitationSet


class RAGResponse:
    """Represents a complete RAG response."""
    
    def __init__(
        self,
        answer: str,
        citations: CitationSet,
        context_used: str,
        tokens_used: Dict[str, int],
        model: str,
        latency_ms: float,
        confidence: str,
        documents_used: List[str]
    ):
        self.answer = answer
        self.citations = citations
        self.context_used = context_used
        self.tokens_used = tokens_used  # {'input': x, 'output': y, 'total': z}
        self.model = model
        self.latency_ms = latency_ms
        self.confidence = confidence
        self.documents_used = documents_used
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for API."""
        return {
            'id': self.id,
            'answer': self.answer,
            'citations': self.citations.to_dict() if self.citations else None,
            'context_used': self.context_used[:500] + '...' if len(self.context_used) > 500 else self.context_used,
            'tokens_used': self.tokens_used,
            'model': self.model,
            'latency_ms': round(self.latency_ms, 2),
            'confidence': self.confidence,
            'documents_used': self.documents_used,
            'timestamp': self.timestamp.isoformat()
        }


class RAGEngine:
    """
    Main RAG pipeline controller.
    
    Flow:
    1. Receive user question
    2. Call retriever → get relevant chunks
    3. Call context_builder → build context
    4. Call prompt_builder → build full prompt
    5. Call AI model → generate answer
    6. Call citation_tracker → add citations
    7. Return final answer + citations
    """
    
    def __init__(
        self,
        retriever=None,
        ai_model=None,
        context_builder: Optional[ContextBuilder] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        citation_tracker: Optional[CitationTracker] = None
    ):
        """
        Initialize RAG engine.
        
        Args:
            retriever: Vector store retriever instance
            ai_model: AI model instance (OpenAI, Claude, etc.)
            context_builder: Context builder instance
            prompt_builder: Prompt builder instance
            citation_tracker: Citation tracker instance
        """
        self.retriever = retriever
        self.ai_model = ai_model
        self.context_builder = context_builder or get_context_builder()
        self.prompt_builder = prompt_builder or get_prompt_builder()
        self.citation_tracker = citation_tracker or get_citation_tracker()
        self.logger = None
        self.document_map: Dict[str, str] = {}  # doc_id -> doc_name
    
    def set_retriever(self, retriever):
        """Set the retriever instance."""
        self.retriever = retriever
    
    def set_ai_model(self, ai_model):
        """Set the AI model instance."""
        self.ai_model = ai_model
    
    def update_document_map(self, document_map: Dict[str, str]):
        """Update mapping of document IDs to names."""
        self.document_map.update(document_map)
    
    def ask(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
        template_name: Optional[str] = None,
        industry_mode: Optional[str] = None,
        language: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> RAGResponse:
        """
        Ask a question using RAG pipeline.
        
        Args:
            question: User's question
            document_ids: List of document IDs to search (None = all)
            top_k: Number of chunks to retrieve
            template_name: Prompt template to use
            industry_mode: Industry-specific mode
            language: Response language
            chat_history: Previous conversation messages
            **kwargs: Additional parameters
            
        Returns:
            RAGResponse object with answer and citations
        """
        start_time = datetime.utcnow()
        
        if self.logger:
            self.logger.info(f"RAG: Processing question: {question[:100]}")
        
        # Step 1: Retrieve relevant chunks
        if not self.retriever:
            raise ValueError("Retriever not configured")
        
        retrieved_chunks = self.retriever.search(
            query=question,
            document_ids=document_ids,
            top_k=top_k
        )
        
        if self.logger:
            self.logger.info(f"RAG: Retrieved {len(retrieved_chunks)} chunks")
        
        # Step 2: Build context
        context, processed_chunks = self.context_builder.build_context(
            retrieved_chunks=retrieved_chunks,
            document_map=self.document_map
        )
        
        if self.logger:
            self.logger.info(f"RAG: Built context ({len(context)} chars)")
        
        # Step 3: Build prompt
        messages = self.prompt_builder.build_prompt(
            template_name=template_name,
            context=context,
            question=question,
            chat_history=chat_history,
            industry_mode=industry_mode,
            language=language,
            doc_names=", ".join(self.document_map.values()) if self.document_map else "No documents"
        )
        
        # Step 4: Generate answer with AI model
        if not self.ai_model:
            raise ValueError("AI model not configured")
        
        response = self.ai_model.generate(messages)
        
        # Step 5: Track citations
        chunk_data = [chunk.to_dict() if hasattr(chunk, 'to_dict') else chunk for chunk in retrieved_chunks]
        citation_set = self.citation_tracker.track_answer(
            answer_id=str(uuid.uuid4()),
            retrieved_chunks=chunk_data,
            document_map=self.document_map
        )
        
        # Calculate metrics
        end_time = datetime.utcnow()
        latency_ms = (end_time - start_time).total_seconds() * 1000
        
        tokens_used = {
            'input': response.get('usage', {}).get('prompt_tokens', 0),
            'output': response.get('usage', {}).get('completion_tokens', 0),
            'total': response.get('usage', {}).get('total_tokens', 0)
        }
        
        # Create response
        rag_response = RAGResponse(
            answer=response.get('content', ''),
            citations=citation_set,
            context_used=context,
            tokens_used=tokens_used,
            model=response.get('model', 'unknown'),
            latency_ms=latency_ms,
            confidence=citation_set.overall_confidence,
            documents_used=citation_set.get_unique_documents()
        )
        
        if self.logger:
            self.logger.info(f"RAG: Completed in {latency_ms:.2f}ms")
        
        return rag_response
    
    async def ask_stream(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
        template_name: Optional[str] = None,
        industry_mode: Optional[str] = None,
        language: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Ask a question with streaming response.
        
        Args:
            Same as ask()
            
        Yields:
            Chunks of the answer as they are generated
        """
        # Retrieve and build context (same as ask)
        if not self.retriever:
            raise ValueError("Retriever not configured")
        
        retrieved_chunks = self.retriever.search(
            query=question,
            document_ids=document_ids,
            top_k=top_k
        )
        
        context, _ = self.context_builder.build_context(
            retrieved_chunks=retrieved_chunks,
            document_map=self.document_map
        )
        
        # Build prompt
        messages = self.prompt_builder.build_prompt(
            template_name=template_name,
            context=context,
            question=question,
            chat_history=chat_history,
            industry_mode=industry_mode,
            language=language,
            doc_names=", ".join(self.document_map.values()) if self.document_map else "No documents"
        )
        
        # Stream from AI model
        if not self.ai_model:
            raise ValueError("AI model not configured")
        
        async for chunk in self.ai_model.stream(messages):
            yield chunk
    
    def ask_multi_document(
        self,
        question: str,
        document_ids: List[str],
        top_k_per_doc: int = 3,
        **kwargs
    ) -> RAGResponse:
        """
        Ask a question across multiple specific documents.
        
        Args:
            question: User's question
            document_ids: List of document IDs to search
            top_k_per_doc: Chunks to retrieve per document
            **kwargs: Additional parameters
            
        Returns:
            RAGResponse object
        """
        if self.logger:
            self.logger.info(f"Multi-doc RAG: Searching {len(document_ids)} documents")
        
        # Retrieve from each document
        all_chunks = []
        for doc_id in document_ids:
            chunks = self.retriever.search(
                query=question,
                document_ids=[doc_id],
                top_k=top_k_per_doc
            )
            all_chunks.extend(chunks)
        
        # Use standard ask flow with combined chunks
        return self.ask(
            question=question,
            document_ids=document_ids,
            top_k=len(all_chunks),
            template_name='multi_doc_qa',
            **kwargs
        )
    
    def summarize_document(
        self,
        document_id: str,
        summary_type: str = 'executive'
    ) -> Dict[str, Any]:
        """
        Generate a summary of a document.
        
        Args:
            document_id: ID of document to summarize
            summary_type: 'one_line', 'executive', 'detailed', or 'bullet_points'
            
        Returns:
            Summary response dictionary
        """
        if not self.retriever:
            raise ValueError("Retriever not configured")
        
        # Get all chunks for this document
        all_chunks = self.retriever.get_document_chunks(document_id)
        
        if not all_chunks:
            return {'error': 'Document not found or empty'}
        
        # Combine all text
        full_text = "\n\n".join([
            chunk.get('text', '') for chunk in all_chunks
        ])
        
        # Build summary prompt
        doc_name = self.document_map.get(document_id, 'Unknown Document')
        messages = self.prompt_builder.build_prompt(
            template_name='executive_summary',
            document_text=full_text[:15000],  # Limit text
            document_name=doc_name,
            document_type='General',
            industry='General'
        )
        
        # Generate summary
        if not self.ai_model:
            raise ValueError("AI model not configured")
        
        response = self.ai_model.generate(messages)
        
        return {
            'document_id': document_id,
            'document_name': doc_name,
            'summary_type': summary_type,
            'summary': response.get('content', ''),
            'tokens_used': response.get('usage', {})
        }
    
    def compare_documents(
        self,
        document_id_1: str,
        document_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two documents.
        
        Args:
            document_id_1: First document ID
            document_id_2: Second document ID
            
        Returns:
            Comparison response dictionary
        """
        if not self.retriever:
            raise ValueError("Retriever not configured")
        
        # Get chunks for both documents
        chunks_1 = self.retriever.get_document_chunks(document_id_1)
        chunks_2 = self.retriever.get_document_chunks(document_id_2)
        
        if not chunks_1 or not chunks_2:
            return {'error': 'One or both documents not found'}
        
        # Combine texts
        text_1 = "\n\n".join([c.get('text', '') for c in chunks_1])[:10000]
        text_2 = "\n\n".join([c.get('text', '') for c in chunks_2])[:10000]
        
        doc_name_1 = self.document_map.get(document_id_1, 'Document 1')
        doc_name_2 = self.document_map.get(document_id_2, 'Document 2')
        
        # Build comparison prompt
        messages = self.prompt_builder.build_prompt(
            template_name='document_comparison',
            doc1_name=doc_name_1,
            doc1_text=text_1,
            doc2_name=doc_name_2,
            doc2_text=text_2
        )
        
        # Generate comparison
        if not self.ai_model:
            raise ValueError("AI model not configured")
        
        response = self.ai_model.generate(messages)
        
        return {
            'document_1': {'id': document_id_1, 'name': doc_name_1},
            'document_2': {'id': document_id_2, 'name': doc_name_2},
            'comparison': response.get('content', ''),
            'tokens_used': response.get('usage', {})
        }
    
    def clear_cache(self):
        """Clear any cached data."""
        self.citation_tracker.clear_history()
        if self.logger:
            self.logger.info("RAG: Cleared cache")


# Singleton instance
_rag_engine_instance: Optional[RAGEngine] = None


def get_rag_engine(
    retriever=None,
    ai_model=None
) -> RAGEngine:
    """Get singleton RAG engine instance."""
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine(
            retriever=retriever,
            ai_model=ai_model
        )
    else:
        # Update components if provided
        if retriever:
            _rag_engine_instance.set_retriever(retriever)
        if ai_model:
            _rag_engine_instance.set_ai_model(ai_model)
    
    return _rag_engine_instance
