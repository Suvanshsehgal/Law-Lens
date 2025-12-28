from modules.chatbot import answer_query_with_context
from services.pdf_service import DOCUMENT_STORE

def chat_with_document(session_id: str, query: str) -> str:
    """Chat with a specific document session"""
    if session_id not in DOCUMENT_STORE:
        return "Session not found. Please upload a PDF first."
    
    session_data = DOCUMENT_STORE[session_id]
    index = session_data["index"]
    chunks = session_data["chunks"]
    
    try:
        answer = answer_query_with_context(query, index, chunks)
        return answer
    except Exception as e:
        return f"Error processing query: {str(e)}"
