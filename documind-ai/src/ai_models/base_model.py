"""
Base Model Module
Abstract base class for all AI model integrations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ModelResponse:
    """Standardized response from any AI model."""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=lambda: {
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'total_tokens': 0
    })
    finish_reason: str = "stop"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'content': self.content,
            'model': self.model,
            'usage': self.usage,
            'finish_reason': self.finish_reason,
            'metadata': self.metadata
        }


class BaseModel(ABC):
    """
    Abstract base class for all AI model providers.
    
    All model implementations (OpenAI, Claude, etc.) must inherit from this.
    """
    
    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 60
    ):
        """
        Initialize base model.
        
        Args:
            model_name: Name/ID of the model to use
            api_key: API key for the service
            base_url: Custom base URL for API
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.logger = None
        
        # Validate API key
        if not self.api_key:
            self.api_key = self._load_api_key_from_env()
    
    @abstractmethod
    def _load_api_key_from_env(self) -> Optional[str]:
        """Load API key from environment variables."""
        pass
    
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ModelResponse:
        """
        Generate a complete response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional model-specific parameters
            
        Returns:
            ModelResponse object
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream response chunks.
        
        Args:
            messages: List of message dicts
            **kwargs: Additional parameters
            
        Yields:
            Response text chunks
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        pass
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count total tokens in a message list."""
        total = 0
        for msg in messages:
            content = msg.get('content', '')
            role = msg.get('role', '')
            # Rough estimate: role adds ~4 tokens
            total += self.count_tokens(content) + 4
        return total
    
    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """Validate message format."""
        if not messages:
            return False
        
        for msg in messages:
            if not isinstance(msg, dict):
                return False
            if 'role' not in msg or 'content' not in msg:
                return False
            if msg['role'] not in ['system', 'user', 'assistant']:
                return False
        
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'model_name': self.model_name,
            'provider': self.__class__.__name__,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout
        }
    
    def _log_request(self, messages: List[Dict[str, str]], kwargs: Dict[str, Any]):
        """Log API request for debugging."""
        if self.logger:
            token_count = self.count_messages_tokens(messages)
            self.logger.info(
                f"Model: {self.model_name}, "
                f"Messages: {len(messages)}, "
                f"Tokens: ~{token_count}"
            )
    
    def _log_response(self, response: ModelResponse):
        """Log API response for debugging."""
        if self.logger:
            self.logger.info(
                f"Model: {self.model_name}, "
                f"Tokens: {response.usage.get('total_tokens', 0)}, "
                f"Finish: {response.finish_reason}"
            )
