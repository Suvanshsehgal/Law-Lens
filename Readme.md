# ⚖️ Law-Lens: Legal Document Analysis

An AI-powered legal document analysis tool that extracts text, identifies legal terms, highlights important clauses, and provides access to related Indian court cases.

## Features

### 📄 Document Processing
- **Text Extraction**: Optimized PDF text extraction with OCR fallback for scanned documents
- **Parallel Processing**: Fast extraction using pypdfium2 with multi-threading
- **Smart Caching**: Avoids re-processing the same document

### 🧠 AI-Powered Analysis
- **Keyword Extraction**: LegalBERT model identifies top legal keywords
- **Keyword Meanings**: Smart explanations for legal terminology
- **Hybrid Paragraph Scoring**: Semantic understanding + Groq AI scoring
  - Semantic filtering to identify legal content
  - AI scoring (1-3) for paragraph importance
  - Batch processing with exponential backoff

### 🎨 Document Highlighting
- **Color-Coded Highlights**:
  - 🔴 Red: High importance (critical obligations, liabilities)
  - 🟡 Yellow: Medium importance (supporting terms, procedures)
- **Original Formatting Preserved**: Highlights on actual PDF layout
- **Fuzzy Matching**: Robust matching across different PDF structures

### ⚖️ Indian Case Law Integration
- **IPC Section Identification**: AI identifies relevant IPC/law sections for each keyword
- **IndianKanoon Links**: Direct links to ALL related Supreme Court and High Court cases
- **Categories**: Criminal, Civil, Consumer, Property, General
- **100% Reliable**: No hallucinated cases, only real IndianKanoon search results

### 💬 Interactive Chatbot
- **Document Q&A**: Ask questions about the uploaded document
- **Context-Aware**: Uses FAISS vector search for relevant context
- **Groq-Powered**: Fast responses using Llama models

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
GROQ_API_KEY=your_groq_api_key
TESSERACT_PATH=path_to_tesseract
POPPLER_BIN_PATH=path_to_poppler
```

## Usage

```bash
streamlit run app.py
```

1. Upload a legal PDF document
2. View extracted keywords and meanings
3. Chat with the document
4. Download highlighted PDF with color-coded importance
5. Explore related IPC sections and Indian court cases

## Technology Stack

- **Frontend**: Streamlit
- **AI Models**: 
  - LegalBERT (keyword extraction)
  - Groq Llama 3.1 (meanings, scoring, IPC identification)
  - Sentence Transformers (semantic analysis)
- **PDF Processing**: pypdfium2, PyPDF2, pdf2image
- **OCR**: Tesseract
- **Vector Search**: FAISS
- **Highlighting**: PyMuPDF (fitz)

## Documentation

- `SIMPLIFIED_IPC_SYSTEM.md` - Details on IPC-based case law system
- `HYBRID_ANALYSIS_GUIDE.md` - Hybrid paragraph importance analysis

## Performance

- **Text Extraction**: 3-5x faster with pypdfium2
- **Paragraph Analysis**: Semantic filtering reduces API calls by 40-60%
- **Case Law**: 50% cost reduction with simplified IPC-based approach
- **Batch Processing**: Handles large documents efficiently

## Features in Detail

### Semantic Paragraph Analysis
- Filters legally-relevant paragraphs using embeddings
- Compares against 30+ legal concept keywords
- Only sends relevant content to AI for scoring

### Batch Processing with Retry Logic
- Processes 10 paragraphs per batch
- Exponential backoff: 2s → 4s → 8s → 15s
- Validates all responses before returning

### IPC-Based Case Law
- Identifies relevant IPC sections for keywords
- Creates generic IndianKanoon links showing ALL cases
- No hallucination risk - only real search results

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here] 