"""
Translator Module
Translate documents and answers to different languages
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Translator:
    """
    Translate text using AI models
    
    Supports 100+ languages via GPT-4/Claude
    """
    
    def __init__(self, ai_model=None):
        self.ai_model = ai_model
        self._model_initialized = False
    
    def _ensure_model(self):
        if not self._model_initialized:
            if not self.ai_model:
                from ..ai_models.openai_model import OpenAIModel
                self.ai_model = OpenAIModel()
            self._model_initialized = True
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Language to translate to
            source_language: Source language (or "auto" for detection)
            
        Returns:
            Translation results
        """
        self._ensure_model()
        
        if source_language == "auto":
            prompt = f"""Translate the following text to {target_language}.
First detect the source language, then translate accurately.
Preserve formatting, technical terms, and proper nouns.

TEXT TO TRANSLATE:
{text[:10000]}

TRANSLATION:"""
        else:
            prompt = f"""Translate the following text from {source_language} to {target_language}.
Preserve formatting, technical terms, and proper nouns.

TEXT TO TRANSLATE:
{text[:10000]}

TRANSLATION:"""
        
        response = self.ai_model.generate(prompt, max_tokens=len(text.split()) * 2)
        
        return {
            'translated_text': response.text.strip(),
            'source_language': source_language,
            'target_language': target_language,
            'original_length': len(text),
            'translated_length': len(response.text),
            'tokens_used': response.usage
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of text"""
        self._ensure_model()
        
        prompt = f"""Identify the language of this text.
Respond with only the language name (e.g., "English", "Spanish", "French").

TEXT:
{text[:1000]}

LANGUAGE:"""
        
        response = self.ai_model.generate(prompt, max_tokens=20)
        
        return {
            'language': response.text.strip(),
            'confidence': 'high',
            'tokens_used': response.usage
        }


def translate_text(text: str, target_lang: str) -> str:
    translator = Translator()
    result = translator.translate(text, target_lang)
    return result['translated_text']
