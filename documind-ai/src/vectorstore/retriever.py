"""
DocuMind AI - Retriever
Search and retrieve relevant document chunks.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    """Represents a retrieval result."""
    text: str
    score: float
    source: str
    page: Optional[int] = None
    chunk_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Retriever:
    """Document retrieval engine for RAG."""
    
    def __init__(
        self,
        vector_store=None,
        embedder=None,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize retriever.
        
        Args:
            vector_store: Vector store instance (ChromaDB or Pinecone)
            embedder: Embedding model instance
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        logger.info(f"Initialized Retriever (top_k={top_k}, threshold={similarity_threshold})")
    
    def retrieve(
        self,
        query: str,
        collection_name: str = None,
        filter_metadata: Dict[str, Any] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query string
            collection_name: Target collection
            filter_metadata: Metadata filters
            
        Returns:
            List of retrieval results
        """
        if not self.embedder or not self.vector_store:
            logger.error("Embedder or vector store not configured")
            return []
        
        # Embed the query
        query_embedding = self.embedder.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=self.top_k,
            filter_metadata=filter_metadata,
            collection_name=collection_name
        )
        
        # Convert to RetrievalResult objects
        retrieval_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results.get("documents", []),
            results.get("metadatas", []),
            results.get("distances", [])
        )):
            # Convert distance to similarity (cosine distance = 1 - cosine similarity)
            similarity = 1.0 - distance
            
            if similarity < self.similarity_threshold:
                continue
            
            result = RetrievalResult(
                text=doc,
                score=similarity,
                source=metadata.get("source", "unknown"),
                page=metadata.get("page"),
                chunk_id=results.get("ids", [])[i] if i < len(results.get("ids", [])) else None,
                metadata=metadata
            )
            retrieval_results.append(result)
        
        # Sort by score descending
        retrieval_results.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Retrieved {len(retrieval_results)} results for query")
        return retrieval_results
    
    def retrieve_multi_document(
        self,
        query: str,
        document_ids: List[str],
        per_doc_limit: int = 3
    ) -> List[RetrievalResult]:
        """
        Retrieve from multiple specific documents.
        
        Args:
            query: User query
            document_ids: List of document IDs to search
            per_doc_limit: Max results per document
            
        Returns:
            Combined retrieval results
        """
        all_results = []
        
        for doc_id in document_ids:
            results = self.retrieve(
                query=query,
                collection_name=doc_id,
                filter_metadata={"document_id": doc_id}
            )
            
            # Limit per document
            all_results.extend(results[:per_doc_limit])
        
        # Sort all results by score
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Multi-doc retrieval: {len(all_results)} results from {len(document_ids)} docs")
        return all_results
    
    def retrieve_with_reranking(
        self,
        query: str,
        initial_k: int = 20,
        final_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Retrieve with initial broad search then rerank.
        
        Args:
            query: User query
            initial_k: Initial number of results
            final_k: Final number after reranking
            
        Returns:
            Reranked retrieval results
        """
        # Temporarily increase top_k
        original_top_k = self.top_k
        self.top_k = initial_k
        
        try:
            results = self.retrieve(query)
            
            # Simple reranking based on keyword overlap
            query_terms = set(query.lower().split())
            
            for result in results:
                text_terms = set(result.text.lower().split())
                overlap = len(query_terms & text_terms)
                result.score = result.score * 0.7 + (overlap / len(query_terms)) * 0.3
            
            # Sort by new scores
            results.sort(key=lambda x: x.score, reverse=True)
            
            return results[:final_k]
            
        finally:
            self.top_k = original_top_k
    
    def get_relevant_chunks_as_text(
        self,
        query: str,
        max_tokens: int = 4000
    ) -> str:
        """
        Get retrieved chunks formatted as text context.
        
        Args:
            query: User query
            max_tokens: Maximum tokens in context
            
        Returns:
            Formatted context string
        """
        results = self.retrieve(query)
        
        if not results:
            return "No relevant information found in documents."
        
        context_parts = []
        total_chars = max_tokens * 4  # Rough char estimate
        
        for result in results:
            chunk_text = f"[Source: {result.source}"
            if result.page:
                chunk_text += f", Page: {result.page}"
            chunk_text += f"]\n{result.text}\n"
            
            if len("\n".join(context_parts)) + len(chunk_text) > total_chars:
                break
            
            context_parts.append(chunk_text)
        
        return "\n---\n".join(context_parts)
    
    def __repr__(self):
        return f"Retriever(vector_store={type(self.vector_store).__name__}, top_k={self.top_k})"
