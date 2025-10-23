from PyPDF2 import PdfReader  # type: ignore[import]
import tempfile
import re
from modules.ocr import extract_text_from_scanned_pdf

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from uploaded PDF (text-based or scanned) with improved cleaning
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())
        temp_pdf_path = temp_pdf.name

    text = ""
    try:
        reader = PdfReader(temp_pdf_path)
        page_texts = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                page_texts.append(page_text)
        
        # Check if we got meaningful text (not just whitespace/garbage)
        text = "\n".join(page_texts)
        if not text.strip() or len(text.strip()) < 50:  # Threshold for meaningful content
            print("🔍 No digital text detected, using OCR...")
            text = extract_text_from_scanned_pdf(temp_pdf_path)

    except Exception as e:
        print(f"⚠️ Error reading PDF — switching to OCR: {e}")
        text = extract_text_from_scanned_pdf(temp_pdf_path)

    # Clean and normalize the text
    return clean_extracted_text(text)


def clean_extracted_text(text):
    """
    Clean and normalize extracted text to remove distortions
    """
    if not text:
        return ""
    
    # Remove null bytes and other control characters
    text = text.replace('\x00', '')
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Fix common PDF extraction issues
    # Remove excessive whitespace while preserving paragraph breaks
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double newline
    
    # Remove hyphenation at line breaks
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Fix broken words (common in PDFs with encoding issues)
    # Example: "e x a m p l e" -> "example"
    text = re.sub(r'(\w)\s+(?=\w\s+\w)', r'\1', text)
    
    # Normalize unicode characters
    text = text.encode('utf-8', errors='ignore').decode('utf-8')
    
    # Remove page numbers and headers/footers (common patterns)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Skip lines that are just numbers (page numbers)
        if line and not (line.isdigit() and len(line) <= 3):
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Final cleanup: normalize spaces
    text = ' '.join(text.split())
    
    return text.strip()