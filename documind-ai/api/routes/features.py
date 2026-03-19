"""
Features Routes
Handles summarization, comparison, extraction, translation, and other AI features.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

router = APIRouter(prefix="/features", tags=["Features"])


class SummarizeRequest(BaseModel):
    document_id: str
    summary_type: str = Field(default="executive", description="one_line, executive, detailed, or bullet_points")


class CompareRequest(BaseModel):
    document_id_1: str
    document_id_2: str


class ExtractRequest(BaseModel):
    document_id: str
    extract_types: List[str] = Field(default=["names", "dates", "numbers", "actions"])


@router.post("/summarize")
async def summarize_document(request: SummarizeRequest):
    """
    Generate a summary of a document.
    
    Args:
        document_id: Document to summarize
        summary_type: Type of summary (one_line, executive, detailed, bullet_points)
        
    Returns:
        Generated summary
    """
    try:
        from src.rag.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        
        if not rag_engine.retriever or not rag_engine.ai_model:
            raise HTTPException(status_code=503, detail="RAG engine not configured")
        
        result = rag_engine.summarize_document(
            document_id=request.document_id,
            summary_type=request.summary_type
        )
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return JSONResponse({
            "status": "success",
            "document_id": request.document_id,
            "summary_type": request.summary_type,
            "summary": result['summary'],
            "tokens_used": result.get('tokens_used', {})
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_documents(request: CompareRequest):
    """
    Compare two documents side by side.
    
    Args:
        document_id_1: First document ID
        document_id_2: Second document ID
        
    Returns:
        Comparison report
    """
    try:
        from src.rag.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        
        if not rag_engine.retriever or not rag_engine.ai_model:
            raise HTTPException(status_code=503, detail="RAG engine not configured")
        
        result = rag_engine.compare_documents(
            document_id_1=request.document_id_1,
            document_id_2=request.document_id_2
        )
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return JSONResponse({
            "status": "success",
            "document_1": result['document_1'],
            "document_2": result['document_2'],
            "comparison": result['comparison'],
            "tokens_used": result.get('tokens_used', {})
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_information(request: ExtractRequest):
    """
    Extract specific information from a document.
    
    Args:
        document_id: Document ID
        extract_types: Types of info to extract (names, dates, numbers, actions, contacts)
        
    Returns:
        Extracted information
    """
    try:
        from src.features.extractor import InformationExtractor
        extractor = InformationExtractor()
        
        # Get document text (placeholder - would retrieve from storage)
        # In production: get full document text from database/vector store
        document_text = "Document content placeholder"
        
        results = {}
        
        if 'names' in request.extract_types:
            results['names'] = extractor.extract_names(document_text)
        
        if 'dates' in request.extract_types:
            results['dates'] = extractor.extract_dates(document_text)
        
        if 'numbers' in request.extract_types:
            results['numbers'] = extractor.extract_numbers(document_text)
        
        if 'actions' in request.extract_types:
            results['actions'] = extractor.extract_actions(document_text)
        
        if 'contacts' in request.extract_types:
            results['contacts'] = extractor.extract_contacts(document_text)
        
        return JSONResponse({
            "status": "success",
            "document_id": request.document_id,
            "extracted_data": results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_document(
    document_id: str,
    target_language: str,
    source_language: Optional[str] = None
):
    """
    Translate a document to another language.
    
    Args:
        document_id: Document to translate
        target_language: Target language
        source_language: Source language (auto-detect if not provided)
        
    Returns:
        Translated text
    """
    try:
        from src.features.translator import DocumentTranslator
        translator = DocumentTranslator()
        
        # Placeholder - would get actual document text
        document_text = "Document content to translate"
        
        result = translator.translate(
            text=document_text,
            target_language=target_language,
            source_language=source_language
        )
        
        return JSONResponse({
            "status": "success",
            "document_id": document_id,
            "source_language": result.get('source_language', 'auto'),
            "target_language": target_language,
            "translated_text": result['translated_text']
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-questions")
async def generate_questions(
    document_id: str,
    num_questions: int = 10,
    question_type: str = "general"
):
    """
    Generate questions from a document.
    
    Args:
        document_id: Document ID
        num_questions: Number of questions to generate
        question_type: Type (general, quiz, interview, flashcard)
        
    Returns:
        Generated questions
    """
    try:
        from src.features.question_generator import QuestionGenerator
        generator = QuestionGenerator()
        
        # Placeholder - would get actual document text
        document_text = "Document content"
        
        questions = generator.generate(
            text=document_text,
            num_questions=num_questions,
            question_type=question_type
        )
        
        return JSONResponse({
            "status": "success",
            "document_id": document_id,
            "question_type": question_type,
            "questions": questions
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-risks")
async def detect_risks(
    document_id: str,
    risk_type: str = "general"
):
    """
    Detect risks in a document.
    
    Args:
        document_id: Document ID
        risk_type: Type of risk detection (legal, financial, compliance, general)
        
    Returns:
        Risk analysis report
    """
    try:
        from src.features.risk_detector import RiskDetector
        detector = RiskDetector(risk_type=risk_type)
        
        # Placeholder - would get actual document text
        document_text = "Document content"
        
        result = detector.analyze(document_text)
        
        return JSONResponse({
            "status": "success",
            "document_id": document_id,
            "risk_type": risk_type,
            "risk_score": result.get('risk_score', 0),
            "risks_found": result.get('risks', []),
            "recommendations": result.get('recommendations', [])
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-sentiment")
async def analyze_sentiment(document_id: str):
    """
    Analyze sentiment of a document.
    
    Args:
        document_id: Document ID
        
    Returns:
        Sentiment analysis results
    """
    try:
        # Placeholder implementation
        # In production: use NLP library or AI model
        
        return JSONResponse({
            "status": "success",
            "document_id": document_id,
            "sentiment": "neutral",
            "confidence": 0.85,
            "scores": {
                "positive": 0.3,
                "neutral": 0.5,
                "negative": 0.2
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
