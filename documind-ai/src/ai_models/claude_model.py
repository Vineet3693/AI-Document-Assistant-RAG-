"""
Anthropic Claude Model Integration
Claude 3 and other Anthropic model support.
"""

import os
from typing import List, Dict, Any, Optional, AsyncGenerator

try:
    import anthropic
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base_model import BaseModel, ModelResponse


class ClaudeModel(BaseModel):
    """
    Anthropic Claude model integration.
    
    Supports:
    - Claude 3 Opus
    - Claude 3 Sonnet
    - Claude 3 Haiku
    - Streaming responses
    - Token counting
    - Cost tracking
    """
    
    # Pricing per 1K tokens (approximate, update as needed)
    PRICING = {
        'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
        'claude-2.1': {'input': 0.008, 'output': 0.024},
    }
    
    def __init__(
        self,
        model_name: str = "claude-3-sonnet-20240229",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 60
    ):
        """
        Initialize Claude model.
        
        Args:
            model_name: Anthropic model ID
            api_key: Anthropic API key
            base_url: Custom base URL
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            timeout: Request timeout
        """
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        
        self._client = None
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
    
    def _load_api_key_from_env(self) -> Optional[str]:
        """Load API key from environment."""
        return os.getenv('ANTHROPIC_API_KEY')
    
    @property
    def client(self) -> 'Anthropic':
        """Get or create Anthropic client."""
        if self._client is None:
            self._client = Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self._client
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using Anthropic Messages API.
        
        Args:
            messages: Chat messages (must start with user message)
            **kwargs: Additional parameters
            
        Returns:
            ModelResponse object
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        self._log_request(messages, kwargs)
        
        # Extract system message if present
        system_message = ""
        chat_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                chat_messages.append(msg)
        
        # Ensure first message is from user (Claude requirement)
        if chat_messages and chat_messages[0]['role'] != 'user':
            # Add empty user message if needed
            chat_messages.insert(0, {'role': 'user', 'content': ''})
        
        # Prepare parameters
        params = {
            'model': self.model_name,
            'messages': chat_messages,
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature),
        }
        
        # Add system message
        if system_message:
            params['system'] = system_message
        
        # Add optional parameters
        if 'stop_sequences' in kwargs:
            params['stop_sequences'] = kwargs['stop_sequences']
        if 'top_p' in kwargs:
            params['top_p'] = kwargs.get('top_p', 1.0)
        if 'top_k' in kwargs:
            params['top_k'] = kwargs.get('top_k', -1)
        
        try:
            # Make API call
            response = self.client.messages.create(**params)
            
            # Extract response
            content = ""
            if response.content and len(response.content) > 0:
                # Handle both text and tool use content blocks
                for block in response.content:
                    if hasattr(block, 'text'):
                        content += block.text
            
            usage = {
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
            
            model_response = ModelResponse(
                content=content,
                model=response.model or self.model_name,
                usage=usage,
                finish_reason=response.stop_reason or "stop",
                metadata={
                    'id': response.id,
                    'created': None,  # Claude doesn't provide this
                    'type': response.type
                }
            )
            
            self._log_response(model_response)
            return model_response
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from Anthropic API.
        
        Args:
            messages: Chat messages
            **kwargs: Additional parameters
            
        Yields:
            Text chunks as they arrive
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid message format")
        
        # Extract system message
        system_message = ""
        chat_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                chat_messages.append(msg)
        
        # Ensure first message is from user
        if chat_messages and chat_messages[0]['role'] != 'user':
            chat_messages.insert(0, {'role': 'user', 'content': ''})
        
        # Prepare parameters
        params = {
            'model': self.model_name,
            'messages': chat_messages,
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature),
        }
        
        if system_message:
            params['system'] = system_message
        
        try:
            # Make streaming API call
            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    yield text
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Anthropic streaming error: {str(e)}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens (estimate for Claude).
        
        Claude uses a different tokenizer than OpenAI.
        This is an approximation.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Claude's tokenizer is roughly 1 token per 3-4 characters
        # This is a rough estimate
        return len(text) // 3.5
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a request.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        pricing = self.PRICING.get(self.model_name, self.PRICING['claude-3-sonnet-20240229'])
        
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    def get_model_context_window(self) -> int:
        """Get model's maximum context window."""
        context_windows = {
            'claude-3-opus-20240229': 200000,
            'claude-3-sonnet-20240229': 200000,
            'claude-3-haiku-20240307': 200000,
            'claude-2.1': 200000,
            'claude-2.0': 100000,
        }
        return context_windows.get(self.model_name, 200000)
    
    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """Validate message format for Claude."""
        if not messages:
            return False
        
        # Check all messages have required fields
        for msg in messages:
            if not isinstance(msg, dict):
                return False
            if 'role' not in msg or 'content' not in msg:
                return False
            if msg['role'] not in ['system', 'user', 'assistant']:
                return False
        
        # For Claude, we need at least one user message
        user_messages = [m for m in messages if m['role'] == 'user']
        if not user_messages:
            return False
        
        return True
