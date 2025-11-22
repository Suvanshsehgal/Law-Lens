import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

try:
    import nest_asyncio  # type: ignore[import]
    nest_asyncio.apply()
except Exception:
    pass

import streamlit as st
import tempfile
import os

from modules.pdf_processor import extract_text_from_pdf, prepare_paragraph_importance_data
from modules.keyword import load_legalbert_model, extract_legal_keywords
from modules.keyword_meaning import get_keywords_meaning_smart
from modules.vector_store import create_faiss_index
from modules.chatbot import answer_query_with_context
from modules.highlight_pdf import highlight_paragraphs_in_original_pdf

# --- Page Config ---
st.set_page_config(page_title="⚖️ Law-Lens", layout="wide")

# --- Load LegalBERT Model Once ---
@st.cache_resource
def get_kw_model(): 
    return load_legalbert_model()

kw_model = get_kw_model()

# --- Title ---
st.title("⚖️ Law-Lens: Legal Document Analysis")
st.write("""
Upload a legal PDF document to extract text, identify legal terms, 
highlight important clauses inside the original PDF,  
and ask questions directly about the document.
""")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# --- Processing ---
if uploaded_file:

    # Save original PDF temporarily (needed for highlighting)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        original_pdf_path = tmp.name

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -------- TEXT EXTRACTION --------
    with st.spinner("🔍 Extracting text from PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    # -------- KEYWORD EXTRACTION --------
    with st.spinner("🧠 Identifying legal keywords..."):
        keywords = extract_legal_keywords(text, kw_model, top_n=15)

    # -------- KEYWORD MEANINGS --------
    with st.spinner("💬 Generating keyword meanings..."):
        meanings = get_keywords_meaning_smart(keywords)

    # -------- PARAGRAPH IMPORTANCE SCORING --------
    with st.spinner("📑 Detecting important paragraphs..."):
        # DO NOT pass extra arguments — your function expects only (text, keywords)
        paragraph_data = prepare_paragraph_importance_data(text, keywords)

    # -------- CHAT INDEXING --------
    with st.spinner("💾 Preparing chatbot search index..."):
        index, chunks = create_faiss_index(text)

    st.success("✅ Document processed successfully!")
    st.divider()

    # -------- GENERATE HIGHLIGHTED ORIGINAL PDF --------
    with st.spinner("📄 Creating highlighted PDF (original formatting preserved)..."):
        highlighted_pdf_path = highlight_paragraphs_in_original_pdf(
            original_pdf_path,
            paragraph_data
        )

    # -------- DOWNLOAD HIGHLIGHTED PDF --------
    with open(highlighted_pdf_path, "rb") as f:
        st.download_button(
            label="⬇️ Download Highlighted Original PDF",
            data=f,
            file_name="Highlighted_Legal_Document.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.divider()

    # =======================================================
    #               KEYWORDS (LEFT) + CHATBOT (RIGHT)
    # =======================================================
    col1, col2 = st.columns([1, 1])

    # -------- KEYWORDS PANEL --------
    with col1:
        st.subheader("📚 Key Legal Terms")

        keyword_download_list = []

        with st.container(border=True, height=500):
            if keywords and isinstance(meanings, dict):
                explained_count = 0

                for kw, meaning in meanings.items():
                    keyword_download_list.append(f"{kw}: {meaning}")

                    if isinstance(meaning, str) and meaning.lower() != "no explanation needed":
                        with st.expander(f"🔹 {kw}"):
                            st.write(meaning)
                        explained_count += 1

                if explained_count == 0:
                    st.info("All extracted keywords are common English words—no special legal meaning.")
            else:
                st.info("No legal keywords identified.")

            if keyword_download_list:
                st.download_button(
                    label="⬇️ Download All Keywords + Meanings",
                    data="\n\n".join(keyword_download_list),
                    file_name=f"{uploaded_file.name}_keywords.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    # -------- CHATBOT PANEL --------
    with col2:
        st.subheader("🤖 Chat with Document")

        chat_container = st.container(height=400, border=True)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_query = st.text_input("Ask a question about this document:", key="chat_input_box")

        ask_col, clear_col = st.columns(2)
        ask_btn = ask_col.button("Ask", use_container_width=True, type="primary")
        clear_btn = clear_col.button("Clear Chat", use_container_width=True)

        if clear_btn:
            st.session_state.messages = []
            st.rerun()

        if ask_btn:
            if user_query.strip():
                st.session_state.messages.append({"role": "user", "content": user_query})

                with st.spinner("💭 Thinking..."):
                    answer = answer_query_with_context(user_query, index, chunks)

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.warning("Please enter a valid question.")

    st.divider()

    # -------- DOWNLOAD RAW EXTRACTED TEXT --------
    st.download_button(
        label="⬇️ Download Extracted Raw Text",
        data=text,
        file_name=f"{uploaded_file.name}_extracted_text.txt",
        mime="text/plain",
        use_container_width=True
    )

else:
    st.info("👆 Upload a PDF to begin analysis.")
