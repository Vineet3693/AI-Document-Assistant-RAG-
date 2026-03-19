"""
Analytics Routes
Provides usage statistics, token tracking, and audit logs.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# In-memory analytics store (use database in production)
analytics_store = {
    "usage": [],
    "questions": [],
    "documents_accessed": [],
    "audit_logs": []
}


@router.get("/usage")
async def get_usage_analytics(
    days: int = 7,
    group_by: str = "day"
):
    """
    Get API usage and token consumption analytics.
    
    Args:
        days: Number of days to analyze
        group_by: Group results by 'hour', 'day', or 'week'
        
    Returns:
        Usage statistics
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Filter recent usage
    recent_usage = [
        u for u in analytics_store["usage"]
        if datetime.fromisoformat(u.get('timestamp', '1970-01-01')) > cutoff_date
    ]
    
    # Calculate totals
    total_tokens = sum(u.get('tokens_used', {}).get('total', 0) for u in recent_usage)
    total_requests = len(recent_usage)
    avg_tokens_per_request = total_tokens / total_requests if total_requests > 0 else 0
    
    # Estimate cost (using average pricing)
    estimated_cost = (total_tokens / 1000) * 0.002  # ~$0.002 per 1K tokens average
    
    # Group by time period
    grouped_data = {}
    for usage in recent_usage:
        timestamp = datetime.fromisoformat(usage.get('timestamp', '1970-01-01'))
        
        if group_by == "hour":
            key = timestamp.strftime("%Y-%m-%d %H:00")
        elif group_by == "week":
            key = timestamp.strftime("%Y-W%W")
        else:  # day
            key = timestamp.strftime("%Y-%m-%d")
        
        if key not in grouped_data:
            grouped_data[key] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0
            }
        
        grouped_data[key]["requests"] += 1
        grouped_data[key]["tokens"] += usage.get('tokens_used', {}).get('total', 0)
        grouped_data[key]["cost"] += (usage.get('tokens_used', {}).get('total', 0) / 1000) * 0.002
    
    return JSONResponse({
        "period": {
            "days": days,
            "group_by": group_by,
            "start_date": cutoff_date.isoformat(),
            "end_date": datetime.utcnow().isoformat()
        },
        "summary": {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "avg_tokens_per_request": round(avg_tokens_per_request, 2),
            "estimated_cost_usd": round(estimated_cost, 4)
        },
        "time_series": grouped_data
    })


