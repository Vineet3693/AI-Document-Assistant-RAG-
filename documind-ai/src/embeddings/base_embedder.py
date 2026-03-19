"""
DocuMind AI - Base Embedder
Abstract base class for all embedding models.
"""

from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np


class BaseEmbedder(ABC):
    """Abstract base class for text embedding models."""
    
    def __init__(self, model_name: str = "default", dimension: int = 384):
        """
        Initialize the embedder.
        
        Args:
            model_name: Name of the embedding model
            dimension: Dimension of the embedding vectors
        """
        self.model_name = model_name
        self.dimension = dimension
        self._model = None
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text into a vector.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed multiple texts into vectors.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            
        Returns:
            List of embedding vectors
        """
        pass
    
    def embed_with_metadata(self, text: str, metadata: dict = None) -> dict:
        """
        Embed text and return with metadata.
        
        Args:
            text: Text to embed
            metadata: Optional metadata to attach
            
        Returns:
            Dictionary with embedding and metadata
        """
        embedding = self.embed_text(text)
        return {
            "embedding": embedding,
            "dimension": len(embedding),
            "model": self.model_name,
            "metadata": metadata or {}
        }
    
    def normalize_embedding(self, embedding: List[float]) -> List[float]:
        """
        Normalize an embedding vector to unit length.
        
        Args:
            embedding: Raw embedding vector
            
        Returns:
            Normalized embedding vector
        """
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return (np.array(embedding) / norm).tolist()
    
    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def load_model(self):
        """Load the embedding model (to be implemented by subclasses)."""
        pass
    
    def unload_model(self):
        """Unload the model from memory."""
        self._model = None
    
    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model_name}, dim={self.dimension})"
