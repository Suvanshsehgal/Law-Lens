import re
from PyPDF2 import PdfReader
import tempfile
from modules.ocr import extract_text_from_scanned_pdf


# ============================================================
#                PDF TEXT EXTRACTION (UNCHANGED)
# ============================================================

def extract_text_from_pdf(uploaded_file):
    """Extract PDF text; fallback to OCR if needed."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())
        temp_pdf_path = temp_pdf.name

    try:
        reader = PdfReader(temp_pdf_path)
        page_texts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                page_texts.append(page_text)

        text = "\n".join(page_texts)

        # Fallback to OCR if text is empty or too short
        if not text.strip() or len(text.strip()) < 50:
            text = extract_text_from_scanned_pdf(temp_pdf_path)

    except Exception:
        text = extract_text_from_scanned_pdf(temp_pdf_path)

    return clean_extracted_text(text)


def clean_extracted_text(text):
    """Clean extracted PDF text before analysis."""
    if not text:
        return ""

    text = text.replace('\x00', '')
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    text = re.sub(r'\n+', '\n', text)

    # Remove page numbers and isolated digits
    lines = []
    for line in text.split("\n"):
        if not (line.strip().isdigit() and len(line.strip()) <= 3):
            lines.append(line.strip())

    text = "\n".join(lines)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ============================================================
#                   PARAGRAPH PROCESSING
# ============================================================

def split_into_paragraphs(text):
    """
    Split text into meaningful legal paragraphs.
    Avoid splitting on '1.', '2.', '3.' etc.
    """
    # First split on double newlines
    candidates = re.split(r"\n\s*\n", text)

    # If still too long, split by period but only when followed by uppercase letter
    final_paragraphs = []
    for chunk in candidates:
        parts = re.split(r'\.\s+(?=[A-Z])', chunk)
        for p in parts:
            p = p.strip()
            if len(p) > 40:  # ignore noise
                final_paragraphs.append(p)

    return final_paragraphs


def compute_keyword_density(paragraph, keywords):
    """Count keyword occurrences using whole-word regex search."""
    if not paragraph or not keywords:
        return 0

    density = 0

    for kw in keywords:
        if not kw:
            continue

        pattern = r'\b' + re.escape(kw) + r'\b'
        hits = len(re.findall(pattern, paragraph, flags=re.IGNORECASE))
        density += hits

    return density


def classify_importance_by_density(density, high_threshold=2):
    """Classify paragraph importance based on keyword density."""
    return "high" if density >= high_threshold else "low"


def prepare_paragraph_importance_data(text, keywords, high_threshold=2):
    """
    Returns list of:
    {
        "paragraph": "...",
        "density": int,
        "importance": "high" or "low"
    }
    """
    paragraphs = split_into_paragraphs(text)
    results = []

    for para in paragraphs:
        density = compute_keyword_density(para, keywords)
        importance = classify_importance_by_density(density, high_threshold)

        results.append({
            "paragraph": para,
            "density": density,
            "importance": importance
        })

    return results
