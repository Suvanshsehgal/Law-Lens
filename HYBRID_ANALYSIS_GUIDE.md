# Hybrid Paragraph Importance Analysis

## Overview
The system now uses a **two-stage hybrid model** combining semantic understanding with AI-powered scoring to identify and highlight important legal paragraphs.

## How It Works

### Stage 1: Semantic Legal Relevance Check
**Purpose:** Filter out non-legal content before expensive AI scoring

**Method:**
- Uses `sentence-transformers` (all-MiniLM-L6-v2) to create embeddings
- Compares paragraph embeddings against 30+ legal concept keywords
- Calculates cosine similarity to determine legal relevance
- Threshold: 0.3 similarity score

**Legal Concepts Checked:**
- Contract terms (agreement, liability, indemnify, warranty, breach)
- Legal procedures (jurisdiction, arbitration, dispute, remedy)
- Rights & obligations (duties, responsibilities, enforce, binding)
- Compliance terms (regulation, statute, law, compliance)

**Result:** Only legally-relevant paragraphs proceed to Stage 2

---

### Stage 2: Groq AI Importance Scoring
**Purpose:** Intelligent scoring of legal paragraph importance

**Model:** Llama-3.1-8b-instant via Groq API

**Scoring Criteria:**
- **Score 3 (HIGH):** Critical legal obligations, liabilities, rights, penalties, termination clauses, indemnification, warranties, binding commitments
- **Score 2 (MEDIUM):** Supporting legal terms, definitions, procedural details, contextual information
- **Score 1 (LOW):** General statements, background information, non-binding content

**Prompt Engineering:**
- Zero-shot classification with clear criteria
- Temperature: 0.1 (deterministic)
- Max tokens: 10 (single number response)

---

## Highlighting System

### Color Mapping:
- 🔴 **RED** = Score 3 (High Importance) - Critical legal content
- 🟡 **YELLOW** = Score 2 (Medium Importance) - Supporting legal content
- ⚪ **NO HIGHLIGHT** = Score 1 (Low Importance) - General content

### Matching Algorithm:
Uses fuzzy matching to handle PDF formatting differences:
1. **Token Overlap:** Word-level set comparison (≥50% overlap)
2. **Fuzzy Similarity:** Character-level SequenceMatcher (≥60% similar)
3. **Minimum Threshold:** At least 5 shared tokens required

---

## Performance Optimization

### Efficiency Features:
- **Semantic filtering** reduces Groq API calls by 40-60%
- **Batch processing** with progress logging
- **Fallback mechanism** if semantic model fails
- **Error handling** with default scores

### Cost Savings:
- Only legally-relevant paragraphs sent to Groq
- Typical 100-paragraph document: ~30-50 API calls instead of 100

---

## Installation

```bash
pip install sentence-transformers scikit-learn
```

---

## Example Output

```
Paragraph: "The Seller shall indemnify the Buyer against all losses..."
→ Semantic Check: ✓ Legal (similarity: 0.78)
→ Groq Score: 3 (HIGH)
→ Highlight: 🔴 RED

Paragraph: "This agreement is governed by the laws of..."
→ Semantic Check: ✓ Legal (similarity: 0.65)
→ Groq Score: 2 (MEDIUM)
→ Highlight: 🟡 YELLOW

Paragraph: "The parties acknowledge that this document..."
→ Semantic Check: ✓ Legal (similarity: 0.42)
→ Groq Score: 1 (LOW)
→ Highlight: None

Paragraph: "The weather was sunny on the day of signing..."
→ Semantic Check: ✗ Not Legal (similarity: 0.12)
→ Groq Score: Skipped
→ Highlight: None
```

---

## Benefits

1. **Accuracy:** AI understands context, not just keywords
2. **Efficiency:** Semantic filtering reduces API costs
3. **Granularity:** 3-level scoring vs binary high/low
4. **Robustness:** Fallback mechanisms prevent failures
5. **Transparency:** Visual metrics show analysis results
