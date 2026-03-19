"""DocuMind AI - Industry Modes Module"""
from .legal_mode import LegalMode
from .finance_mode import FinanceMode
from .healthcare_mode import HealthcareMode
from .hr_mode import HRMode
from .research_mode import ResearchMode
from .education_mode import EducationMode

__all__ = [
    "LegalMode",
    "FinanceMode",
    "HealthcareMode",
    "HRMode",
    "ResearchMode",
    "EducationMode"
]
