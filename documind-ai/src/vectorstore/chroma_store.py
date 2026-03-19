"""
DocuMind AI - ChromaDB Vector Store
Local vector database for document embeddings.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from ..embeddings.base_embedder import BaseEmbedder
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChromaStore:
    """ChromaDB vector store for local document storage."""
    
    def __init__(
        self,
        persist_directory: str = "./data/vectorstore",
        collection_name: str = "documind_default"
    ):
        """
        Initialize ChromaDB store.
        
        Args:
            persist_directory: Directory to persist data
            collection_name: Default collection name
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        
        os.makedirs(persist_directory, exist_ok=True)
        logger.info(f"Initialized ChromaStore at {persist_directory}")
    
    def _get_client(self):
        """Lazy load ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                
                self._client = chromadb.Client(Settings(
                    persist_directory=self.persist_directory,
                    anonymized_telemetry=False
                ))
                logger.debug("ChromaDB client initialized")
            except ImportError:
                logger.error("chromadb not installed. Run: pip install chromadb")
                raise
        return self._client
    
    def create_collection(self, name: str = None) -> str:
        """
        Create a new collection.
        
        Args:
            name: Collection name (uses default if None)
            
        Returns:
            Collection name
        """
        client = self._get_client()
        collection_name = name or self.collection_name
        
        # Delete if exists
        try:
            existing = client.get_collection(name=collection_name)
            client.delete_collection(name=collection_name)
            logger.debug(f"Deleted existing collection: {collection_name}")
        except Exception:
            pass
        
        # Create new
        self._collection = client.create_collection(name=collection_name)
        logger.info(f"Created collection: {collection_name}")
        return collection_name
    
    def get_collection(self, name: str = None):
        """Get or create a collection."""
        client = self._get_client()
        collection_name = name or self.collection_name
        
        try:
            self._collection = client.get_collection(name=collection_name)
        except Exception:
            self.create_collection(collection_name)
        
        return self._collection
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None,
        collection_name: str = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional metadata for each document
            ids: Optional IDs (generated if not provided)
            collection_name: Target collection
            
        Returns:
            List of document IDs
        """
        collection = self.get_collection(collection_name)
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        if metadatas is None:
            metadatas = [{} for _ in documents]
        
        # Ensure metadata values are valid types
        cleaned_metadatas = []
        for meta in metadatas:
            cleaned = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    cleaned[k] = v
                else:
                    cleaned[k] = str(v)
            cleaned_metadatas.append(cleaned)
        
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=cleaned_metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to collection")
        return ids
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Dict[str, Any] = None,
        collection_name: str = None
    ) -> Dict[str, List]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_metadata: Metadata filters
            collection_name: Collection to search
            
        Returns:
            Dictionary with documents, metadatas, distances, ids
        """
        collection = self.get_collection(collection_name)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"]
        )
        
        # Flatten results (remove outer list)
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "ids": results["ids"][0] if results["ids"] else []
        }
    
    def delete_collection(self, name: str = None):
        """Delete a collection."""
        client = self._get_client()
        collection_name = name or self.collection_name
        
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        client = self._get_client()
        return [col.name for col in client.list_collections()]
    
    def get_document_count(self, collection_name: str = None) -> int:
        """Get total document count in collection."""
        collection = self.get_collection(collection_name)
        return collection.count()
    
    def clear_all(self):
        """Clear all collections."""
        for name in self.list_collections():
            self.delete_collection(name)
        logger.info("Cleared all collections")
    
    def __repr__(self):
        return f"ChromaStore(path={self.persist_directory})"
