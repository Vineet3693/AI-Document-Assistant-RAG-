"""
Summarizer Module
Generate summaries of documents in various formats and lengths
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class Summarizer:
    """
    Generate document summaries using AI
    
    Summary types:
    - One-line summary
    - Executive summary (short paragraph)
    - Detailed summary (full page)
    - Bullet point summary
    - Custom length summary
    """
    
    def __init__(self, ai_model=None):
        """
        Initialize summarizer
        
        Args:
            ai_model: AI model instance to use for summarization
        """
        self.ai_model = ai_model
        self._model_initialized = False
    
    def _ensure_model(self):
        """Ensure AI model is available"""
        if not self._model_initialized:
            if not self.ai_model:
                from ..ai_models.openai_model import OpenAIModel
                self.ai_model = OpenAIModel()
            self._model_initialized = True
    
    def one_line(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a one-sentence summary
        
        Args:
            text: Document text to summarize
            
        Returns:
            Dictionary with summary and metadata
        """
        self._ensure_model()
        
        prompt = f"""Summarize the following text in exactly ONE clear sentence.
        Capture the main point only. Be concise and specific.

TEXT:
{text[:5000]}

ONE SENTENCE SUMMARY:"""
        
        response = self.ai_model.generate(prompt, max_tokens=50)
        
        return {
            'summary': response.text.strip(),
            'type': 'one_line',
            'original_length': len(text),
            'summary_length': len(response.text),
            'compression_ratio': len(text) / max(len(response.text), 1),
            'tokens_used': response.usage
        }
    
    def executive(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Generate an executive summary (~100 words)
        
        Args:
            text: Document text to summarize
            
        Returns:
            Dictionary with summary and metadata
        """
        self._ensure_model()
        
        prompt = f"""Write an executive summary of the following text.
        Keep it to approximately 100 words.
        Focus on:
        - What is this about?
        - Why does it matter?
        - What are the key conclusions?

TEXT:
{text[:8000]}

EXECUTIVE SUMMARY:"""
        
        response = self.ai_model.generate(prompt, max_tokens=150)
        
        return {
            'summary': response.text.strip(),
            'type': 'executive',
            'word_count': len(response.text.split()),
            'original_length': len(text),
            'tokens_used': response.usage
        }
    
    def detailed(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a detailed summary (full page)
        
        Args:
            text: Document text to summarize
            
        Returns:
            Dictionary with summary and metadata
        """
        self._ensure_model()
        
        prompt = f"""Write a comprehensive, detailed summary of the following text.
        Include:
        - Main topic and purpose
        - Key arguments or findings
        - Important data points or evidence
        - Conclusions and implications
        - Any recommendations made

        Organize with clear paragraphs. Aim for 300-500 words.

TEXT:
{text[:15000]}

DETAILED SUMMARY:"""
        
        response = self.ai_model.generate(prompt, max_tokens=800)
        
        return {
            'summary': response.text.strip(),
            'type': 'detailed',
            'word_count': len(response.text.split()),
            'original_length': len(text),
            'tokens_used': response.usage
        }
    
    def bullet_points(self, text: str, num_points: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Generate bullet point summary
        
        Args:
            text: Document text to summarize
            num_points: Number of bullet points to generate
            
        Returns:
            Dictionary with summary and metadata
        """
        self._ensure_model()
        
        prompt = f"""Extract the {num_points} most important points from the following text.
        Present each point as a clear, concise bullet point.
        Each bullet should be 1-2 sentences maximum.

TEXT:
{text[:10000]}

KEY POINTS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=300)
        
        # Parse bullet points
        lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        bullets = []
        for line in lines:
            # Remove bullet markers
            cleaned = line.lstrip('•-*').strip()
            if cleaned:
                bullets.append(cleaned)
        
        return {
            'summary': bullets,
            'type': 'bullet_points',
            'num_points': len(bullets),
            'requested_points': num_points,
            'original_length': len(text),
            'tokens_used': response.usage
        }
    
    def custom(self, text: str, length: str = "medium", **kwargs) -> Dict[str, Any]:
        """
        Generate custom length summary
        
        Args:
            text: Document text to summarize
            length: "short" (~50 words), "medium" (~200 words), "long" (~500 words)
            
        Returns:
            Dictionary with summary and metadata
        """
        self._ensure_model()
        
        length_config = {
            'short': (50, 100),
            'medium': (200, 300),
            'long': (500, 700)
        }
        
        target_min, target_max = length_config.get(length, (200, 300))
        max_tokens = target_max // 4  # Rough estimate
        
        prompt = f"""Write a summary of the following text.
        Target length: {target_min}-{target_max} words.
        Be comprehensive but concise.

TEXT:
{text[:15000]}

SUMMARY:"""
        
        response = self.ai_model.generate(prompt, max_tokens=max_tokens)
        
        return {
            'summary': response.text.strip(),
            'type': 'custom',
            'length': length,
            'word_count': len(response.text.split()),
            'original_length': len(text),
            'tokens_used': response.usage
        }
    
    def with_sections(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Generate structured summary with sections
        
        Returns:
            Dictionary with structured summary
        """
        self._ensure_model()
        
        prompt = f"""Analyze the following text and create a structured summary with these sections:

1. OVERVIEW (2-3 sentences)
2. KEY FINDINGS (bullet points)
3. IMPORTANT DATA (numbers, dates, names)
4. CONCLUSIONS
5. ACTION ITEMS (if any)

TEXT:
{text[:12000]}

STRUCTURED SUMMARY:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        return {
            'summary': response.text.strip(),
            'type': 'structured',
            'original_length': len(text),
            'tokens_used': response.usage
        }
    
    def compare_summaries(
        self,
        text1: str,
        text2: str,
        doc1_name: str = "Document 1",
        doc2_name: str = "Document 2"
    ) -> Dict[str, Any]:
        """
        Generate comparative summary of two documents
        
        Args:
            text1: First document text
            text2: Second document text
            doc1_name: Name of first document
            doc2_name: Name of second document
            
        Returns:
            Dictionary with comparative summary
        """
        self._ensure_model()
        
        prompt = f"""Compare these two documents and provide a comparative summary.

{doc1_name}:
{text1[:6000]}

{doc2_name}:
{text2[:6000]}

Provide:
1. What both documents agree on
2. Key differences between them
3. Unique insights from each document
4. Overall assessment

COMPARATIVE SUMMARY:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        return {
            'summary': response.text.strip(),
            'type': 'comparative',
            'documents': [doc1_name, doc2_name],
            'tokens_used': response.usage
        }


def summarize(
    text: str,
    summary_type: str = "executive",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to summarize text
    
    Args:
        text: Text to summarize
        summary_type: Type of summary ("one_line", "executive", "detailed", "bullet_points", "custom")
        **kwargs: Additional arguments
        
    Returns:
        Summary dictionary
    """
    summarizer = Summarizer()
    
    if summary_type == "one_line":
        return summarizer.one_line(text, **kwargs)
    elif summary_type == "executive":
        return summarizer.executive(text, **kwargs)
    elif summary_type == "detailed":
        return summarizer.detailed(text, **kwargs)
    elif summary_type == "bullet_points":
        return summarizer.bullet_points(text, **kwargs)
    elif summary_type == "custom":
        return summarizer.custom(text, **kwargs)
    else:
        return summarizer.executive(text, **kwargs)
