#!/usr/bin/env python3
"""
Law-Lens FastAPI Server Launcher (Routes/Services Architecture)
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Launch the FastAPI server"""
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with the following variables:")
        print("GROQ_API_KEY=your_groq_api_key")
        print("TESSERACT_PATH=path_to_tesseract")
        print("POPPLER_BIN_PATH=path_to_poppler")
        print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        sys.exit(1)
    
    print("🚀 Starting Law-Lens API Server...")
    print("📁 Using Routes/Services Architecture")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend: Open frontend.html in your browser")
    print("🔄 Health Check: http://localhost:8000/health")
    print()
    print("📋 Available Endpoints:")
    print("  POST /pdf/upload - Upload and analyze PDF")
    print("  POST /chat/ - Chat with document")
    print("  GET  /pdf/session/{id} - Get session data")
    print("  GET  /pdf/download/highlighted/{id} - Download highlighted PDF")
    print("  GET  /pdf/download/keywords/{id} - Download keywords")
    print("  GET  /pdf/download/text/{id} - Download raw text")
    print("  DELETE /pdf/session/{id} - Delete session")
    print()
    
    # Launch server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

if __name__ == "__main__":
    main()