"""
Citation Tracker Module
Tracks and formats source citations for RAG answers.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Citation:
    """Represents a single citation."""
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    chunk_id: Optional[str] = None
    score: float = 0.0
    quote: str = ""
    confidence: str = "Medium"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary."""
        return {
            'document_id': self.document_id,
            'document_name': self.document_name,
            'page_number': self.page_number,
            'section': self.section,
            'chunk_id': self.chunk_id,
            'score': self.score,
            'quote': self.quote[:200] + '...' if len(self.quote) > 200 else self.quote,
            'confidence': self.confidence
        }
    
    def format_short(self) -> str:
        """Format citation in short form."""
        location = []
        if self.page_number:
            location.append(f"Page {self.page_number}")
        if self.section:
            location.append(f"Section {self.section}")
        
        loc_str = ", ".join(location) if location else "Unknown location"
        return f"📄 {self.document_name} - {loc_str}"
    
    def format_full(self) -> str:
        """Format citation in full detail."""
        lines = [
            f"Document: {self.document_name}",
        ]
        if self.page_number:
            lines.append(f"Page: {self.page_number}")
        if self.section:
            lines.append(f"Section: {self.section}")
        if self.quote:
            quote_display = self.quote[:150] + '...' if len(self.quote) > 150 else self.quote
            lines.append(f"Quote: \"{quote_display}\"")
        lines.append(f"Confidence: {self.confidence}")
        return "\n".join(lines)


@dataclass
class CitationSet:
    """Collection of citations for a single answer."""
    citations: List[Citation] = field(default_factory=list)
    overall_confidence: str = "Medium"
    total_sources: int = 0
    
    def add_citation(self, citation: Citation):
        """Add a citation to the set."""
        self.citations.append(citation)
        self.total_sources = len(self.citations)
        self._update_confidence()
    
    def _update_confidence(self):
        """Update overall confidence based on citations."""
        if not self.citations:
            self.overall_confidence = "Low"
            return
        
        avg_score = sum(c.score for c in self.citations) / len(self.citations)
        
        if avg_score >= 0.8:
            self.overall_confidence = "High"
        elif avg_score >= 0.6:
            self.overall_confidence = "Medium"
        else:
            self.overall_confidence = "Low"
    
    def get_unique_documents(self) -> List[str]:
        """Get list of unique document names."""
        return list(set(c.document_name for c in self.citations))
    
    def format_all(self) -> str:
        """Format all citations for display."""
        if not self.citations:
            return "No sources cited."
        
        lines = ["### 📄 Sources:"]
        for i, citation in enumerate(self.citations, 1):
            lines.append(f"{i}. {citation.format_short()}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert citation set to dictionary."""
        return {
            'citations': [c.to_dict() for c in self.citations],
            'overall_confidence': self.overall_confidence,
            'total_sources': self.total_sources,
            'unique_documents': self.get_unique_documents()
        }


class CitationTracker:
    """
    Tracks and manages citations for RAG answers.
    """
    
    def __init__(self):
        """Initialize citation tracker."""
        self.citation_sets: Dict[str, CitationSet] = {}
        self.logger = None
        
    def create_citation(
        self,
        document_id: str,
        document_name: str,
        chunk_data: Dict[str, Any],
        score: float
    ) -> Citation:
        """
        Create a citation from chunk data.
        
        Args:
            document_id: ID of the source document
            document_name: Name of the source document
            chunk_data: Metadata from the retrieved chunk
            score: Similarity score
            
        Returns:
            Citation object
        """
        # Extract metadata from chunk
        page_number = chunk_data.get('page') or chunk_data.get('page_number')
        section = chunk_data.get('section') or chunk_data.get('heading')
        chunk_id = chunk_data.get('chunk_id') or chunk_data.get('id')
        text = chunk_data.get('text', '')
        
        # Determine confidence based on score
        if score >= 0.8:
            confidence = "High"
        elif score >= 0.6:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return Citation(
            document_id=document_id,
            document_name=document_name,
            page_number=page_number,
            section=section,
            chunk_id=chunk_id,
            score=score,
            quote=text,
            confidence=confidence
        )
    
    def track_answer(
        self,
        answer_id: str,
        retrieved_chunks: List[Dict[str, Any]],
        document_map: Dict[str, str]
    ) -> CitationSet:
        """
        Track citations for an answer.
        
        Args:
            answer_id: Unique ID for the answer
            retrieved_chunks: List of chunks used to generate answer
            document_map: Mapping of document_id to document_name
            
        Returns:
            CitationSet containing all citations
        """
        citation_set = CitationSet()
        
        for chunk_info in retrieved_chunks:
            doc_id = chunk_info.get('document_id', 'unknown')
            doc_name = document_map.get(doc_id, 'Unknown Document')
            score = chunk_info.get('score', 0.0)
            
            citation = self.create_citation(
                document_id=doc_id,
                document_name=doc_name,
                chunk_data=chunk_info,
                score=score
            )
            
            citation_set.add_citation(citation)
        
        self.citation_sets[answer_id] = citation_set
        return citation_set
    
    def get_citation_set(self, answer_id: str) -> Optional[CitationSet]:
        """Get citation set for an answer."""
        return self.citation_sets.get(answer_id)
    
    def format_citations_for_response(
        self,
        citation_set: CitationSet,
        format_type: str = "short"
    ) -> str:
        """
        Format citations for API response.
        
        Args:
            citation_set: Set of citations to format
            format_type: 'short' or 'full'
            
        Returns:
            Formatted citation string
        """
        if format_type == "full":
            return citation_set.format_all()
        
        # Short format
        if not citation_set.citations:
            return "Sources: Not available"
        
        sources = []
        for citation in citation_set.citations[:5]:  # Limit to 5
            sources.append(citation.format_short())
        
        return "Sources: " + "; ".join(sources)
    
    def clear_history(self, older_than: Optional[datetime] = None):
        """Clear old citation history."""
        if older_than is None:
            self.citation_sets.clear()
        else:
            # In production, would filter by timestamp
            pass
    
    def export_citations(
        self,
        answer_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Export citations for reporting.
        
        Args:
            answer_ids: Specific answer IDs to export, or None for all
            
        Returns:
            List of citation dictionaries
        """
        if answer_ids is None:
            answer_ids = list(self.citation_sets.keys())
        
        all_citations = []
        for answer_id in answer_ids:
            citation_set = self.citation_sets.get(answer_id)
            if citation_set:
                citation_data = citation_set.to_dict()
                citation_data['answer_id'] = answer_id
                all_citations.append(citation_data)
        
        return all_citations


# Singleton instance
_citation_tracker_instance: Optional[CitationTracker] = None


def get_citation_tracker() -> CitationTracker:
    """Get singleton citation tracker instance."""
    global _citation_tracker_instance
    if _citation_tracker_instance is None:
        _citation_tracker_instance = CitationTracker()
    return _citation_tracker_instance
