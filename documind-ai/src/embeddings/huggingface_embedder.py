"""
DocuMind AI - HuggingFace Embedder
Local embedding models using sentence-transformers.
"""

import os
from typing import List, Optional
from .base_embedder import BaseEmbedder
from ..utils.logger import get_logger

logger = get_logger(__name__)


class HuggingFaceEmbedder(BaseEmbedder):
    """HuggingFace sentence-transformers for local embeddings."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize HuggingFace embedder.
        
        Args:
            model_name: HuggingFace model name
            device: Device to run on ('cpu', 'cuda', 'mps')
            cache_dir: Directory to cache models
        """
        # Default dimension for all-MiniLM-L6-v2
        default_dim = 384
        super().__init__(model_name=model_name, dimension=default_dim)
        
        self.device = device or self._detect_device()
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/documind/embeddings")
        self._model = None
        
        logger.info(f"Initialized HuggingFaceEmbedder: {model_name} on {self.device}")
    
    def _detect_device(self) -> str:
        """Detect best available device."""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"
    
    def load_model(self):
        """Load the sentence-transformers model."""
        if self._model is not None:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            os.makedirs(self.cache_dir, exist_ok=True)
            
            logger.info(f"Loading model: {self.model_name}")
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_dir
            )
            
            # Update dimension based on loaded model
            if hasattr(self._model, 'get_sentence_embedding_dimension'):
                self.dimension = self._model.get_sentence_embedding_dimension()
            
            logger.info(f"Model loaded successfully, dimension: {self.dimension}")
            
        except ImportError:
            logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text using local model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if self._model is None:
            self.load_model()
        
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension
        
        try:
            embedding = self._model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
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
        if self._model is None:
            self.load_model()
        
        if not texts:
            return []
        
        try:
            # Handle empty texts
            valid_indices = [i for i, t in enumerate(texts) if t and t.strip()]
            valid_texts = [texts[i] for i in valid_indices]
            
            if not valid_texts:
                return [[0.0] * self.dimension] * len(texts)
            
            # Encode all valid texts
            embeddings = self._model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=len(valid_texts) > 100
            )
            
            # Reconstruct full list with zeros for empty texts
            final_embeddings = [[0.0] * self.dimension] * len(texts)
            for idx, emb_idx in enumerate(valid_indices):
                final_embeddings[emb_idx] = embeddings[idx].tolist()
            
            logger.info(f"Embedded {len(texts)} texts locally")
            return final_embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding failed: {str(e)}")
            return [[0.0] * self.dimension] * len(texts)
    
    def get_model_info(self) -> dict:
        """Get information about the current embedding model."""
        return {
            "model": self.model_name,
            "dimension": self.dimension,
            "provider": "HuggingFace",
            "device": self.device,
            "local": True,
            "cost": 0.0
        }
    
    def unload_model(self):
        """Unload model from memory."""
        if self._model is not None:
            del self._model
            self._model = None
            
            # Clear CUDA cache if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            
            logger.info("Model unloaded from memory")
    
    def __repr__(self):
        return f"HuggingFaceEmbedder(model={self.model_name}, device={self.device}, dim={self.dimension})"
