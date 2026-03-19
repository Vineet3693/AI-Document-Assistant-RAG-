"""Legal Mode - Specialized handling for legal documents"""

from typing import Dict, Any

class LegalMode:
    def __init__(self):
        self.mode_name = "legal"
    
    def process_query(self, query: str, context: str) -> str:
        prompt = f"""You are a legal document analysis expert. Analyze this legal document.

CONTEXT:
{context[:8000]}

QUERY: {query}

Provide accurate legal analysis with citations."""
        return prompt
    
    def extract_clauses(self, text: str) -> Dict[str, Any]:
        return {"mode": "legal", "analysis": "Contract clauses extracted"}

class FinanceMode:
    def __init__(self):
        self.mode_name = "finance"
    
    def process_query(self, query: str, context: str) -> str:
        prompt = f"""You are a financial analyst. Analyze this financial document.

CONTEXT:
{context[:8000]}

QUERY: {query}

Provide detailed financial analysis."""
        return prompt

class HealthcareMode:
    def __init__(self):
        self.mode_name = "healthcare"
    
    def process_query(self, query: str, context: str) -> str:
        prompt = f"""You are a medical document specialist. ANALYSIS IS FOR INFORMATION ONLY, NOT MEDICAL ADVICE.

CONTEXT:
{context[:8000]}

QUERY: {query}

Provide analysis with medical disclaimer."""
        return prompt

class HRMode:
    def __init__(self):
        self.mode_name = "hr"
    
    def process_query(self, query: str, context: str) -> str:
        prompt = f"""You are an HR specialist. Analyze this HR document.

CONTEXT:
{context[:8000]}

QUERY: {query}

Provide HR-focused analysis."""
        return prompt

class ResearchMode:
    def __init__(self):
        self.mode_name = "research"
    
    def process_query(self, query: str, context: str) -> str:
        prompt = f"""You are a research analyst. Analyze this academic paper.

CONTEXT:
{context[:8000]}

QUERY: {query}

Provide scholarly analysis."""
        return prompt

class EducationMode:
    def __init__(self):
        self.mode_name = "education"
    
    def process_query(self, query: str, context: str) -> str:
        prompt = f"""You are an educational assistant. Help understand this material.

CONTEXT:
{context[:8000]}

QUERY: {query}

Provide clear educational explanation."""
        return prompt
