"""
Healthcare Mode - Special handling for medical documents
Includes medical disclaimers, medication extraction, and emergency detection
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class HealthcareMode:
    """Specialized processing for healthcare and medical documents"""
    
    def __init__(self):
        self.medical_disclaimer = """
⚠️ MEDICAL DISCLAIMER:
This analysis is provided for informational purposes only and does not constitute 
medical advice, diagnosis, or treatment. Always seek the advice of qualified health 
providers with any questions regarding medical conditions. Never disregard 
professional medical advice or delay seeking it because of something you have read.

In case of emergency, call your local emergency services immediately.
"""
        
        self.medication_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|tablet|capsule)s?',
            r'(?:take|administer|dose|dosage)[:\s]+(\d+(?:\.\d+)?)\s*(mg|mcg|ml)',
            r'(?:prescribed|medication|drug)[:\s]+([A-Z][a-z]+)',
        ]
        
        self.condition_keywords = [
            'diagnosis', 'condition', 'disease', 'disorder', 'syndrome',
            'infection', 'injury', 'illness', ' ailment', 'complaint'
        ]
        
        self.allergy_indicators = [
            'allergic', 'allergy', 'hypersensitive', 'anaphylaxis',
            'contraindicated', 'adverse reaction', 'intolerance'
        ]
        
        self.emergency_keywords = [
            'emergency', 'urgent', 'critical', 'immediate', 'stat',
            'life-threatening', 'severe', 'acute', 'crisis'
        ]
    
    def extract_medications(self, text: str) -> List[Dict[str, str]]:
        """Extract medications and dosages from medical text"""
        medications = []
        
        for pattern in self.medication_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                med = {
                    'name': groups[0] if len(groups) > 0 else 'Unknown',
                    'dosage': groups[1] if len(groups) > 1 else '',
                    'unit': groups[2] if len(groups) > 2 else '',
                    'context': match.group(0)
                }
                medications.append(med)
        
        return medications[:20]  # Limit to top 20
    
    def extract_conditions(self, text: str) -> List[Dict[str, str]]:
        """Extract medical conditions mentioned"""
        conditions = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for keyword in self.condition_keywords:
                if keyword in sentence_lower:
                    conditions.append({
                        'condition': sentence.strip(),
                        'keyword': keyword,
                        'type': self._classify_condition(sentence)
                    })
                    break
        
        return conditions[:15]
    
    def _classify_condition(self, text: str) -> str:
        """Classify the type of medical condition"""
        text_lower = text.lower()
        
        if 'chronic' in text_lower:
            return 'Chronic'
        elif 'acute' in text_lower:
            return 'Acute'
        elif 'history of' in text_lower or 'prior' in text_lower:
            return 'Historical'
        elif 'current' in text_lower or 'presenting' in text_lower:
            return 'Current'
        else:
            return 'Unspecified'
    
    def detect_allergies(self, text: str) -> List[Dict[str, str]]:
        """Detect allergies and contraindications"""
        allergies = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for indicator in self.allergy_indicators:
                if indicator in sentence_lower:
                    allergies.append({
                        'allergy': sentence.strip(),
                        'indicator': indicator,
                        'severity': self._assess_allergy_severity(sentence)
                    })
                    break
        
        return allergies
    
    def _assess_allergy_severity(self, text: str) -> str:
        """Assess severity of allergy mentioned"""
        text_lower = text.lower()
        
        if 'anaphylaxis' in text_lower or 'severe' in text_lower:
            return 'SEVERE'
        elif 'moderate' in text_lower:
            return 'MODERATE'
        elif 'mild' in text_lower:
            return 'MILD'
        else:
            return 'UNSPECIFIED'
    
    def detect_emergencies(self, text: str) -> List[Dict[str, Any]]:
        """Detect emergency situations requiring immediate attention"""
        emergencies = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for keyword in self.emergency_keywords:
                if keyword in sentence_lower:
                    emergencies.append({
                        'text': sentence.strip(),
                        'keyword': keyword,
                        'urgency': 'CRITICAL' if keyword in ['emergency', 'critical', 'life-threatening'] else 'HIGH',
                        'requires_immediate_action': True
                    })
                    break
        
        return emergencies
    
    def extract_patient_info(self, text: str) -> Dict[str, Any]:
        """Extract patient information (with privacy considerations)"""
        info = {}
        
        # Age patterns
        age_match = re.search(r'\b(\d{1,3})\s*(?:year|yr|y/o|years old)\b', text, re.IGNORECASE)
        if age_match:
            info['age'] = age_match.group(1)
        
        # Gender patterns
        gender_match = re.search(r'\b(male|female|m|f)\b', text, re.IGNORECASE)
        if gender_match:
            info['gender'] = gender_match.group(1).upper()
        
        # Weight patterns
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|lbs|pounds)\b', text, re.IGNORECASE)
        if weight_match:
            info['weight'] = f"{weight_match.group(1)} {weight_match.group(2)}"
        
        return info
    
    def generate_medical_summary(self, text: str, patient_id: str = "") -> Dict[str, Any]:
        """Generate comprehensive medical summary with disclaimer"""
        medications = self.extract_medications(text)
        conditions = self.extract_conditions(text)
        allergies = self.detect_allergies(text)
        emergencies = self.detect_emergencies(text)
        patient_info = self.extract_patient_info(text)
        
        # Check for drug interactions (basic check)
        interactions = self._check_drug_interactions(medications)
        
        return {
            'patient_id': patient_id,
            'patient_info': patient_info,
            'medications': medications,
            'conditions': conditions,
            'allergies': allergies,
            'emergencies': emergencies,
            'drug_interactions': interactions,
            'disclaimer': self.medical_disclaimer,
            'generated_at': datetime.now().isoformat(),
            'requires_clinical_review': len(emergencies) > 0 or len(allergies) > 0
        }
    
    def _check_drug_interactions(self, medications: List[Dict]) -> List[Dict[str, str]]:
        """Basic drug interaction check (placeholder for real integration)"""
        # In production, this would integrate with a drug interaction database
        interactions = []
        
        common_interactions = {
            ('warfarin', 'aspirin'): 'Increased bleeding risk',
            ('lisinopril', 'potassium'): 'Hyperkalemia risk',
            ('metformin', 'contrast dye'): 'Lactic acidosis risk',
        }
        
        med_names = [med.get('name', '').lower() for med in medications]
        
        for (drug1, drug2), interaction in common_interactions.items():
            if drug1 in med_names and drug2 in med_names:
                interactions.append({
                    'drugs': [drug1, drug2],
                    'interaction': interaction,
                    'severity': 'HIGH'
                })
        
        return interactions
    
    def get_prompt_template(self) -> str:
        """Return the medical analysis prompt template"""
        return f"""You are a medical documentation specialist analyzing healthcare records.

IMPORTANT: Always include this disclaimer at the end of your analysis:
{self.medical_disclaimer}

DOCUMENT CONTENT:
{{document_text}}

Generate a comprehensive medical summary including:
1. Patient Information (age, gender if available)
2. Current Medications and Dosages
3. Medical Conditions and Diagnoses
4. Allergies and Contraindications
5. Key Clinical Findings
6. Action Items and Follow-ups

Be precise, maintain patient privacy, and flag any emergency situations immediately."""
