"""
Education Mode - Study assistant, quiz generation, and learning support
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class EducationMode:
    """Specialized processing for educational materials and study content"""
    
    def __init__(self):
        self.difficulty_levels = {
            'elementary': ['simple', 'basic', 'introduction', 'fundamentals'],
            'intermediate': ['intermediate', 'moderate', 'standard'],
            'advanced': ['advanced', 'complex', 'detailed', 'comprehensive'],
            'expert': ['expert', 'graduate', 'phd', 'research']
        }
        
        self.question_types = [
            'multiple_choice', 'true_false', 'short_answer', 
            'essay', 'fill_blank', 'matching'
        ]
    
    def analyze_learning_material(self, text: str, subject: str = "") -> Dict[str, Any]:
        """Analyze educational content for learning purposes"""
        return {
            'subject': subject or self._detect_subject(text),
            'difficulty': self._assess_difficulty(text),
            'key_concepts': self._extract_key_concepts(text),
            'learning_objectives': self._identify_learning_objectives(text),
            'prerequisites': self._identify_prerequisites(text),
            'summary': self._generate_summary(text),
            'study_notes': self._generate_study_notes(text),
            'flashcards': self._generate_flashcards(text),
            'quiz_questions': self._generate_quiz(text)
        }
    
    def _detect_subject(self, text: str) -> str:
        """Detect the subject area of the material"""
        subject_keywords = {
            'Mathematics': ['equation', 'formula', 'theorem', 'calculate', 'algebra', 'geometry'],
            'Physics': ['force', 'energy', 'momentum', 'velocity', 'acceleration', 'quantum'],
            'Chemistry': ['molecule', 'atom', 'reaction', 'compound', 'element', 'bond'],
            'Biology': ['cell', 'organism', 'gene', 'protein', 'evolution', 'species'],
            'History': ['century', 'war', 'empire', 'revolution', 'dynasty', 'treaty'],
            'Literature': ['novel', 'poem', 'character', 'plot', 'theme', 'metaphor'],
            'Computer Science': ['algorithm', 'programming', 'data structure', 'software', 'code'],
            'Economics': ['market', 'supply', 'demand', 'price', 'economy', 'trade'],
        }
        
        text_lower = text.lower()
        scores = {}
        
        for subject, keywords in subject_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[subject] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return "General"
    
    def _assess_difficulty(self, text: str) -> str:
        """Assess the difficulty level of the material"""
        text_lower = text.lower()
        
        for level, indicators in self.difficulty_levels.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return level.title()
        
        # Fallback: assess by vocabulary complexity
        words = text.split()
        long_words = [w for w in words if len(w) > 10]
        ratio = len(long_words) / len(words) if words else 0
        
        if ratio > 0.15:
            return "Advanced"
        elif ratio > 0.08:
            return "Intermediate"
        else:
            return "Elementary"
    
    def _extract_key_concepts(self, text: str) -> List[Dict[str, str]]:
        """Extract key concepts from the material"""
        concepts = []
        
        # Look for defined terms (often in bold or quotes)
        patterns = [
            r'\*\*([^*]+)\*\*\s*(?:is|are|refers to|means)[:\s]+(.+?)(?:\.|\n)',
            r'"([^"]+)"\s*(?:is|are|refers to|means)[:\s]+(.+?)(?:\.|\n)',
            r'(?:term|concept|definition)[:\s]+([^.\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                concepts.append({
                    'term': match.group(1).strip(),
                    'definition': match.group(2).strip() if match.lastindex >= 2 else '',
                    'importance': 'high'
                })
        
        # Also extract capitalized terms that might be concepts
        cap_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        for term in cap_terms[:5]:
            if not any(c['term'] == term for c in concepts):
                concepts.append({
                    'term': term,
                    'definition': 'Context needed',
                    'importance': 'medium'
                })
        
        return concepts[:10]
    
    def _identify_learning_objectives(self, text: str) -> List[str]:
        """Identify learning objectives from the material"""
        objectives = []
        
        patterns = [
            r'(?:learning objective|student will|you will learn|by the end)[:\s]+(.+?)(?:\.|\n)',
            r'(?:understand|learn|master|explore)\s+(?:how to|what|why|the)\s+([^.\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                obj = match.group(1).strip() if match.lastindex >= 1 else match.group(0)
                if len(obj) > 10 and len(obj) < 200:
                    objectives.append(obj)
        
        return objectives[:5]
    
    def _identify_prerequisites(self, text: str) -> List[str]:
        """Identify prerequisite knowledge"""
        prerequisites = []
        
        patterns = [
            r'(?:prerequisite|prior knowledge|before starting|you should know)[:\s]+(.+?)(?:\.|\n)',
            r'(?:familiar with|understanding of|knowledge of)\s+([^.\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                prereq = match.group(1).strip() if match.lastindex >= 1 else match.group(0)
                if len(prereq) > 5 and len(prereq) < 150:
                    prerequisites.append(prereq)
        
        return prerequisites[:3]
    
    def _generate_summary(self, text: str) -> str:
        """Generate a concise summary for students"""
        # Extract first paragraph or section
        paragraphs = text.split('\n\n')
        
        if paragraphs:
            # Take first substantial paragraph
            for para in paragraphs:
                para = para.strip()
                if len(para) > 50 and len(para) < 500:
                    return para[:300] + "..." if len(para) > 300 else para
        
        # Fallback: first 200 characters
        return text[:200] + "..." if len(text) > 200 else text
    
    def _generate_study_notes(self, text: str) -> List[Dict[str, str]]:
        """Generate structured study notes"""
        notes = []
        
        # Split into sections
        sections = re.split(r'\n(?=[A-Z][^.\n]{5,50}\n)', text)
        
        for i, section in enumerate(sections[:6]):
            lines = section.strip().split('\n')
            if lines:
                heading = lines[0].strip()
                content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
                
                notes.append({
                    'heading': heading,
                    'content': content[:200] + "..." if len(content) > 200 else content,
                    'order': i
                })
        
        return notes
    
    def _generate_flashcards(self, text: str) -> List[Dict[str, str]]:
        """Generate flashcards for memorization"""
        flashcards = []
        
        # Create flashcards from key concepts
        concepts = self._extract_key_concepts(text)
        
        for concept in concepts[:8]:
            flashcards.append({
                'front': f"What is {concept['term']}?",
                'back': concept['definition'],
                'difficulty': concept['importance']
            })
        
        # Generate additional Q&A pairs
        sentences = text.split('.')
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if len(sentence) > 30 and 'is' in sentence.lower():
                # Convert statement to question
                parts = sentence.split(' is ', 1)
                if len(parts) == 2:
                    flashcards.append({
                        'front': f"What is {parts[0].strip()}?",
                        'back': parts[1].strip() + '.',
                        'difficulty': 'medium'
                    })
        
        return flashcards[:10]
    
    def _generate_quiz(self, text: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions from the material"""
        questions = []
        
        # Extract important sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        
        for i, sentence in enumerate(sentences[:num_questions * 2]):
            if len(questions) >= num_questions:
                break
            
            words = sentence.split()
            
            # Create fill-in-the-blank question
            if len(words) > 5:
                # Remove a key word (long word)
                long_words = [(j, w) for j, w in enumerate(words) if len(w) > 5]
                if long_words:
                    idx, removed = long_words[0]
                    blank_sentence = ' '.join(words[:idx]) + ' _____ ' + ' '.join(words[idx+1:])
                    
                    questions.append({
                        'type': 'fill_blank',
                        'question': f"Fill in the blank: {blank_sentence}",
                        'answer': removed.replace('.', '').replace(',', ''),
                        'points': 1
                    })
        
        # Add multiple choice if we have concepts
        concepts = self._extract_key_concepts(text)
        for concept in concepts[:3]:
            if len(questions) < num_questions:
                # Generate wrong answers from other concepts
                wrong_answers = [c['term'] for c in concepts if c['term'] != concept['term']][:3]
                
                questions.append({
                    'type': 'multiple_choice',
                    'question': f"What is {concept['term']}?",
                    'options': [concept['definition'][:50]] + wrong_answers,
                    'correct_answer': 0,
                    'points': 2
                })
        
        return questions[:num_questions]
    
    def simplify_explanation(self, text: str, target_level: str = 'elementary') -> str:
        """Simplify complex explanation for given level"""
        simplified = text
        
        # Replace complex words with simpler alternatives
        replacements = {
            'utilize': 'use',
            'demonstrate': 'show',
            'indicate': 'show',
            'subsequently': 'then',
            'approximately': 'about',
            'methodology': 'method',
            'facilitate': 'help',
            'comprehensive': 'complete',
            'significant': 'important',
            'therefore': 'so',
            'however': 'but',
            'nevertheless': 'still',
            'furthermore': 'also',
            'consequently': 'so',
        }
        
        for complex_word, simple_word in replacements.items():
            simplified = simplified.replace(complex_word, simple_word)
        
        # Break long sentences
        sentences = simplified.split('.')
        short_sentences = []
        
        for sentence in sentences:
            if len(sentence) > 100:
                # Try to split at conjunctions
                for conj in [' and ', ' but ', ' which ', ' that ']:
                    if conj in sentence:
                        parts = sentence.split(conj, 1)
                        short_sentences.append(parts[0] + '.')
                        short_sentences.append(parts[1][0].upper() + parts[1][1:] + '.')
                        break
                else:
                    short_sentences.append(sentence + '.')
            else:
                short_sentences.append(sentence + '.')
        
        return ' '.join(short_sentences)
    
    def create_study_plan(self, text: str, available_days: int = 7) -> List[Dict[str, Any]]:
        """Create a study plan based on the material"""
        concepts = self._extract_key_concepts(text)
        total_concepts = len(concepts)
        
        concepts_per_day = max(1, total_concepts // available_days)
        
        plan = []
        for day in range(1, available_days + 1):
            start_idx = (day - 1) * concepts_per_day
            end_idx = min(start_idx + concepts_per_day, total_concepts)
            
            day_concepts = concepts[start_idx:end_idx]
            
            plan.append({
                'day': day,
                'topics': [c['term'] for c in day_concepts],
                'activities': [
                    f"Read about: {', '.join([c['term'] for c in day_concepts[:3]])}",
                    "Create flashcards",
                    "Practice with quiz questions",
                    "Review previous day's material"
                ],
                'estimated_time': f"{len(day_concepts) * 15} minutes"
            })
        
        # Add review days
        plan.append({
            'day': available_days + 1,
            'topics': ['All concepts'],
            'activities': [
                "Comprehensive review",
                "Take practice test",
                "Review weak areas"
            ],
            'estimated_time': '60 minutes'
        })
        
        return plan
    
    def get_prompt_template(self) -> str:
        """Return the education mode prompt template"""
        return """You are an expert educator and learning assistant.

SUBJECT: {subject}
LEVEL: {difficulty}

DOCUMENT CONTENT:
{document_text}

Help students learn by providing:
1. Key Concepts (with clear definitions)
2. Learning Objectives (what students should understand)
3. Simplified Summary (appropriate for the level)
4. Study Notes (organized by topic)
5. Flashcards (for memorization)
6. Quiz Questions (multiple choice and fill-in-blank)
7. Study Plan (day-by-day schedule)

Make explanations clear, engaging, and appropriate for the student's level. Use examples when helpful."""
