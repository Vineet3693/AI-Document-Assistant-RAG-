"""DocuMind AI - Features Module"""
from .summarizer import Summarizer
from .comparator import Comparator
from .extractor import Extractor
from .translator import Translator
from .question_generator import QuestionGenerator
from .risk_detector import RiskDetector

__all__ = [
    "Summarizer",
    "Comparator",
    "Extractor",
    "Translator",
    "QuestionGenerator",
    "RiskDetector"
]
