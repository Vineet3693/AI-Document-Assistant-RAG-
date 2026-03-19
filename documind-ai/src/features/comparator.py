"""
Comparator Module
Compare multiple documents and identify similarities, differences, and conflicts
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class Comparator:
    """
    Compare documents using AI
    
    Features:
    - Side-by-side comparison
    - Similarity detection
    - Difference identification
    - Conflict detection
    - Version comparison
    """
    
    def __init__(self, ai_model=None):
        """
        Initialize comparator
        
        Args:
            ai_model: AI model instance to use
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
    
    def compare_two(
        self,
        text1: str,
        text2: str,
        doc1_name: str = "Document 1",
        doc2_name: str = "Document 2"
    ) -> Dict[str, Any]:
        """
        Compare two documents side by side
        
        Args:
            text1: First document text
            text2: Second document text
            doc1_name: Name of first document
            doc2_name: Name of second document
            
        Returns:
            Comparison results
        """
        self._ensure_model()
        
        prompt = f"""Compare these two documents thoroughly.

{doc1_name}:
{text1[:8000]}

{doc2_name}:
{text2[:8000]}

Provide a detailed comparison with:

1. OVERVIEW
   - Main topic of each document
   - Purpose of each document

2. SIMILARITIES
   - What both documents agree on
   - Common themes and points

3. DIFFERENCES
   - Key differences in content
   - Different perspectives or conclusions

4. CONTRADICTIONS
   - Any direct conflicts between the documents
   - Inconsistent information

5. UNIQUE TO EACH
   - What's only in {doc1_name}
   - What's only in {doc2_name}

6. ANALYSIS
   - Which document is more comprehensive?
   - Any notable omissions?
   - Overall assessment

COMPARISON:"""
        
        response = self.ai_model.generate(prompt, max_tokens=1000)
        
        return {
            'comparison': response.text.strip(),
            'type': 'side_by_side',
            'documents': [doc1_name, doc2_name],
            'tokens_used': response.usage
        }
    
    def find_similarities(
        self,
        text1: str,
        text2: str,
        min_similarity: float = 0.7
    ) -> Dict[str, Any]:
        """
        Find similar content between documents
        
        Args:
            text1: First document text
            text2: Second document text
            min_similarity: Minimum similarity threshold
            
        Returns:
            Dictionary with similar passages
        """
        self._ensure_model()
        
        prompt = f"""Identify all similar content between these two texts.
        Focus on passages that convey the same or very similar information.

TEXT 1:
{text1[:6000]}

TEXT 2:
{text2[:6000]}

List each similarity with:
- Quote from Text 1
- Quote from Text 2
- Brief description of what they have in common

SIMILARITIES:"""
        
        response = self.ai_model.generate(prompt, max_tokens=800)
        
        return {
            'similarities': response.text.strip(),
            'threshold': min_similarity,
            'tokens_used': response.usage
        }
    
    def find_differences(
        self,
        text1: str,
        text2: str,
        difference_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Find differences between documents
        
        Args:
            text1: First document text
            text2: Second document text
            difference_type: "content", "tone", "facts", or "all"
            
        Returns:
            Dictionary with differences
        """
        self._ensure_model()
        
        diff_focus = {
            'content': 'Focus on differences in content and information presented.',
            'tone': 'Focus on differences in tone, style, and presentation.',
            'facts': 'Focus on factual differences and conflicting data.',
            'all': 'Cover all types of differences: content, tone, facts, and perspective.'
        }
        
        prompt = f"""Identify differences between these two texts.
        {diff_focus.get(difference_type, diff_focus['all'])}

TEXT 1:
{text1[:6000]}

TEXT 2:
{text2[:6000]}

For each difference, provide:
- Aspect being compared
- What Text 1 says
- What Text 2 says
- Significance of the difference

DIFFERENCES:"""
        
        response = self.ai_model.generate(prompt, max_tokens=800)
        
        return {
            'differences': response.text.strip(),
            'type': difference_type,
            'tokens_used': response.usage
        }
    
    def find_conflicts(
        self,
        text1: str,
        text2: str
    ) -> Dict[str, Any]:
        """
        Find contradictory information between documents
        
        Args:
            text1: First document text
            text2: Second document text
            
        Returns:
            Dictionary with conflicts identified
        """
        self._ensure_model()
        
        prompt = f"""Find all contradictions and conflicts between these two documents.
        Look for:
        - Conflicting facts or numbers
        - Opposing conclusions
        - Incompatible statements
        - Contradictory recommendations

TEXT 1:
{text1[:6000]}

TEXT 2:
{text2[:6000]}

For each conflict:
1. Describe the conflict
2. Quote from Text 1
3. Quote from Text 2
4. Assess severity (Critical/Major/Minor)

CONFLICTS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=800)
        
        return {
            'conflicts': response.text.strip(),
            'tokens_used': response.usage
        }
    
    def version_diff(
        self,
        old_text: str,
        new_text: str,
        version_old: str = "v1",
        version_new: str = "v2"
    ) -> Dict[str, Any]:
        """
        Compare two versions of the same document
        
        Args:
            old_text: Original document text
            new_text: Updated document text
            version_old: Old version label
            version_new: New version label
            
        Returns:
            Change tracking results
        """
        self._ensure_model()
        
        prompt = f"""Compare these two versions of a document and track all changes.

{version_old}:
{old_text[:8000]}

{version_new}:
{new_text[:8000]}

Identify:

1. ADDED CONTENT
   - New sections, paragraphs, or information
   
2. REMOVED CONTENT
   - What was deleted from the original
   
3. MODIFIED CONTENT
   - Information that was changed or updated
   
4. CLARIFICATIONS
   - Ambiguous text that was clarified
   
5. SUMMARY OF CHANGES
   - Overall nature of revisions
   - Impact of changes

CHANGES:"""
        
        response = self.ai_model.generate(prompt, max_tokens=1000)
        
        return {
            'changes': response.text.strip(),
            'versions': [version_old, version_new],
            'tokens_used': response.usage
        }
    
    def compare_multiple(
        self,
        documents: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Compare multiple documents (3+)
        
        Args:
            documents: List of (text, name) tuples
            
        Returns:
            Multi-document comparison
        """
        self._ensure_model()
        
        # Build prompt with all documents
        prompt_parts = ["Compare these documents and provide a comprehensive analysis.\n"]
        
        for i, (text, name) in enumerate(documents[:5], 1):  # Limit to 5 docs
            prompt_parts.append(f"\nDOCUMENT {i} ({name}):\n{text[:4000]}")
        
        prompt_parts.append("""

ANALYZE:
1. Common themes across ALL documents
2. Unique insights from each document
3. Areas of agreement
4. Areas of disagreement or conflict
5. Overall synthesis

COMPARISON:""")
        
        prompt = "".join(prompt_parts)
        
        response = self.ai_model.generate(prompt, max_tokens=1200)
        
        return {
            'comparison': response.text.strip(),
            'num_documents': len(documents),
            'document_names': [name for _, name in documents],
            'tokens_used': response.usage
        }
    
    def similarity_score(
        self,
        text1: str,
        text2: str
    ) -> Dict[str, Any]:
        """
        Calculate overall similarity score between documents
        
        Args:
            text1: First document text
            text2: Second document text
            
        Returns:
            Similarity score and analysis
        """
        self._ensure_model()
        
        prompt = f"""Analyze the overall similarity between these two texts.
        Rate their similarity on a scale of 0-100%, where:
        - 0% = Completely different topics
        - 50% = Some overlap but mostly different
        - 100% = Nearly identical content

TEXT 1:
{text1[:5000]}

TEXT 2:
{text2[:5000]}

Provide:
1. Similarity percentage (0-100%)
2. Brief justification for the score
3. Main areas of overlap
4. Main areas of divergence

SIMILARITY ANALYSIS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=400)
        
        # Extract percentage from response
        import re
        match = re.search(r'(\d+)%', response.text)
        score = int(match.group(1)) if match else 50
        
        return {
            'similarity_score': score,
            'analysis': response.text.strip(),
            'tokens_used': response.usage
        }


def compare_documents(
    text1: str,
    text2: str,
    doc1_name: str = "Document 1",
    doc2_name: str = "Document 2",
    comparison_type: str = "full"
) -> Dict[str, Any]:
    """
    Convenience function to compare two documents
    
    Args:
        text1: First document text
        text2: Second document text
        doc1_name: Name of first document
        doc2_name: Name of second document
        comparison_type: Type of comparison ("full", "similarities", "differences", "conflicts")
        
    Returns:
        Comparison results
    """
    comparator = Comparator()
    
    if comparison_type == "similarities":
        return comparator.find_similarities(text1, text2)
    elif comparison_type == "differences":
        return comparator.find_differences(text1, text2)
    elif comparison_type == "conflicts":
        return comparator.find_conflicts(text1, text2)
    else:
        return comparator.compare_two(text1, text2, doc1_name, doc2_name)
