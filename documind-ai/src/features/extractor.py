"""
Extractor Module
Extract specific information from documents (names, dates, numbers, etc.)
"""

from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


class Extractor:
    """
    Extract structured information from documents using AI
    
    Extracts:
    - Names (people, organizations)
    - Dates and deadlines
    - Financial numbers
    - Action items
    - Contact information
    - Legal clauses
    - Custom entities
    """
    
    def __init__(self, ai_model=None):
        """
        Initialize extractor
        
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
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all types of information from text
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with all extracted information
        """
        self._ensure_model()
        
        prompt = f"""Extract all key information from the following text.
        Organize into these categories:

1. PEOPLE (names mentioned)
2. ORGANIZATIONS (companies, institutions, agencies)
3. DATES (all dates, deadlines, timeframes)
4. FINANCIAL AMOUNTS (money, values, figures)
5. LOCATIONS (places, addresses)
6. ACTION ITEMS (tasks, responsibilities)
7. CONTACT INFO (emails, phone numbers)
8. KEY TERMS (important concepts, jargon)

For each item, include context about what it relates to.

TEXT:
{text[:12000]}

EXTRACTED INFORMATION:"""
        
        response = self.ai_model.generate(prompt, max_tokens=1000)
        
        return {
            'extracted_data': response.text.strip(),
            'type': 'comprehensive',
            'tokens_used': response.usage
        }
    
    def extract_names(self, text: str) -> Dict[str, Any]:
        """
        Extract names of people and organizations
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with names categorized
        """
        self._ensure_model()
        
        prompt = f"""Extract all names from the text below.
        Categorize as:
        - People (full names)
        - Organizations (companies, agencies, institutions)
        - Products/Services

For each name, note the role or context.

TEXT:
{text[:10000]}

NAMES:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        return {
            'names': response.text.strip(),
            'type': 'names',
            'tokens_used': response.usage
        }
    
    def extract_dates(self, text: str) -> Dict[str, Any]:
        """
        Extract all dates and temporal information
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with dates and their context
        """
        self._ensure_model()
        
        prompt = f"""Extract all dates and time-related information.
        Include:
        - Specific dates (e.g., January 15, 2024)
        - Deadlines
        - Time periods (e.g., Q1 2024, fiscal year)
        - Durations (e.g., 30 days, 6 months)

For each date, explain what event or deadline it refers to.

TEXT:
{text[:10000]}

DATES AND TIMELINE:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        return {
            'dates': response.text.strip(),
            'type': 'dates',
            'tokens_used': response.usage
        }
    
    def extract_numbers(self, text: str) -> Dict[str, Any]:
        """
        Extract financial numbers and statistics
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with numerical data
        """
        self._ensure_model()
        
        prompt = f"""Extract all numerical data, especially:
        - Monetary amounts ($, €, £, etc.)
        - Percentages
        - Statistics
        - Measurements
        - Quantities

For each number, specify what it represents.

TEXT:
{text[:10000]}

NUMBERS AND DATA:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        return {
            'numbers': response.text.strip(),
            'type': 'numbers',
            'tokens_used': response.usage
        }
    
    def extract_actions(self, text: str) -> Dict[str, Any]:
        """
        Extract action items and tasks
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with action items
        """
        self._ensure_model()
        
        prompt = f"""Extract all action items, tasks, and responsibilities.
        For each action, identify:
        - What needs to be done
        - Who is responsible (if specified)
        - Deadline or timeframe (if specified)
        - Priority level (if indicated)

Format as a clear list.

TEXT:
{text[:10000]}

