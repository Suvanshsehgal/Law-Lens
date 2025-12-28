from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from routes import chat, pdf, health
from services.pdf_service import initialize_models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="⚖️ Law-Lens API",
    description="AI-powered Legal Document Analysis Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to load models
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Law-Lens API...")
    logger.info("Loading AI models...")
    initialize_models()
    logger.info("Models loaded successfully!")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(pdf.router, prefix="/pdf", tags=["PDF"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
