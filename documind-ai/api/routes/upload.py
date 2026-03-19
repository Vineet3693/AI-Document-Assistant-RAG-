"""
Upload Routes
Handles document upload, batch upload, and import from external sources.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """
    Upload a single document.
    
    Args:
        file: Document file (PDF, DOCX, TXT, etc.)
        doc_type: Optional document type classification
        tags: Optional comma-separated tags
        
    Returns:
        Document ID and processing status
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.csv', '.xlsx', '.xls', '.pptx', '.ppt'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed: {allowed_extensions}"
        )
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    
    # Create upload directory if not exists
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, f"{doc_id}{file_ext}")
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Return success response
        return JSONResponse({
            "status": "success",
            "document_id": doc_id,
            "filename": file.filename,
            "file_type": file_ext,
            "file_size": len(content),
            "upload_time": datetime.utcnow().isoformat(),
            "processing_status": "queued",
            "message": "Document uploaded successfully. Processing will begin shortly."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/batch")
async def upload_batch(
    files: List[UploadFile] = File(...),
    doc_type: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """
    Upload multiple documents at once.
    
    Args:
        files: List of document files
        doc_type: Optional document type for all files
        tags: Optional tags for all files
        
    Returns:
        List of document IDs and statuses
    """
    results = []
    failed = []
    
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        doc_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        try:
            # Validate
            allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.csv', '.xlsx', '.xls', '.pptx', '.ppt'}
            if file_ext not in allowed_extensions:
                failed.append({
                    "filename": file.filename,
                    "error": f"Invalid file type: {file_ext}"
                })
                continue
            
            # Save file
            file_path = os.path.join(upload_dir, f"{doc_id}{file_ext}")
            
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            results.append({
                "document_id": doc_id,
                "filename": file.filename,
                "file_type": file_ext,
                "file_size": len(content),
                "status": "success"
            })
            
        except Exception as e:
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return JSONResponse({
        "status": "completed",
        "uploaded": len(results),
        "failed": len(failed),
        "documents": results,
        "failures": failed,
        "upload_time": datetime.utcnow().isoformat()
    })


@router.post("/url")
async def upload_from_url(
    url: str = Form(...),
    doc_type: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """
    Upload document from a URL.
    
    Args:
        url: URL to download document from
        doc_type: Optional document type
        tags: Optional tags
        
    Returns:
        Document ID and status
    """
    import httpx
    
    doc_id = str(uuid.uuid4())
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
        
        # Determine file extension from URL or content type
        content_type = response.headers.get('content-type', '')
        file_ext = '.bin'
        
        if 'pdf' in content_type:
            file_ext = '.pdf'
        elif 'word' in content_type or 'docx' in content_type:
            file_ext = '.docx'
        elif 'text' in content_type:
            file_ext = '.txt'
        
        # Save file
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{doc_id}{file_ext}")
        
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        return JSONResponse({
            "status": "success",
            "document_id": doc_id,
            "source_url": url,
            "file_type": file_ext,
            "file_size": len(response.content),
            "upload_time": datetime.utcnow().isoformat(),
            "processing_status": "queued"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL upload failed: {str(e)}")


@router.post("/drive")
async def upload_from_google_drive(
    drive_file_id: str = Form(...),
    access_token: Optional[str] = Form(None)
):
    """
    Import document from Google Drive.
    
    Args:
        drive_file_id: Google Drive file ID
        access_token: OAuth access token (or use configured credentials)
        
    Returns:
        Document ID and status
    """
    # This is a placeholder - full implementation would use Google Drive API
    doc_id = str(uuid.uuid4())
    
    return JSONResponse({
        "status": "success",
        "document_id": doc_id,
        "source": "google_drive",
        "drive_file_id": drive_file_id,
        "upload_time": datetime.utcnow().isoformat(),
        "message": "Google Drive integration requires OAuth setup"
    })


@router.post("/dropbox")
async def upload_from_dropbox(
    dropbox_path: str = Form(...),
    access_token: Optional[str] = Form(None)
):
    """
    Import document from Dropbox.
    
    Args:
        dropbox_path: Path to file in Dropbox
        access_token: Dropbox access token
        
    Returns:
        Document ID and status
    """
    # Placeholder for Dropbox integration
    doc_id = str(uuid.uuid4())
    
    return JSONResponse({
        "status": "success",
        "document_id": doc_id,
        "source": "dropbox",
        "dropbox_path": dropbox_path,
        "upload_time": datetime.utcnow().isoformat(),
        "message": "Dropbox integration requires OAuth setup"
    })
