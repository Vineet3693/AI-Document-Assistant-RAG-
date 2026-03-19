"""
Risk Detector Module
Detect risks in documents (legal, financial, compliance)
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class RiskDetector:
    """Detect and analyze risks in documents"""
    
    def __init__(self, ai_model=None):
        self.ai_model = ai_model
        self._model_initialized = False
    
    def _ensure_model(self):
        if not self._model_initialized:
            if not self.ai_model:
                from ..ai_models.openai_model import OpenAIModel
                self.ai_model = OpenAIModel()
            self._model_initialized = True
    
    def detect_risks(
        self,
        text: str,
        risk_type: str = "all"
    ) -> Dict[str, Any]:
        """Detect risks in document"""
        self._ensure_model()
        
        risk_types = {
            'legal': 'Legal and contractual risks',
            'financial': 'Financial risks and concerns',
            'compliance': 'Regulatory compliance issues',
            'operational': 'Operational risks',
            'all': 'All types of risks'
        }
        
        prompt = f"""Analyze this document for {risk_types.get(risk_type, 'all')}.

For each risk found:
1. Risk description
2. Location in document
3. Severity (Critical/High/Medium/Low)
4. Potential impact
5. Recommended mitigation

TEXT:
{text[:12000]}

RISK ANALYSIS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=1000)
        
        # Calculate overall risk score
        severity_map = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        import re
        severities = re.findall(r'(Critical|High|Medium|Low)', response.text, re.IGNORECASE)
        if severities:
            scores = [severity_map.get(s.capitalize(), 2) for s in severities]
            avg_score = sum(scores) / len(scores)
            risk_level = "CRITICAL" if avg_score >= 3.5 else "HIGH" if avg_score >= 2.5 else "MEDIUM" if avg_score >= 1.5 else "LOW"
        else:
            avg_score = 0
            risk_level = "NONE"
        
        return {
            'risks': response.text.strip(),
            'risk_level': risk_level,
            'risk_score': f"{avg_score:.1f}/4",
            'num_risks_found': len(severities),
            'type': risk_type,
            'tokens_used': response.usage
        }
    
    def detect_missing_clauses(self, text: str, document_type: str = "contract") -> Dict[str, Any]:
        """Detect missing important clauses"""
        self._ensure_model()
        
        prompt = f"""This appears to be a {document_type}. 
Identify important standard clauses that are MISSING from this document.

For each missing clause:
1. Clause name
2. Why it's important
3. Risk of not having it

TEXT:
{text[:10000]}

MISSING CLAUSES:"""
        
        response = self.ai_model.generate(prompt, max_tokens=600)
        
        return {
            'missing_clauses': response.text.strip(),
            'document_type': document_type,
            'tokens_used': response.usage
        }


def detect_risks(text: str, risk_type: str = "all") -> Dict[str, Any]:
    detector = RiskDetector()
    return detector.detect_risks(text, risk_type)
