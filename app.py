try:
    import nest_asyncio  # type: ignore[import]
    nest_asyncio.apply()
except Exception:
    pass

import streamlit as st  # type: ignore[import]
from modules.pdf_processor import extract_text_from_pdf
from modules.keyword import load_legalbert_model, extract_legal_keywords
from modules.keyword_meaning import get_keywords_meaning_smart  # ✅ For keyword meanings
from modules.vector_store import create_faiss_index  # ✅ NEW for FAISS index creation
from modules.chatbot import answer_query_with_context  # ✅ NEW for Groq chatbot

# --- Page Config ---
st.set_page_config(page_title="Legal Document Chatbot", layout="wide")

# --- Load LegalBERT Model Once ---
@st.cache_resource
def get_kw_model(): 
    return load_legalbert_model()

kw_model = get_kw_model()

# --- Title & Instructions ---
st.title("📄 Legal Document Chatbot")
st.write("""
Upload a legal PDF document — text-based or scanned — to extract its contents, 
identify key legal terms using **LegalBERT**, understand their meanings through **Llama (Groq API)**, 
and ask questions directly about the document using **FAISS + Llama Chat**.
""")

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

            # --- Keyword Extraction ---
            with st.spinner("🧠 Extracting legal keywords using LegalBERT..."):
                keywords = extract_legal_keywords(text, kw_model, top_n=15)

            st.subheader("🔑 Extracted Legal Keywords")
            if keywords:
                st.write(", ".join(keywords))

                # --- Get Keyword Meanings via Groq API ---
                st.subheader("📚 Keyword Meanings (via Llama Model)")
                with st.spinner("💬 Fetching keyword meanings intelligently..."):
                    meanings = get_keywords_meaning_smart(keywords)

                # --- Display Results (only show ones needing explanation) ---
                if isinstance(meanings, dict):
                    for kw, meaning in meanings.items():
                        if not (isinstance(meaning, str) and meaning.lower() == "no explanation needed"):
                            st.markdown(f"**{kw}:** {meaning}")
                else:
                    st.warning("Unexpected response from Groq API. Please check your API setup.")
            else:
                st.info("No keywords found. Try uploading a longer or clearer legal document.")

            # --- ✅ NEW: Create FAISS Index ---
            st.subheader("💾 Indexing Document for Chatbot")
            with st.spinner("Creating FAISS vector index..."):
                index, chunks = create_faiss_index(text)
            st.success("📂 Document successfully indexed for retrieval!")

            # --- ✅ NEW: Chatbot Section ---
            st.subheader("🤖 Ask Questions About the Document")
            user_query = st.text_input("Enter your legal question:")

            if user_query:
                with st.spinner("💭 Thinking..."):
                    answer = answer_query_with_context(user_query, index, chunks)
                    st.markdown(f"**Answer:** {answer}")

            # --- Download Extracted Text ---
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
