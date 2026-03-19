"""
Export Routes
Handles exporting answers, summaries, and reports in various formats.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from pydantic import BaseModel
import os
from datetime import datetime

router = APIRouter(prefix="/export", tags=["Export"])


class ExportRequest(BaseModel):
    content_type: str  # 'chat', 'summary', 'comparison', 'analysis'
    format: str  # 'pdf', 'word', 'excel', 'html'
    data: dict
    include_citations: bool = True
    include_metadata: bool = True


@router.post("/pdf")
async def export_pdf(request: ExportRequest):
    """
    Export content as PDF.
    
    Args:
        content_type: Type of content (chat, summary, comparison, analysis)
        format: Should be 'pdf'
        data: Content to export
        include_citations: Include citations in export
        include_metadata: Include metadata
        
    Returns:
        PDF file or download link
    """
    try:
        from exports.pdf_exporter import PDFExporter
        
        exporter = PDFExporter()
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"documind_export_{timestamp}.pdf"
        filepath = f"data/exports/{filename}"
        
        # Ensure directory exists
        os.makedirs("data/exports", exist_ok=True)
        
        # Generate PDF
        success = exporter.generate(
            filepath=filepath,
            content_type=request.content_type,
            data=request.data,
            include_citations=request.include_citations,
            include_metadata=request.include_metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
        # Return file
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf'
        )
        
    except ImportError:
        # Fallback if pdf exporter not available
        return JSONResponse({
            "status": "success",
            "message": "PDF export requested (placeholder - install reportlab for full functionality)",
            "content_type": request.content_type,
            "data_size": len(str(request.data))
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/word")
async def export_word(request: ExportRequest):
    """
    Export content as Word document.
    
    Args:
        content_type: Type of content
        format: Should be 'word'
        data: Content to export
        
    Returns:
        Word document file
    """
    try:
        from exports.word_exporter import WordExporter
        
        exporter = WordExporter()
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"documind_export_{timestamp}.docx"
        filepath = f"data/exports/{filename}"
        
        os.makedirs("data/exports", exist_ok=True)
        
        success = exporter.generate(
            filepath=filepath,
            content_type=request.content_type,
            data=request.data,
            include_citations=request.include_citations
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Word export failed")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except ImportError:
        return JSONResponse({
            "status": "success",
            "message": "Word export requested (placeholder - install python-docx for full functionality)",
            "content_type": request.content_type
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/excel")
async def export_excel(request: ExportRequest):
    """
    Export content as Excel spreadsheet.
    
    Args:
        content_type: Type of content (typically 'comparison' or 'extracted_data')
        format: Should be 'excel'
        data: Content to export
        
    Returns:
        Excel file
    """
    try:
        from exports.excel_exporter import ExcelExporter
        
        exporter = ExcelExporter()
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"documind_export_{timestamp}.xlsx"
        filepath = f"data/exports/{filename}"
        
        os.makedirs("data/exports", exist_ok=True)
        
        success = exporter.generate(
            filepath=filepath,
            content_type=request.content_type,
            data=request.data
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Excel export failed")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except ImportError:
        return JSONResponse({
            "status": "success",
            "message": "Excel export requested (placeholder - install openpyxl for full functionality)",
            "content_type": request.content_type
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/html")
async def export_html(request: ExportRequest):
    """
    Export content as HTML.
    
    Args:
        content_type: Type of content
        format: Should be 'html'
        data: Content to export
        
    Returns:
        HTML file
    """
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"documind_export_{timestamp}.html"
        filepath = f"data/exports/{filename}"
        
        os.makedirs("data/exports", exist_ok=True)
        
        # Simple HTML template
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DocuMind AI Export</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        .metadata {{ color: #7f8c8d; font-size: 0.9em; }}
        .content {{ margin: 20px 0; }}
        .citation {{ background: #ecf0f1; padding: 10px; margin: 10px 0; border-left: 3px solid #3498db; }}
    </style>
</head>
<body>
    <h1>DocuMind AI Export</h1>
    <p class="metadata">Generated: {datetime.utcnow().isoformat()}</p>
    <p class="metadata">Type: {request.content_type}</p>
    <div class="content">
        <pre>{str(request.data)}</pre>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='text/html'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_export_history(limit: int = 20):
    """
    Get recent export history.
    
    Args:
        limit: Maximum entries to return
        
    Returns:
        List of recent exports
    """
    exports_dir = "data/exports"
    
    if not os.path.exists(exports_dir):
        return JSONResponse({
            "exports": [],
            "total": 0
        })
    
    # List files
    files = os.listdir(exports_dir)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(exports_dir, x)), reverse=True)
    
    exports = []
    for filename in files[:limit]:
        filepath = os.path.join(exports_dir, filename)
        stat = os.stat(filepath)
        
        file_type = "unknown"
        if filename.endswith('.pdf'):
            file_type = "pdf"
        elif filename.endswith('.docx'):
            file_type = "word"
        elif filename.endswith('.xlsx'):
            file_type = "excel"
        elif filename.endswith('.html'):
            file_type = "html"
        
        exports.append({
            "filename": filename,
            "type": file_type,
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
        })
    
    return JSONResponse({
        "exports": exports,
        "total": len(exports)
    })


@router.delete("/{filename}")
async def delete_export(filename: str):
    """
    Delete an exported file.
    
    Args:
        filename: Name of file to delete
        
    Returns:
        Deletion confirmation
    """
    filepath = f"data/exports/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Export file not found")
    
    try:
        os.remove(filepath)
        return JSONResponse({
            "status": "success",
            "message": f"Export '{filename}' deleted successfully"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
