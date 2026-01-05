import os
import uuid
import tempfile
from typing import Dict, Any

import numpy as np

from modules.pdf_processor import extract_text_from_pdf, split_into_paragraphs
from modules.keyword import load_legalbert_model, extract_legal_keywords
from modules.keyword_meaning import get_keywords_meaning_smart
from modules.vector_store import create_faiss_index
from modules.highlight_pdf import highlight_paragraphs_in_original_pdf
from modules.case_law_fetcher import get_cases_for_keywords
from modules.semantic_importance import analyze_paragraphs_hybrid
from modules.utils.text_cleaner import normalize_keyword   # ✅ IMPORTANT


# -------------------------------
# JSON SAFE CONVERTER (CRITICAL)
# -------------------------------
def to_python(obj):
    """Recursively convert NumPy / non-JSON types to native Python"""
    if isinstance(obj, dict):
        return {k: to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_python(v) for v in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    else:
        return obj


# -------------------------------
# MODEL INITIALIZATION
# -------------------------------
kw_model = None

def initialize_models():
    """Load heavy models once at startup"""
    global kw_model
    if kw_model is None:
        kw_model = load_legalbert_model()


# -------------------------------
# GLOBAL DOCUMENT STORE
# -------------------------------
DOCUMENT_STORE: Dict[str, Dict[str, Any]] = {}


# -------------------------------
# MAIN PDF PROCESSING SERVICE
# -------------------------------
def process_pdf_service(pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
    try:
        initialize_models()

        session_id = str(uuid.uuid4())

        # Save PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            pdf_path = tmp.name

        # Mock object for existing extractor
        class MockUploadedFile:
            def __init__(self, path, name):
                self.path = path
                self.name = name

            def read(self):
                with open(self.path, "rb") as f:
                    return f.read()

        mock_file = MockUploadedFile(pdf_path, filename)

        # -------- PIPELINE --------
        text = extract_text_from_pdf(mock_file)

        if not text or not text.strip():
            raise ValueError("No extractable text found in PDF")

        # -------------------------------
        # KEYWORDS + CLEANING
        # -------------------------------
        raw_keywords = extract_legal_keywords(text, kw_model, top_n=15)

        cleaned_keywords = []
        for kw in raw_keywords:
            clean = normalize_keyword(kw)
            if clean and clean not in cleaned_keywords:
                cleaned_keywords.append(clean)

        # -------------------------------
        # MEANINGS
        # -------------------------------
        meanings = get_keywords_meaning_smart(cleaned_keywords)

        # -------------------------------
        # CASE LAWS (ONLY CLEAN KEYWORDS)
        # -------------------------------
        case_laws = {}
        if cleaned_keywords:
            laws = get_cases_for_keywords(cleaned_keywords[:5])
            case_laws = {k: v[0] for k, v in laws.items()}   # remove UI text

        # -------------------------------
        # PARAGRAPH & IMPORTANCE
        # -------------------------------
        paragraphs = split_into_paragraphs(text)
        paragraph_data = analyze_paragraphs_hybrid(paragraphs)

        index, chunks = create_faiss_index(text)

        # Highlighting (fail-safe)
        try:
            highlighted_pdf_path = highlight_paragraphs_in_original_pdf(
                pdf_path, paragraph_data
            )
        except Exception:
            highlighted_pdf_path = None

        # -------------------------------
        # METRICS
        # -------------------------------
        high_count = sum(1 for p in paragraph_data if p.get("importance") == "high")
        medium_count = sum(1 for p in paragraph_data if p.get("importance") == "medium")
        low_count = sum(1 for p in paragraph_data if p.get("importance") == "low")

        metrics = {
            "high_priority": high_count,
            "medium_priority": medium_count,
            "low_priority": low_count,
            "total_paragraphs": len(paragraph_data),
            "total_keywords": len(cleaned_keywords),
        }

        # -------------------------------
        # STORE SESSION
        # -------------------------------
        DOCUMENT_STORE[session_id] = {
            "text": text,
            "keywords": cleaned_keywords,
            "meanings": meanings,
            "case_laws": case_laws,
            "paragraph_data": paragraph_data,
            "index": index,
            "chunks": chunks,
            "original_pdf_path": pdf_path,
            "highlighted_pdf_path": highlighted_pdf_path,
            "filename": filename,
            "metrics": metrics,
        }

        # -------------------------------
        # FINAL RESPONSE
        # -------------------------------
        return to_python({
            "session_id": session_id,
            "message": "Document processed successfully",
            "keywords": cleaned_keywords,
            "keyword_meanings": meanings,
            "case_laws": case_laws,
            "paragraph_data": paragraph_data,
            "metrics": metrics,
        })

    except Exception as e:
        try:
            if "pdf_path" in locals():
                os.unlink(pdf_path)
        except:
            pass
        raise Exception(f"Error processing PDF: {str(e)}")


# -------------------------------
# SESSION HELPERS
# -------------------------------
def get_session_data(session_id: str) -> Dict[str, Any]:
    if session_id not in DOCUMENT_STORE:
        raise ValueError("Session not found")

    return to_python({
        "session_id": session_id,
        **DOCUMENT_STORE[session_id]
    })


def delete_session(session_id: str) -> bool:
    if session_id not in DOCUMENT_STORE:
        return False

    data = DOCUMENT_STORE[session_id]

    for path in ["original_pdf_path", "highlighted_pdf_path"]:
        try:
            if data.get(path):
                os.unlink(data[path])
        except:
            pass

    del DOCUMENT_STORE[session_id]
    return True


def get_highlighted_pdf_path(session_id: str) -> str:
    if session_id not in DOCUMENT_STORE:
        raise ValueError("Session not found")
    return DOCUMENT_STORE[session_id]["highlighted_pdf_path"]


def get_keywords_text(session_id: str) -> str:
    if session_id not in DOCUMENT_STORE:
        raise ValueError("Session not found")

    data = DOCUMENT_STORE[session_id]
    return "\n\n".join(
        f"{kw}: {data['meanings'].get(kw, 'No meaning available')}"
        for kw in data["keywords"]
    )


def get_raw_text(session_id: str) -> str:
    if session_id not in DOCUMENT_STORE:
        raise ValueError("Session not found")
    return DOCUMENT_STORE[session_id]["text"]
