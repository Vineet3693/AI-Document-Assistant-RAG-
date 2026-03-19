"""
OpenAI Model Integration
GPT-4 Turbo and other OpenAI model support.
"""

import os
from typing import List, Dict, Any, Optional, AsyncGenerator
import json

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

from .base_model import BaseModel, ModelResponse


class OpenAIModel(BaseModel):
    """
    OpenAI GPT model integration.
    
    Supports:
    - GPT-4 Turbo
    - GPT-4
    - GPT-3.5 Turbo
    - Streaming responses
    - Token counting with tiktoken
    - Cost tracking
    """
    
    # Pricing per 1K tokens (approximate, update as needed)
    PRICING = {
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    }
    
    def __init__(
        self,
        model_name: str = "gpt-4-turbo-preview",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 60,
        organization: Optional[str] = None
    ):
        """
        Initialize OpenAI model.
        
        Args:
            model_name: OpenAI model ID (e.g., 'gpt-4-turbo-preview')
            api_key: OpenAI API key
            base_url: Custom base URL (for proxies)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            timeout: Request timeout
            organization: OpenAI organization ID
        """
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        
        self.organization = organization
        self._client = None
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )
    
    def _load_api_key_from_env(self) -> Optional[str]:
        """Load API key from environment."""
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def client(self) -> 'OpenAI':
        """Get or create OpenAI client."""
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
                timeout=self.timeout
            )
        return self._client
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using OpenAI API.
        
        Args:
            messages: Chat messages
            **kwargs: Additional parameters (stop, top_p, etc.)
            
        Returns:
            ModelResponse object
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        self._log_request(messages, kwargs)
        
        # Prepare parameters
        params = {
            'model': self.model_name,
            'messages': messages,
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'stream': False,
        }
        
        # Add optional parameters
        if 'stop' in kwargs:
            params['stop'] = kwargs['stop']
        if 'top_p' in kwargs:
            params['top_p'] = kwargs.get('top_p', 1.0)
        if 'frequency_penalty' in kwargs:
            params['frequency_penalty'] = kwargs['frequency_penalty']
        if 'presence_penalty' in kwargs:
            params['presence_penalty'] = kwargs['presence_penalty']
        
        try:
            # Make API call
            response = self.client.chat.completions.create(**params)
            
            # Extract response
            content = response.choices[0].message.content or ""
            usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            model_response = ModelResponse(
                content=content,
                model=response.model or self.model_name,
                usage=usage,
                finish_reason=response.choices[0].finish_reason or "stop",
                metadata={
                    'id': response.id,
                    'created': response.created,
                    'system_fingerprint': getattr(response, 'system_fingerprint', None)
                }
            )
            
            self._log_response(model_response)
            return model_response
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from OpenAI API.
        
        Args:
            messages: Chat messages
            **kwargs: Additional parameters
            
        Yields:
            Text chunks as they arrive
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        # Prepare parameters
        params = {
            'model': self.model_name,
            'messages': messages,
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'stream': True,
        }
        
        try:
            # Make streaming API call
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"OpenAI streaming error: {str(e)}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens using tiktoken.
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        if not TIKTOKEN_AVAILABLE:
            # Fallback: rough estimate
            return len(text) // 4
        
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a request.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        pricing = self.PRICING.get(self.model_name, self.PRICING['gpt-4-turbo'])
        
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available OpenAI models."""
        try:
            models = self.client.models.list()
            return [
                {'id': m.id, 'created': m.created}
                for m in models.data
            ]
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error listing models: {e}")
            return []
    
    def get_model_context_window(self) -> int:
        """Get model's maximum context window."""
        context_windows = {
            'gpt-4-turbo-preview': 128000,
            'gpt-4-turbo': 128000,
            'gpt-4': 8192,
            'gpt-4-32k': 32768,
            'gpt-3.5-turbo': 16385,
            'gpt-3.5-turbo-16k': 16385,
        }
        return context_windows.get(self.model_name, 8192)
