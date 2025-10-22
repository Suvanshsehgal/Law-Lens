import streamlit as st
from modules.pdf_processor import extract_text_from_pdf

# --- Page Config ---
st.set_page_config(page_title="Legal Document Chatbot", layout="wide")

# --- Title & Instructions ---
st.title("📄 Legal Document Chatbot")
st.write("Upload any legal PDF document — whether text-based or scanned — to extract its contents using OCR.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# --- Process File ---
if uploaded_file:
    with st.spinner("🔍 Extracting text from PDF..."):
        try:
            text = extract_text_from_pdf(uploaded_file)
            st.success("✅ Text extraction complete!")
            
            # --- Preview Section ---
            st.subheader("📘 Extracted Text Preview")
            st.text_area(
                "Preview (first 1000 characters):",
                text[:1000] if text else "No text extracted.",
                height=250
            )
            
            # --- Option to download extracted text ---
            st.download_button(
                label="⬇️ Download Full Extracted Text",
                data=text,
                file_name="extracted_text.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ Error processing PDF: {e}")
else:
    st.info("👆 Please upload a PDF file to begin.")
