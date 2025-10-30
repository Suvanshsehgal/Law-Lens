try:
    import nest_asyncio  # type: ignore[import]
    nest_asyncio.apply()
except Exception:
    pass

import streamlit as st  # type: ignore[import]
from modules.pdf_processor import extract_text_from_pdf
from modules.keyword import load_legalbert_model, extract_legal_keywords
from modules.keyword_meaning import get_keywords_meaning_smart
from modules.vector_store import create_faiss_index
from modules.chatbot import answer_query_with_context

# --- Page Config ---
st.set_page_config(page_title="⚖️ Law-Lens", layout="wide")

# --- Load LegalBERT Model Once ---
@st.cache_resource
def get_kw_model(): 
    """Load and cache the LegalBERT model."""
    return load_legalbert_model()

kw_model = get_kw_model()

# --- Title & Instructions ---
st.title("⚖️ Law-Lens: Legal Document Analysis")
st.write("""
Upload a legal PDF document to identify key terms, understand their meanings, 
and ask questions directly about the document's content.
""")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# --- Process File ---
if uploaded_file:
    
    # --- Initialize Chat History in Session State ---
    # This ensures the chat history persists across reruns
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --- Run all processing with spinners ---
    with st.spinner("🔍 Extracting text from PDF..."):
        try:
            text = extract_text_from_pdf(uploaded_file)
        except Exception as e:
            st.error(f"❌ Error extracting text: {e}")
            st.stop() # Stop execution if text extraction fails

    with st.spinner("🧠 Identifying legal keywords..."):
        keywords = extract_legal_keywords(text, kw_model, top_n=15)

    with st.spinner("💬 Fetching keyword meanings..."):
        meanings = get_keywords_meaning_smart(keywords)

    with st.spinner("💾 Indexing document for chat..."):
        index, chunks = create_faiss_index(text)

    st.success("✅ Document processed! Ready for review and chat.")
    st.divider()

    # --- Create the results panel with Columns (Grid) ---
    col1, col2 = st.columns([1, 1]) # Create two equal-width columns

    # --- Column 1: Keyword Meanings (Left) ---
    with col1:
        st.subheader("📚 Key Legal Terminology")
        
        # Create a container with a border and fixed height for keywords
        with st.container(border=True, height=500): 
            
            # --- MODIFICATION: Initialize download list outside of 'if' ---
            keyword_download_list = [] # List to hold ALL data for download

            if keywords:
                if isinstance(meanings, dict):
                    explained_count = 0
                    
                    for kw, meaning in meanings.items():
                        # --- MODIFICATION: Add ALL keywords to the download list ---
                        keyword_download_list.append(f"{kw}: {meaning}")
                        
                        # --- UI Logic remains filtered ---
                        if not (isinstance(meaning, str) and meaning.lower() == "no explanation needed"):
                            # Use an expander for a cleaner UI
                            with st.expander(f"**{kw}**"):
                                st.write(meaning)
                            explained_count += 1
                    
                    if explained_count == 0:
                        st.info("All extracted keywords are common terms and do not require special legal explanation.")
                
                else:
                    st.warning("Unexpected response from Groq API. Please check your API setup.")
            else:
                st.info("No specific legal keywords were identified in this document.")
                
            # --- MODIFICATION: Download button logic now uses the full list ---
            if keyword_download_list: # Check if the list is not empty
                # Join the list into a single string with newlines
                keyword_download_data = "\n\n".join(keyword_download_list)
                
                st.divider() # Add a small separator
                
                st.download_button(
                    label="⬇️ Download All Identified Keywords", # Updated label
                    data=keyword_download_data,
                    file_name=f"{uploaded_file.name}_all_keywords.txt", # Updated filename
                    mime="text/plain",
                    use_container_width=True # Make button fill width
                )

    # --- Column 2: Chatbot Panel (Right) ---
    with col2:
        st.subheader("🤖 Chat with Document")

        # Create a container for the chat history (makes it scrollable)
        chat_container = st.container(height=400, border=True)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat Input Area (at the bottom of this column)
        user_query = st.text_input("Enter your legal question:", key="chat_input_box")
        
        # Button columns
        btn_col1, btn_col2 = st.columns(2)
        
        ask_button = btn_col1.button("Ask", use_container_width=True, type="primary")
        clear_button = btn_col2.button("Clear Chat", use_container_width=True)

        # Handle button clicks
        if clear_button:
            st.session_state.messages = [] # Empty the history
            st.rerun() # Rerun the app to update the display

        if ask_button:
            if user_query:
                # Add user message to history
                st.session_state.messages.append({"role": "user", "content": user_query})
                
                # Get bot response
                with st.spinner("💭 Thinking..."):
                    answer = answer_query_with_context(user_query, index, chunks)
                
                # Add bot response to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Rerun to update the chat display
                st.rerun()
            else:
                # Show a warning if the ask button is pressed with no text
                st.warning("Please enter a question.")

    # --- Download Button for Full Text (at the bottom) ---
    st.divider()
    st.download_button(
        label="⬇️ Download Full Extracted Text",
        data=text,
        file_name=f"{uploaded_file.name}_extracted.txt",
        mime="text/plain"
    )

else:
    st.info("👆 Please upload a PDF file to begin analysis.")


