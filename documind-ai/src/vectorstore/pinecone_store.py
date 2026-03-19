"""
DocuMind AI - Pinecone Vector Store
Production cloud vector database integration.
"""

import os
from typing import List, Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PineconeStore:
    """Pinecone cloud vector store for production use."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: str = "us-west1-gcp",
        index_name: str = "documind-ai",
        dimension: int = 1536
    ):
        """
        Initialize Pinecone store.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the index
            dimension: Embedding dimension
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("Pinecone API key not provided")
        
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        self._index = None
        self._pinecone_client = None
        
        logger.info(f"Initialized PineconeStore: {index_name}")
    
    def _get_client(self):
        """Lazy load Pinecone client."""
        if self._pinecone_client is None:
            try:
                import pinecone
                pinecone.init(api_key=self.api_key, environment=self.environment)
                self._pinecone_client = pinecone
                logger.debug("Pinecone client initialized")
            except ImportError:
                logger.error("pinecone not installed. Run: pip install pinecone-client")
                raise
        return self._pinecone_client
    
    def _get_index(self):
        """Get or create Pinecone index."""
        client = self._get_client()
        
        # Check if index exists
        existing_indexes = [idx.name for idx in client.list_indexes()]
        
        if self.index_name not in existing_indexes:
            logger.info(f"Creating new index: {self.index_name}")
            client.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine"
            )
        
        self._index = client.Index(self.index_name)
        return self._index
    
    def add_documents(
        self,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None,
        namespace: str = ""
    ) -> List[str]:
        """
        Add documents to Pinecone.
        
        Args:
            embeddings: List of embedding vectors
            metadatas: Metadata for each document
            ids: Document IDs
            namespace: Pinecone namespace for isolation
            
        Returns:
            List of document IDs
        """
        index = self._get_index()
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in embeddings]
        
        if metadatas is None:
            metadatas = [{} for _ in embeddings]
        
        # Prepare vectors for upsert
        vectors = []
        for i, (emb_id, embedding, metadata) in enumerate(zip(ids, embeddings, metadatas)):
            vectors.append({
                "id": emb_id,
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch, namespace=namespace)
        
        logger.info(f"Added {len(embeddings)} vectors to Pinecone")
        return ids
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Dict[str, Any] = None,
        namespace: str = ""
    ) -> Dict[str, List]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results
            filter_metadata: Metadata filters
            namespace: Pinecone namespace
            
        Returns:
            Search results with documents and metadata
        """
        index = self._get_index()
        
        response = index.query(
            vector=query_embedding,
            top_k=n_results,
            filter=filter_metadata,
            namespace=namespace,
            include_metadata=True
        )
        
        matches = response.get("matches", [])
        
        return {
            "documents": [m.metadata.get("text", "") for m in matches],
            "metadatas": [m.metadata for m in matches],
            "scores": [m.score for m in matches],
            "ids": [m.id for m in matches]
        }
    
    def delete_namespace(self, namespace: str):
        """Delete all vectors in a namespace."""
        index = self._get_index()
        index.delete(delete_all=True, namespace=namespace)
        logger.info(f"Deleted namespace: {namespace}")
    
    def get_stats(self) -> dict:
        """Get index statistics."""
        index = self._get_index()
        stats = index.describe_index_stats()
        return {
            "dimension": stats.get("dimension"),
            "total_vectors": stats.get("total_vector_count"),
            "namespaces": list(stats.get("namespaces", {}).keys())
        }
    
    def __repr__(self):
        return f"PineconeStore(index={self.index_name})"
