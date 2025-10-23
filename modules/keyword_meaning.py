import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_keywords_meaning_smart(keywords: list[str]) -> dict:
    """
    Use Groq API (Llama) to decide which keywords need explanation and explain them briefly.
    Returns a dictionary: {keyword: meaning or "No explanation needed"}
    """
    # Combine all keywords into one prompt
    keyword_list = ", ".join(keywords)

    prompt = f"""
    You are a legal assistant. Below is a list of terms extracted from a legal document:
    {keyword_list}

    Your task:
    1. Identify which words/phrases are actual *legal or technical* terms.
    2. For those, provide a short and clear meaning (max 15 words).
    3. For simple/common English words, reply "No explanation needed".
    4. Return the results in JSON format like:
       {{"term1": "meaning", "term2": "No explanation needed", ...}}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a concise and intelligent legal document assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=400,
        )

        # Extract response text
        result_text = response.choices[0].message.content.strip()

        # Try to safely parse JSON-like output
        import json, re
        try:
            cleaned = re.sub(r"```json|```", "", result_text).strip()
            return json.loads(cleaned)
        except Exception:
            # If parsing fails, return raw text
            return {"error": result_text}

    except Exception as e:
        return {"error": f"⚠️ Error fetching meanings: {e}"}
