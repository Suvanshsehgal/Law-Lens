from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os

from services.pdf_service import (
    process_pdf_service, 
    get_session_data, 
    delete_session,
    get_highlighted_pdf_path,
    get_keywords_text,
    get_raw_text
)

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and analyze a PDF document"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Process PDF
        result = process_pdf_service(content, file.filename)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session data"""
    try:
        return get_session_data(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def delete_session_endpoint(session_id: str):
    """Delete session and cleanup files"""
    try:
        success = delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/highlighted/{session_id}")
async def download_highlighted_pdf(session_id: str):
    """Download highlighted PDF"""
    try:
        pdf_path = get_highlighted_pdf_path(session_id)
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="Highlighted PDF not found")
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"highlighted_document.pdf"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/keywords/{session_id}")
async def download_keywords(session_id: str):
    """Download keywords and meanings as text file"""
    try:
        keywords_text = get_keywords_text(session_id)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", encoding='utf-8') as tmp_file:
            tmp_file.write(keywords_text)
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            tmp_file_path,
            media_type="text/plain",
            filename="keywords.txt"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/text/{session_id}")
async def download_raw_text(session_id: str):
    """Download raw extracted text"""
    try:
        raw_text = get_raw_text(session_id)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", encoding='utf-8') as tmp_file:
            tmp_file.write(raw_text)
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            tmp_file_path,
            media_type="text/plain",
            filename="extracted_text.txt"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
