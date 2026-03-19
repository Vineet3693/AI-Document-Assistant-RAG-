"""
DocuMind AI - Token Counter
Tracks token usage for OpenAI and Anthropic models with cost calculation.
"""

import tiktoken
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenUsage:
    """Represents token usage for a single API call."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    cost_usd: float
    timestamp: datetime


class TokenCounter:
    """Count tokens and track API costs for different LLM providers."""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        # OpenAI models
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "text-embedding-3-small": {"input": 0.00002, "output": 0},
        "text-embedding-3-large": {"input": 0.00013, "output": 0},
        
        # Anthropic models
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    }
    
    def __init__(self):
        self.encoders: Dict[str, tiktoken.Encoding] = {}
        self.total_usage: Dict[str, TokenUsage] = []
        self.session_cost: float = 0.0
    
    def _get_encoder(self, model_name: str) -> tiktoken.Encoding:
        """Get or create encoder for the specified model."""
        if model_name not in self.encoders:
            try:
                self.encoders[model_name] = tiktoken.encoding_for_model(model_name)
            except KeyError:
                # Fallback to cl100k_base for unknown models
                self.encoders[model_name] = tiktoken.get_encoding("cl100k_base")
        return self.encoders[model_name]
    
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens in text for a specific model."""
        encoder = self._get_encoder(model)
        return len(encoder.encode(text))
    
    def count_messages_tokens(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4"
    ) -> int:
        """Count tokens in a list of chat messages."""
        encoder = self._get_encoder(model)
        
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = 1     # if there's a name
        
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoder.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        
        num_tokens += 3  # every assistant message is assisted by <|start|>assistant<|message|>
        return num_tokens
    
    def calculate_cost(
        self, 
        input_tokens: int, 
        output_tokens: int, 
        model: str
    ) -> float:
        """Calculate cost in USD for given token usage."""
        if model not in self.PRICING:
            # Try to find base model
            base_model = model.split("-turbo")[0].split("-2024")[0]
            if base_model not in self.PRICING:
                return 0.0
            pricing = self.PRICING[base_model]
        else:
            pricing = self.PRICING[model]
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    def track_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> TokenUsage:
        """Track token usage and calculate cost."""
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            model=model,
            cost_usd=cost,
            timestamp=datetime.now()
        )
        
        self.total_usage.append(usage)
        self.session_cost += cost
        
        return usage
    
    def get_session_stats(self) -> Dict:
        """Get statistics for current session."""
        if not self.total_usage:
            return {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "api_calls": 0,
            }
        
        return {
            "total_input_tokens": sum(u.input_tokens for u in self.total_usage),
            "total_output_tokens": sum(u.output_tokens for u in self.total_usage),
            "total_tokens": sum(u.total_tokens for u in self.total_usage),
            "total_cost_usd": round(self.session_cost, 4),
            "api_calls": len(self.total_usage),
            "average_tokens_per_call": round(
                sum(u.total_tokens for u in self.total_usage) / len(self.total_usage), 2
            ),
        }
    
    def reset_session(self) -> None:
        """Reset session tracking."""
        self.total_usage = []
        self.session_cost = 0.0
    
    def get_usage_by_model(self) -> Dict[str, Dict]:
        """Get usage breakdown by model."""
        model_stats = {}
        
        for usage in self.total_usage:
            if usage.model not in model_stats:
                model_stats[usage.model] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost_usd": 0.0,
                    "calls": 0,
                }
            
            model_stats[usage.model]["input_tokens"] += usage.input_tokens
            model_stats[usage.model]["output_tokens"] += usage.output_tokens
            model_stats[usage.model]["total_tokens"] += usage.total_tokens
            model_stats[usage.model]["cost_usd"] += usage.cost_usd
            model_stats[usage.model]["calls"] += 1
        
        # Round costs
        for model in model_stats:
            model_stats[model]["cost_usd"] = round(model_stats[model]["cost_usd"], 4)
        
        return model_stats


# Singleton instance
_token_counter: Optional[TokenCounter] = None


def get_token_counter() -> TokenCounter:
    """Get the global token counter instance."""
    global _token_counter
    if _token_counter is None:
        _token_counter = TokenCounter()
    return _token_counter
