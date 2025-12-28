from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.chat_service import chat_with_document

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    answer: str
    session_id: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the uploaded document"""
    try:
        answer = chat_with_document(request.session_id, request.query)
        
        return ChatResponse(
            answer=answer,
            session_id=request.session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
