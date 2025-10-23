try:
    import nest_asyncio  # type: ignore[import]
    nest_asyncio.apply()
except Exception:
    pass

import streamlit as st  # type: ignore[import]
from modules.pdf_processor import extract_text_from_pdf
from modules.keyword import load_legalbert_model, extract_legal_keywords

# --- Page Config ---
st.set_page_config(page_title="Legal Document Chatbot", layout="wide")

# --- Load LegalBERT Model Once ---
@st.cache_resource
def get_kw_model(): 
    return load_legalbert_model()

kw_model = get_kw_model()

# --- Title & Instructions ---
st.title("📄 Legal Document Chatbot")
st.write("Upload a legal PDF document — text-based or scanned — to extract contents and identify key legal terms using LegalBERT.")

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

            # --- Keyword Extraction on Full Text ---
            with st.spinner("🧠 Extracting legal keywords using LegalBERT..."):
                keywords = extract_legal_keywords(text, kw_model, top_n=15)

            st.subheader("🔑 Extracted Legal Keywords")
            if keywords:
                st.write(", ".join(keywords))
            else:
                st.info("No keywords found. Try with a longer or clearer document.")

            # --- Download Full Extracted Text ---
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
