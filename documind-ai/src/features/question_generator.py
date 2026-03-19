"""
Question Generator Module
Auto-generate questions from documents for quizzes, interviews, study
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generate various types of questions from documents"""
    
    def __init__(self, ai_model=None):
        self.ai_model = ai_model
        self._model_initialized = False
    
    def _ensure_model(self):
        if not self._model_initialized:
            if not self.ai_model:
                from ..ai_models.openai_model import OpenAIModel
                self.ai_model = OpenAIModel()
            self._model_initialized = True
    
    def generate_questions(
        self,
        text: str,
        num_questions: int = 10,
        question_type: str = "general"
    ) -> Dict[str, Any]:
        """Generate questions from text"""
        self._ensure_model()
        
        q_types = {
            'general': 'General comprehension questions',
            'quiz': 'Multiple-choice quiz questions with answers',
            'interview': 'Interview questions to test knowledge',
            'study': 'Study guide questions',
            'critical': 'Critical thinking questions'
        }
        
        prompt = f"""Generate {num_questions} {q_types.get(question_type, '')} from this text.
{"Include 4 multiple choice options (A,B,C,D) and mark the correct answer." if question_type == "quiz" else ""}
{"Focus on assessing candidate knowledge and experience." if question_type == "interview" else ""}
{"Focus on key concepts that should be memorized." if question_type == "study" else ""}
{"Focus on analysis, evaluation, and synthesis." if question_type == "critical" else ""}

TEXT:
{text[:10000]}

QUESTIONS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=800)
        
        return {
            'questions': response.text.strip(),
            'num_questions': num_questions,
            'type': question_type,
            'tokens_used': response.usage
        }
    
    def generate_flashcards(self, text: str) -> Dict[str, Any]:
        """Generate Q&A flashcards"""
        self._ensure_model()
        
        prompt = f"""Create study flashcards from this text.
Format each as:
Q: [Question]
A: [Answer]

Create 15-20 high-quality flashcards covering key concepts.

TEXT:
{text[:8000]}

FLASHCARDS:"""
        
        response = self.ai_model.generate(prompt, max_tokens=1000)
        
        return {
            'flashcards': response.text.strip(),
            'type': 'flashcards',
            'tokens_used': response.usage
        }


def generate_questions(text: str, num: int = 10, q_type: str = "general") -> str:
    gen = QuestionGenerator()
    result = gen.generate_questions(text, num, q_type)
    return result['questions']
