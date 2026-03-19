"""
Text Splitter Module
Splits large documents into manageable chunks for embedding
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata"""
    chunk_id: str
    text: str
    page_number: Optional[int] = None
    document_name: Optional[str] = None
    start_char: int = 0
    end_char: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TextSplitter:
    """
    Split text into chunks for embedding
    
    Strategies:
    - Character-based splitting
    - Sentence-based splitting
    - Paragraph-based splitting
    - Recursive splitting (preferred)
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = "\n\n",
        keep_separator: bool = True,
        add_start_index: bool = False
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        self.keep_separator = keep_separator
        self.add_start_index = add_start_index
        
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks using recursive strategy"""
        if not text or not text.strip():
            return []
            
        # Try splitting by separator first
        chunks = self._split_with_separator(text)
        
        # If chunks are still too large, split further
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                sub_chunks = self._split_large_chunk(chunk)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
                
        return final_chunks
    
    def _split_with_separator(self, text: str) -> List[str]:
        """Split text using the configured separator"""
        if self.keep_separator:
            # Keep separator with the chunk
            parts = text.split(self.separator)
            chunks = []
            for i, part in enumerate(parts):
                if part.strip():
                    if i < len(parts) - 1:
                        chunks.append(part + self.separator)
                    else:
                        chunks.append(part)
            return chunks
        else:
            return [p for p in text.split(self.separator) if p.strip()]
    
    def _split_large_chunk(self, text: str) -> List[str]:
        """Split a chunk that's still too large"""
        chunks = []
        start_idx = 0
        
        while start_idx < len(text):
            end_idx = start_idx + self.chunk_size
            
            if end_idx >= len(text):
                # Remaining text fits in one chunk
                chunks.append(text[start_idx:])
                break
                
            # Try to break at sentence boundary
            break_point = self._find_break_point(text, start_idx, end_idx)
            
            chunk = text[start_idx:break_point]
            if chunk.strip():
                chunks.append(chunk)
                
            start_idx = break_point - self.chunk_overlap
            if start_idx < 0:
                start_idx = 0
                
        return chunks
    
    def _find_break_point(self, text: str, start: int, end: int) -> int:
        """Find the best break point within a range"""
        # Try to break at sentence boundary
        sentence_endings = ['.!', '.?', '!!', '?!', '.', '!', '?']
        
        for ending in sentence_endings:
            idx = text.rfind(ending, start, end)
            if idx != -1:
                return idx + len(ending)
                
        # Try to break at word boundary
        space_idx = text.rfind(' ', start, end)
        if space_idx != -1:
            return space_idx
            
        # No good break point found, split at exact position
        return end
    
    def create_chunks(
        self,
        text: str,
        document_name: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """Create TextChunk objects from text"""
        split_texts = self.split_text(text)
        chunks = []
        
        for i, chunk_text in enumerate(split_texts):
            chunk = TextChunk(
                chunk_id=f"{document_name}_chunk_{i}",
                text=chunk_text.strip(),
                document_name=document_name,
                start_char=sum(len(c.text) for c in chunks),
                end_char=sum(len(c.text) for c in chunks) + len(chunk_text),
                metadata=metadata or {}
            )
            chunks.append(chunk)
            
        return chunks
    
    def split_pages(
        self,
        pages: List[Dict[str, Any]],
        document_name: str = ""
    ) -> List[TextChunk]:
        """Split text from multiple pages, preserving page numbers"""
        all_chunks = []
        
        for page_num, page_data in enumerate(pages, 1):
            text = page_data.get('text', '')
            page_metadata = {
                'page': page_num,
                **page_data.get('metadata', {})
            }
            
            page_chunks = self.create_chunks(
                text=text,
                document_name=document_name,
                metadata=page_metadata
            )
            
            for chunk in page_chunks:
                chunk.page_number = page_num
                
            all_chunks.extend(page_chunks)
            
        return all_chunks


class SentenceSplitter(TextSplitter):
    """Split text by sentences"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator='. '
        )
        
    def _split_with_separator(self, text: str) -> List[str]:
        """Split by sentences"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
                
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return chunks


class ParagraphSplitter(TextSplitter):
    """Split text by paragraphs"""
    
    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 300):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator='\n\n'
        )


def get_splitter(
    splitter_type: str = "recursive",
    **kwargs
) -> TextSplitter:
    """Factory function to get appropriate splitter"""
    if splitter_type == "sentence":
        return SentenceSplitter(**kwargs)
    elif splitter_type == "paragraph":
        return ParagraphSplitter(**kwargs)
    else:
        return TextSplitter(**kwargs)
