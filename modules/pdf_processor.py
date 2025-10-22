from PyPDF2 import PdfReader
import tempfile
from modules.ocr import extract_text_from_scanned_pdf

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from uploaded PDF (text-based or scanned)
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())
        temp_pdf_path = temp_pdf.name

    text = ""
    try:
        reader = PdfReader(temp_pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        if not text.strip():
            print("🔍 No digital text detected, using OCR...")
            text = extract_text_from_scanned_pdf(temp_pdf_path)

    except Exception as e:
        print(f"⚠️ Error reading PDF — switching to OCR: {e}")
        text = extract_text_from_scanned_pdf(temp_pdf_path)

    return text.replace("\n", " ").replace("\r", " ").strip()
