"""
Chat Routes
Handles Q&A, multi-document questions, and chat history.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    question: str = Field(..., description="User's question")
    document_ids: Optional[List[str]] = Field(None, description="Document IDs to search")
    top_k: int = Field(default=5, description="Number of chunks to retrieve")
    template: Optional[str] = Field(None, description="Prompt template name")
    industry_mode: Optional[str] = Field(None, description="Industry mode (legal, finance, etc.)")
    language: Optional[str] = Field(default="English", description="Response language")
    stream: bool = Field(default=False, description="Stream response")


class ChatResponse(BaseModel):
    id: str
    answer: str
    citations: Optional[Dict[str, Any]] = None
    confidence: str
    documents_used: List[str]
    tokens_used: Dict[str, int]
    latency_ms: float
    timestamp: str


# In-memory chat history storage (use database in production)
chat_history_store: Dict[str, List[Dict[str, Any]]] = {}


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question about uploaded documents.
    
    Args:
        request: Chat request with question and parameters
        
    Returns:
        Answer with citations and metadata
    """
    # Get RAG engine from app state
    # In production, this would be properly injected
    try:
        from src.rag.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        
        # Check if engine is configured
        if not rag_engine.retriever or not rag_engine.ai_model:
            raise HTTPException(
                status_code=503,
                detail="RAG engine not fully configured. Please set up retriever and AI model."
            )
        
        # Get chat history for context
        session_id = "default_session"  # In production, use actual session
        history = chat_history_store.get(session_id, [])
        
        # Ask question
        response = rag_engine.ask(
            question=request.question,
            document_ids=request.document_ids,
            top_k=request.top_k,
            template_name=request.template,
            industry_mode=request.industry_mode,
            language=request.language,
            chat_history=history if len(history) > 0 else None
        )
        
        # Store in history
        history.append({"role": "user", "content": request.question})
        history.append({"role": "assistant", "content": response.answer})
        chat_history_store[session_id] = history[-20:]  # Keep last 20 messages
        
        return ChatResponse(
            id=response.id,
            answer=response.answer,
            citations=response.citations.to_dict() if response.citations else None,
            confidence=response.confidence,
            documents_used=response.documents_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            timestamp=response.timestamp.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.post("/ask-multi")
async def ask_multi_document(
    question: str,
    document_ids: List[str],
    top_k_per_doc: int = 3,
    language: str = "English"
):
    """
    Ask a question across multiple specific documents.
    
    Args:
        question: User's question
        document_ids: List of document IDs to search
        top_k_per_doc: Chunks to retrieve per document
        language: Response language
        
    Returns:
        Synthesized answer from multiple documents
    """
    try:
        from src.rag.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        
        if not rag_engine.retriever or not rag_engine.ai_model:
            raise HTTPException(status_code=503, detail="RAG engine not configured")
        
        response = rag_engine.ask_multi_document(
            question=question,
            document_ids=document_ids,
            top_k_per_doc=top_k_per_doc
        )
        
        return JSONResponse({
            "id": response.id,
            "answer": response.answer,
            "citations": response.citations.to_dict() if response.citations else None,
            "confidence": response.confidence,
            "documents_used": response.documents_used,
            "tokens_used": response.tokens_used,
            "latency_ms": response.latency_ms,
            "timestamp": response.timestamp.isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask/stream")
async def ask_question_stream(request: ChatRequest):
    """
    Ask a question with streaming response.
    
    Args:
        request: Chat request
        
    Returns:
        Streaming response
    """
    try:
        from src.rag.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        
        if not rag_engine.retriever or not rag_engine.ai_model:
            raise HTTPException(status_code=503, detail="RAG engine not configured")
        
        async def generate():
            async for chunk in rag_engine.ask_stream(
                question=request.question,
                document_ids=request.document_ids,
                top_k=request.top_k,
                template_name=request.template,
                industry_mode=request.industry_mode,
                language=request.language
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chat_history(session_id: Optional[str] = None):
    """
    Get chat history.
    
    Args:
        session_id: Session identifier (defaults to 'default_session')
        
    Returns:
        List of chat messages
    """
    session_id = session_id or "default_session"
    history = chat_history_store.get(session_id, [])
    
    return JSONResponse({
        "session_id": session_id,
        "messages": history,
        "count": len(history)
    })


@router.post("/clear")
async def clear_chat_history(session_id: Optional[str] = None):
    """
    Clear chat history.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Confirmation message
    """
    session_id = session_id or "default_session"
    
    if session_id in chat_history_store:
        del chat_history_store[session_id]
    
    return JSONResponse({
        "status": "success",
        "message": "Chat history cleared",
        "session_id": session_id
    })


@router.delete("/history/{message_id}")
async def delete_message(message_id: str, session_id: Optional[str] = None):
    """
    Delete a specific message from history.
    
    Note: This is a simplified implementation.
    """
    session_id = session_id or "default_session"
    history = chat_history_store.get(session_id, [])
    
    # In production, messages would have IDs
    # This is a placeholder
    return JSONResponse({
        "status": "success",
        "message": "Message deleted (placeholder implementation)"
    })
