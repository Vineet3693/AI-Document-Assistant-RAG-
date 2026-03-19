"""
Documents Routes
Handles document listing, retrieval, search, and deletion.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
from datetime import datetime

router = APIRouter(prefix="/documents", tags=["Documents"])


# In-memory document store (use database in production)
document_store: Dict[str, Dict[str, Any]] = {}


@router.get("/list")
async def list_documents(
    page: int = 1,
    limit: int = 50,
    doc_type: Optional[str] = None,
    search: Optional[str] = None
):
    """
    List all uploaded documents with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        limit: Items per page
        doc_type: Filter by document type
        search: Search in filenames
        
    Returns:
        Paginated list of documents
    """
    # Get all documents
    docs = list(document_store.values())
    
    # Apply filters
    if doc_type:
        docs = [d for d in docs if d.get('file_type') == doc_type]
    
    if search:
        search_lower = search.lower()
        docs = [d for d in docs if search_lower in d.get('filename', '').lower()]
    
    # Sort by upload time (newest first)
    docs.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
    
    # Pagination
    total = len(docs)
    start = (page - 1) * limit
    end = start + limit
    paginated_docs = docs[start:end]
    
    return JSONResponse({
        "documents": paginated_docs,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    })


@router.get("/{document_id}")
async def get_document(document_id: str):
    """
    Get details of a specific document.
    
    Args:
        document_id: Document ID
        
    Returns:
        Document details
    """
    doc = document_store.get(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return JSONResponse({
        "document": doc
    })


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and its vector embeddings.
    
    Args:
        document_id: Document ID
        
    Returns:
        Deletion confirmation
    """
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Remove from store
        doc = document_store.pop(document_id)
        
        # Delete physical file
        file_path = f"data/uploads/{document_id}{doc.get('file_ext', '')}"
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from vector store (placeholder)
        # In production: vector_store.delete_document(document_id)
        
        return JSONResponse({
            "status": "success",
            "message": f"Document '{doc.get('filename')}' deleted successfully",
            "document_id": document_id
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.get("/search")
async def search_documents(
    query: str,
    limit: int = 10
):
    """
    Search documents by filename and metadata.
    
    Args:
        query: Search query
        limit: Maximum results
        
    Returns:
        Matching documents
    """
    results = []
    query_lower = query.lower()
    
    for doc_id, doc in document_store.items():
        score = 0
        
        # Search in filename
        if query_lower in doc.get('filename', '').lower():
            score += 3
        
        # Search in tags
        tags = doc.get('tags', [])
        if any(query_lower in tag.lower() for tag in tags):
            score += 2
        
        # Search in document type
        if query_lower in doc.get('doc_type', '').lower():
            score += 1
        
        if score > 0:
            results.append({
                **doc,
                'relevance_score': score
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return JSONResponse({
        "query": query,
        "results": results[:limit],
        "count": len(results)
    })


@router.post("/{document_id}/tags")
async def update_document_tags(
    document_id: str,
    tags: List[str]
):
    """
    Update tags for a document.
    
    Args:
        document_id: Document ID
        tags: New list of tags
        
    Returns:
        Updated document
    """
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document_store[document_id]['tags'] = tags
    document_store[document_id]['updated_at'] = datetime.utcnow().isoformat()
    
    return JSONResponse({
        "status": "success",
        "document": document_store[document_id]
    })


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    limit: int = 100,
    offset: int = 0
):
    """
    Get chunks for a document.
    
    Args:
        document_id: Document ID
        limit: Maximum chunks to return
        offset: Offset for pagination
        
    Returns:
        List of chunks
    """
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # In production, retrieve from vector store
    # This is a placeholder
    return JSONResponse({
        "document_id": document_id,
        "chunks": [],
        "total_chunks": 0,
        "limit": limit,
        "offset": offset
    })


@router.get("/stats")
async def get_document_stats():
    """
    Get statistics about uploaded documents.
    
    Returns:
        Document statistics
    """
    total_docs = len(document_store)
    
    if total_docs == 0:
        return JSONResponse({
            "total_documents": 0,
            "total_size_bytes": 0,
            "by_type": {},
            "recent_uploads": 0
        })
    
    # Calculate stats
    total_size = sum(d.get('file_size', 0) for d in document_store.values())
    
    by_type = {}
    for doc in document_store.values():
        doc_type = doc.get('file_type', 'unknown')
        by_type[doc_type] = by_type.get(doc_type, 0) + 1
    
    # Recent uploads (last 7 days)
    seven_days_ago = datetime.utcnow().timestamp() - (7 * 24 * 60 * 60)
    recent = sum(
        1 for d in document_store.values()
        if datetime.fromisoformat(d.get('upload_time', '1970-01-01')).timestamp() > seven_days_ago
    )
    
    return JSONResponse({
        "total_documents": total_docs,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "by_type": by_type,
        "recent_uploads_7d": recent,
        "average_size_kb": round(total_size / total_docs / 1024, 2)
    })
