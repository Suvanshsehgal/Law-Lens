from fastapi import APIRouter
from services.pdf_service import kw_model

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "⚖️ Law-Lens API is running!"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "LawLens backend running",
        "models_loaded": kw_model is not None
    }
