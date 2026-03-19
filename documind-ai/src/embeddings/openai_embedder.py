"""
DocuMind AI - OpenAI Embedder
OpenAI text embedding integration.
"""

import os
from typing import List, Optional
from openai import OpenAI
from .base_embedder import BaseEmbedder
from ..utils.logger import get_logger
from ..utils.token_counter import TokenCounter

logger = get_logger(__name__)


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI text embedding model integration."""
    
    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        dimension: int = 1536,
        max_retries: int = 3
    ):
        """
        Initialize OpenAI embedder.
        
        Args:
            model_name: OpenAI embedding model name
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            dimension: Output dimension (1536 for small, 3072 for large)
            max_retries: Number of retries on failure
        """
        super().__init__(model_name=model_name, dimension=dimension)
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = max_retries
        self.token_counter = TokenCounter()
        
        logger.info(f"Initialized OpenAIEmbedder with model: {model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text using OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension
        
        for attempt in range(self.max_retries):
            try:
                # Count tokens for cost tracking
                tokens = self.token_counter.count_tokens(text, model="cl100k_base")
                
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=text,
                    dimensions=self.dimension if self.model_name == "text-embedding-3-large" else None
                )
                
                embedding = response.data[0].embedding
                usage = response.usage
                
                # Log usage
                logger.debug(f"Embedded text ({tokens} tokens), API usage: {usage}")
                
                return embedding
                
            except Exception as e:
                logger.error(f"Embedding attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("All embedding attempts failed")
                    raise
                continue
        
        return [0.0] * self.dimension
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        total_tokens = 0
        
        # Filter out empty texts but keep track of indices
        valid_texts = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        
        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i:i + batch_size]
            batch_content = [t[1] for t in batch]
            
            try:
                # Count tokens
                batch_tokens = sum(self.token_counter.count_tokens(t, model="cl100k_base") 
                                  for t in batch_content)
                total_tokens += batch_tokens
                
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=batch_content,
                    dimensions=self.dimension if self.model_name == "text-embedding-3-large" else None
                )
                
                # Sort embeddings back to original order
                batch_embeddings = sorted(
                    zip([t[0] for t in batch], [e.embedding for e in response.data]),
                    key=lambda x: x[0]
                )
                
                all_embeddings.extend([emb for _, emb in batch_embeddings])
                
                logger.debug(f"Processed batch {i // batch_size + 1}, {len(batch)} texts")
                
            except Exception as e:
                logger.error(f"Batch embedding failed: {str(e)}")
                # Return zeros for failed batch
                all_embeddings.extend([[0.0] * self.dimension] * len(batch))
        
        # Fill in zeros for originally empty texts
        final_embeddings = []
        valid_idx = 0
        for i, text in enumerate(texts):
            if text and text.strip():
                final_embeddings.append(all_embeddings[valid_idx])
                valid_idx += 1
            else:
                final_embeddings.append([0.0] * self.dimension)
        
        logger.info(f"Embedded {len(texts)} texts, total tokens: {total_tokens}")
        return final_embeddings
    
    def get_model_info(self) -> dict:
        """Get information about the current embedding model."""
        return {
            "model": self.model_name,
            "dimension": self.dimension,
            "provider": "OpenAI",
            "max_input_tokens": 8191,
            "pricing_per_1k_tokens": 0.00002 if "small" in self.model_name else 0.00013
        }
    
    def __repr__(self):
        return f"OpenAIEmbedder(model={self.model_name}, dim={self.dimension})"
