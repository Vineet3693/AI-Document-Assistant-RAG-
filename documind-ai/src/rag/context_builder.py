"""
Context Builder Module
Builds clean, optimized context from retrieved chunks for RAG.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class ContextChunk:
    """Represents a processed chunk for context."""
    text: str
    document_id: str
    document_name: str
    score: float
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'document_id': self.document_id,
            'document_name': self.document_name,
            'score': self.score,
            'page': self.page,
            'section': self.section,
            'chunk_id': self.chunk_id
        }


class ContextBuilder:
    """
    Builds optimized context from retrieved chunks for RAG pipeline.
    """
    
    def __init__(
        self,
        max_context_length: int = 8000,
        min_similarity_threshold: float = 0.3,
        max_chunks: int = 10
    ):
        """
        Initialize context builder.
        
        Args:
            max_context_length: Maximum characters in final context
            min_similarity_threshold: Minimum score to include chunk
            max_chunks: Maximum number of chunks to include
        """
        self.max_context_length = max_context_length
        self.min_similarity_threshold = min_similarity_threshold
        self.max_chunks = max_chunks
        self.logger = None
    
    def build_context(
        self,
        retrieved_chunks: List[Dict[str, Any]],
        document_map: Optional[Dict[str, str]] = None
    ) -> Tuple[str, List[ContextChunk]]:
        """
        Build formatted context from retrieved chunks.
        
        Args:
            retrieved_chunks: List of chunk dictionaries from retriever
            document_map: Optional mapping of doc_id to doc_name
            
        Returns:
            Tuple of (formatted_context_string, list_of_processed_chunks)
        """
        if not retrieved_chunks:
            return "", []
        
        # Filter by similarity threshold
        filtered_chunks = [
            chunk for chunk in retrieved_chunks
            if chunk.get('score', 0) >= self.min_similarity_threshold
        ]
        
        # Sort by score (highest first)
        filtered_chunks.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Limit to max chunks
        filtered_chunks = filtered_chunks[:self.max_chunks]
        
        # Process chunks
        processed_chunks = []
        for chunk in filtered_chunks:
            doc_id = chunk.get('document_id', 'unknown')
            doc_name = document_map.get(doc_id, chunk.get('document_name', 'Unknown'))
            
            processed = ContextChunk(
                text=chunk.get('text', ''),
                document_id=doc_id,
                document_name=doc_name,
                score=chunk.get('score', 0),
                page=chunk.get('page') or chunk.get('page_number'),
                section=chunk.get('section') or chunk.get('heading'),
                chunk_id=chunk.get('chunk_id') or chunk.get('id')
            )
            processed_chunks.append(processed)
        
        # Remove duplicates (same text content)
        processed_chunks = self._remove_duplicates(processed_chunks)
        
        # Format context
        context_string = self._format_context(processed_chunks)
        
        # Trim if too long
        if len(context_string) > self.max_context_length:
            context_string = self._trim_context(context_string, processed_chunks)
        
        return context_string, processed_chunks
    
    def _remove_duplicates(
        self,
        chunks: List[ContextChunk]
    ) -> List[ContextChunk]:
        """Remove duplicate chunks based on text content."""
        seen_texts = set()
        unique_chunks = []
        
        for chunk in chunks:
            # Normalize text for comparison
            normalized = self._normalize_text(chunk.text)
            if normalized not in seen_texts:
                seen_texts.add(normalized)
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for duplicate detection."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase
        text = text.lower()
        # Take first 200 chars for comparison
        return text[:200]
    
    def _format_context(self, chunks: List[ContextChunk]) -> str:
        """Format chunks into readable context string."""
        if not chunks:
            return ""
        
        sections = []
        sections.append("=== DOCUMENT CONTEXT ===\n")
        
        for i, chunk in enumerate(chunks, 1):
            # Build location info
            location_parts = []
            if chunk.page:
                location_parts.append(f"Page {chunk.page}")
            if chunk.section:
                location_parts.append(f"Section: {chunk.section}")
            
            location_str = " | ".join(location_parts) if location_parts else "Location unknown"
            
            # Format chunk header
            header = f"[Source {i}: {chunk.document_name} - {location_str}] (Score: {chunk.score:.2f})"
            
            # Add chunk text
            section = f"{header}\n{chunk.text}\n"
            sections.append(section)
        
        sections.append("\n=== END CONTEXT ===")
        
        return "\n".join(sections)
    
    def _trim_context(
        self,
        context: str,
        chunks: List[ContextChunk]
    ) -> str:
        """Trim context to fit within max length."""
        if len(context) <= self.max_context_length:
            return context
        
        # Progressive trimming strategy
        # 1. First, try truncating individual chunks
        target_chunk_length = (self.max_context_length - 500) // len(chunks)
        
        trimmed_chunks = []
        for chunk in chunks:
            if len(chunk.text) > target_chunk_length:
                # Truncate with ellipsis
                trimmed_text = chunk.text[:target_chunk_length - 20] + "...[truncated]"
                trimmed_chunk = ContextChunk(
                    text=trimmed_text,
                    document_id=chunk.document_id,
                    document_name=chunk.document_name,
                    score=chunk.score,
                    page=chunk.page,
                    section=chunk.section,
                    chunk_id=chunk.chunk_id
                )
                trimmed_chunks.append(trimmed_chunk)
            else:
                trimmed_chunks.append(chunk)
        
        # Rebuild context
        context = self._format_context(trimmed_chunks)
        
        # If still too long, hard truncate
        if len(context) > self.max_context_length:
            context = context[:self.max_context_length - 50] + "\n\n...[Context truncated due to length limits]"
        
        return context
    
    def build_multi_document_context(
        self,
        all_chunks: Dict[str, List[Dict[str, Any]]],
        document_map: Dict[str, str]
    ) -> Tuple[str, Dict[str, List[ContextChunk]]]:
        """
        Build context from multiple documents.
        
        Args:
            all_chunks: Dictionary mapping doc_id to list of chunks
            document_map: Mapping of doc_id to doc_name
            
        Returns:
            Tuple of (formatted_context, dict of doc_id to processed chunks)
        """
        all_processed = {}
        combined_chunks = []
        
        for doc_id, chunks in all_chunks.items():
            context_str, processed = self.build_context(chunks, document_map)
            all_processed[doc_id] = processed
            combined_chunks.extend(processed)
        
        # Sort all chunks by score
        combined_chunks.sort(key=lambda x: x.score, reverse=True)
        
        # Build unified context
        if not combined_chunks:
            return "", {}
        
        sections = []
        sections.append("=== MULTI-DOCUMENT CONTEXT ===\n")
        
        for i, chunk in enumerate(combined_chunks, 1):
            location_parts = []
            if chunk.page:
                location_parts.append(f"Page {chunk.page}")
            if chunk.section:
                location_parts.append(f"Section: {chunk.section}")
            
            location_str = " | ".join(location_parts) if location_parts else ""
            header = f"[{chunk.document_name}" + (f" - {location_str}" if location_str else "") + f"] (Score: {chunk.score:.2f})"
            
            section = f"{header}\n{chunk.text}\n"
            sections.append(section)
        
        sections.append("\n=== END MULTI-DOCUMENT CONTEXT ===")
        
        return "\n".join(sections), all_processed
    
    def estimate_tokens(self, context: str) -> int:
        """Estimate token count for context."""
        # Rough estimate: 1 token ≈ 4 characters in English
        return len(context) // 4
    
    def get_context_stats(
        self,
        context: str,
        chunks: List[ContextChunk]
    ) -> Dict[str, Any]:
        """Get statistics about the built context."""
        return {
            'total_characters': len(context),
            'estimated_tokens': self.estimate_tokens(context),
            'num_chunks': len(chunks),
            'num_documents': len(set(c.document_id for c in chunks)),
            'avg_score': sum(c.score for c in chunks) / len(chunks) if chunks else 0,
            'max_score': max(c.score for c in chunks) if chunks else 0,
            'min_score': min(c.score for c in chunks) if chunks else 0,
            'documents': list(set(c.document_name for c in chunks))
        }


# Singleton instance
_context_builder_instance: Optional[ContextBuilder] = None


def get_context_builder(
    max_context_length: int = 8000,
    min_similarity_threshold: float = 0.3,
    max_chunks: int = 10
) -> ContextBuilder:
    """Get singleton context builder instance."""
    global _context_builder_instance
    if _context_builder_instance is None:
        _context_builder_instance = ContextBuilder(
            max_context_length=max_context_length,
            min_similarity_threshold=min_similarity_threshold,
            max_chunks=max_chunks
        )
    return _context_builder_instance