ACTION ITEMS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        return {
            'actions': response.text.strip(),
            'type': 'actions',
            'tokens_used': response.usage
        }
    
    def extract_contacts(self, text: str) -> Dict[str, Any]:
        """
        Extract contact information
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with contact details
        """
        self._ensure_model()
        
        # Also use regex for direct extraction
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        phones = re.findall(r'\b(?:\+?\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b', text)
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
        
        prompt = f"""Extract all contact information including:
        - Email addresses
        - Phone numbers
        - Physical addresses
        - Website URLs
        - Social media handles

Also verify and add to these found by pattern matching:
Emails: {emails}
Phones: {phones}
URLs: {urls}

CONTACT INFORMATION:"""
        
        response = self.ai_model.generate(prompt, max_tokens=400)
        
        return {
            'contacts': response.text.strip(),
            'emails': list(set(emails)),
            'phones': list(set(phones)),
            'urls': list(set(urls)),
            'type': 'contacts',
            'tokens_used': response.usage
        }
    
    def extract_clauses(self, text: str, clause_type: str = "all") -> Dict[str, Any]:
        """
        Extract legal or contractual clauses
        
        Args:
            text: Document text
            clause_type: Type of clauses to extract ("legal", "financial", "termination", "all")
            
        Returns:
            Dictionary with clauses
        """
        self._ensure_model()
        
        clause_focus = {
            'legal': 'Focus on legal clauses: liability, indemnification, governing law, dispute resolution.',
            'financial': 'Focus on financial clauses: payment terms, penalties, pricing, fees.',
            'termination': 'Focus on termination clauses: conditions, notice periods, consequences.',
            'all': 'Extract all types of important clauses.'
        }
        
        prompt = f"""Extract important clauses from this document.
        {clause_focus.get(clause_type, clause_focus['all'])}

For each clause:
1. Clause type/title
2. Summary of what it says
3. Exact quote from the text
4. Why it's important

TEXT:
{text[:12000]}

CLAUSES:"""
        
        response = self.ai_model.generate(prompt, max_tokens=800)
        
        return {
            'clauses': response.text.strip(),
            'type': clause_type,
            'tokens_used': response.usage
        }
    
    def extract_custom(self, text: str, entity_types: List[str]) -> Dict[str, Any]:
        """
        Extract custom entity types
        
        Args:
            text: Document text
            entity_types: List of entity types to extract
            
        Returns:
            Dictionary with custom extractions
        """
        self._ensure_model()
        
        types_str = ", ".join(entity_types)
        
        prompt = f"""Extract instances of these specific entity types from the text:
        {types_str}

For each entity type, list all occurrences with their context.

TEXT:
{text[:10000]}

EXTRACTED ENTITIES:"""
        
        response = self.ai_model.generate(prompt, max_tokens=800)
        
        return {
            'entities': response.text.strip(),
            'requested_types': entity_types,
            'type': 'custom',
            'tokens_used': response.usage
        }
    
    def extract_key_facts(self, text: str, num_facts: int = 10) -> Dict[str, Any]:
        """
        Extract key factual statements
        
        Args:
            text: Document text
            num_facts: Number of facts to extract
            
        Returns:
            Dictionary with key facts
        """
        self._ensure_model()
        
        prompt = f"""Extract the {num_facts} most important factual statements from this text.
        Focus on verifiable facts, not opinions.
        Present each fact as a clear, standalone statement.

TEXT:
{text[:10000]}

KEY FACTS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        # Parse facts into list
        lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        facts = []
        for line in lines:
            cleaned = line.lstrip('•-*123456789.').strip()
            if cleaned and len(cleaned) > 10:
                facts.append(cleaned)
        
        return {
            'facts': facts,
            'num_facts': len(facts),
            'type': 'key_facts',
            'tokens_used': response.usage
        }
    
    def extract_definitions(self, text: str) -> Dict[str, Any]:
        """
        Extract definitions of terms
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with term definitions
        """
        self._ensure_model()
        
        prompt = f"""Extract all defined terms and their definitions.
        Look for patterns like:
        - "X means..."
        - "X refers to..."
        - "X is defined as..."
        - Terms in quotes with explanations
        - Glossary-style definitions

Format as: Term: Definition

TEXT:
{text[:10000]}

DEFINITIONS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        return {
            'definitions': response.text.strip(),
            'type': 'definitions',
            'tokens_used': response.usage
        }


def extract_info(
    text: str,
    extraction_type: str = "all"
) -> Dict[str, Any]:
    """
    Convenience function to extract information
    
    Args:
        text: Text to extract from
        extraction_type: Type of extraction ("all", "names", "dates", "numbers", "actions", "contacts")
        
    Returns:
        Extraction results
    """
    extractor = Extractor()
    
    if extraction_type == "names":
        return extractor.extract_names(text)
    elif extraction_type == "dates":
        return extractor.extract_dates(text)
    elif extraction_type == "numbers":
        return extractor.extract_numbers(text)
    elif extraction_type == "actions":
        return extractor.extract_actions(text)
    elif extraction_type == "contacts":
        return extractor.extract_contacts(text)
    else:
        return extractor.extract_all(text)