@router.get("/documents")
async def get_document_analytics():
    """
    Get document access and usage statistics.
    
    Returns:
        Document analytics
    """
    # Count accesses per document
    doc_access_count = {}
    for access in analytics_store["documents_accessed"]:
        doc_id = access.get('document_id')
        doc_access_count[doc_id] = doc_access_count.get(doc_id, 0) + 1
    
    # Get most accessed documents
    sorted_docs = sorted(
        doc_access_count.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return JSONResponse({
        "total_documents_accessed": len(doc_access_count),
        "total_accesses": sum(doc_access_count.values()),
        "most_accessed": [
            {"document_id": doc_id, "access_count": count}
            for doc_id, count in sorted_docs
        ],
        "recent_uploads": len(analytics_store["documents_accessed"])
    })


@router.get("/questions")
async def get_question_analytics(limit: int = 20):
    """
    Get popular questions and query patterns.
    
    Args:
        limit: Number of top questions to return
        
    Returns:
        Question analytics
    """
    # Count question frequency
    question_count = {}
    for q in analytics_store["questions"]:
        question = q.get('question', '')
        # Normalize question (lowercase, strip)
        normalized = question.lower().strip()
        question_count[normalized] = question_count.get(normalized, 0) + 1
    
    # Get most common questions
    sorted_questions = sorted(
        question_count.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]
    
    return JSONResponse({
        "total_questions": len(analytics_store["questions"]),
        "unique_questions": len(question_count),
        "top_questions": [
            {"question": q, "count": c}
            for q, c in sorted_questions
        ]
    })


@router.get("/audit")
async def get_audit_log(
    days: int = 30,
    action_type: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 100
):
    """
    Get audit logs for compliance and security.
    
    Args:
        days: Number of days to retrieve
        action_type: Filter by action type (upload, delete, access, etc.)
        user_id: Filter by user ID
        limit: Maximum entries to return
        
    Returns:
        Audit log entries
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Filter logs
    filtered_logs = [
        log for log in analytics_store["audit_logs"]
        if datetime.fromisoformat(log.get('timestamp', '1970-01-01')) > cutoff_date
    ]
    
    if action_type:
        filtered_logs = [l for l in filtered_logs if l.get('action') == action_type]
    
    if user_id:
        filtered_logs = [l for l in filtered_logs if l.get('user_id') == user_id]
    
    # Sort by timestamp (newest first)
    filtered_logs.sort(
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    return JSONResponse({
        "filters": {
            "days": days,
            "action_type": action_type,
            "user_id": user_id
        },
        "total_entries": len(filtered_logs),
        "entries": filtered_logs[:limit]
    })


@router.get("/cost")
async def get_cost_breakdown(
    days: int = 30,
    model: Optional[str] = None
):
    """
    Get detailed cost breakdown by model and feature.
    
    Args:
        days: Number of days to analyze
        model: Filter by specific AI model
        
    Returns:
        Cost breakdown
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Filter recent usage
    recent_usage = [
        u for u in analytics_store["usage"]
        if datetime.fromisoformat(u.get('timestamp', '1970-01-01')) > cutoff_date
    ]
    
    if model:
        recent_usage = [u for u in recent_usage if u.get('model') == model]
    
    # Calculate costs by model
    cost_by_model = {}
    cost_by_feature = {}
    
    for usage in recent_usage:
        model_name = usage.get('model', 'unknown')
        feature = usage.get('feature', 'chat')
        tokens = usage.get('tokens_used', {}).get('total', 0)
        
        # Estimate cost based on model
        pricing = {
            'gpt-4': 0.03,
            'gpt-4-turbo': 0.01,
            'gpt-3.5-turbo': 0.0005,
            'claude-3-opus': 0.015,
            'claude-3-sonnet': 0.003,
        }
        price_per_1k = pricing.get(model_name, 0.002)
        cost = (tokens / 1000) * price_per_1k
        
        if model_name not in cost_by_model:
            cost_by_model[model_name] = {"tokens": 0, "cost": 0}
        cost_by_model[model_name]["tokens"] += tokens
        cost_by_model[model_name]["cost"] += cost
        
        if feature not in cost_by_feature:
            cost_by_feature[feature] = {"tokens": 0, "cost": 0}
        cost_by_feature[feature]["tokens"] += tokens
        cost_by_feature[feature]["cost"] += cost
    
    total_cost = sum(m["cost"] for m in cost_by_model.values())
    
    return JSONResponse({
        "period_days": days,
        "total_cost_usd": round(total_cost, 4),
        "by_model": {
            k: {"tokens": v["tokens"], "cost_usd": round(v["cost"], 4)}
            for k, v in cost_by_model.items()
        },
        "by_feature": {
            k: {"tokens": v["tokens"], "cost_usd": round(v["cost"], 4)}
            for k, v in cost_by_feature.items()
        }
    })


@router.get("/export")
async def export_analytics(
    format: str = "json",
    days: int = 30
):
    """
    Export analytics data.
    
    Args:
        format: Export format (json, csv)
        days: Number of days to include
        
    Returns:
        Exported data
    """
    # Collect all analytics
    export_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "period_days": days,
        "usage": analytics_store["usage"][-1000:],  # Last 1000 entries
        "questions": analytics_store["questions"][-500:],
        "audit_logs": analytics_store["audit_logs"][-500:]
    }
    
    if format == "csv":
        # Placeholder for CSV export
        return JSONResponse({
            "status": "success",
            "format": "csv",
            "message": "CSV export would be generated here",
            "data_preview": export_data
        })
    
    return JSONResponse({
        "status": "success",
        "format": "json",
        "data": export_data
    })
