from dotenv import load_dotenv
load_dotenv()


import os
import json
import logging
import re
import time
from typing import Dict, Tuple
from groq import Groq

logging.basicConfig(level=logging.INFO)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def normalize_keyword(keyword: str):
    """
    Clean raw keyword text extracted from OCR/LLM.
    Removes underscores, numbers, extra spaces etc.
    """
    if not keyword:
        return None

    keyword = keyword.lower().strip()

    keyword = keyword.replace("_", " ")
    keyword = " ".join(keyword.split())
    keyword = re.sub(r'\d+', '', keyword)

    if len(keyword) < 3:
        return None

    return keyword


def get_ipc_section_for_keyword(keyword: str) -> Dict:
    """
    Uses LLM to identify the most relevant legal section for a keyword.
    Returns structured JSON (section, category, summary)
    """

    cleaned = normalize_keyword(keyword)

    if not cleaned:
        logging.warning(f"Keyword '{keyword}' became invalid after cleaning.")
        cleaned = keyword

    prompt = f"""
You are a senior Indian legal expert.

For the keyword: "{cleaned}"

Identify the MOST relevant Indian law section.

Prefer:
- Indian Penal Code (IPC)
- Transfer of Property Act
- Rent Control Acts
- Contract Act
- Consumer Protection Act
- IT Act
- CrPC / CPC

Rules:
- DO NOT invent fake sections
- ONLY provide real Indian legal acts
- If unsure, choose the safest commonly applicable section
- Return STRICT JSON ONLY

Respond in this format ONLY:

{{
 "section": "Act Name Section Number",
 "law_type": "criminal | civil | rent | property | contract | consumer | general",
 "summary": "short 1-2 line meaning of this section"
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300
        )

        data = json.loads(response.choices[0].message.content)

        ipc_section = data.get("section", "General Legal Term")
        category = data.get("law_type", "general")
        summary = data.get("summary", "Relevant legal section.")

        logging.info(f"Mapped '{keyword}' → {ipc_section}")

        return {
            "keyword": cleaned,
            "ipc_section": ipc_section,
            "case_category": category,
            "summary": summary
        }

    except Exception as e:
        logging.error(f"Error mapping keyword: {e}")
        return {
            "keyword": keyword,
            "ipc_section": "General Legal Term",
            "case_category": "general",
            "summary": "No specific section identified."
        }


def build_kanoon_link(ipc_section: str):
    """
    Builds Indian Kanoon Search Link
    """
    query = ipc_section.replace(" ", "+")
    return f"https://indiankanoon.org/search/?formInput={query}"


def get_case_law_for_keyword(keyword: str) -> Tuple[Dict, str]:
    """
    Identify IPC/Act + Build Kanoon Link + Summary
    Returns JSON + UI string
    """

    law_info = get_ipc_section_for_keyword(keyword)

    law_info["search_query"] = law_info["ipc_section"].replace(" ", "+")
    law_info["kanoon_link"] = build_kanoon_link(law_info["ipc_section"])

    ui_output = f"""Keyword: {law_info['keyword']}
IPC/Law Section: {law_info['ipc_section']}
Category: {law_info['case_category'].title()}
Summary: {law_info['summary']}
IndianKanoon Link: {law_info['kanoon_link']}"""

    return law_info, ui_output


def get_cases_for_keywords(keywords: list) -> Dict[str, Tuple[Dict, str]]:
    """
    Fetch case law links for multiple keywords.
    Returns: Dict mapping keyword -> (json_output, ui_output)
    """

    if not keywords:
        logging.warning("No keywords provided for case law fetching")
        return {}

    results = {}

    logging.info(f"Starting case law fetch for {len(keywords)} keywords: {keywords}")

    for i, keyword in enumerate(keywords, 1):
        logging.info(f"Processing keyword {i}/{len(keywords)}: {keyword}")

        try:
            json_output, ui_output = get_case_law_for_keyword(keyword)
            results[keyword] = (json_output, ui_output)
            logging.info(f"Successfully processed '{keyword}'")

        except Exception as e:
            logging.error(f"Failed to process '{keyword}': {e}")
            results[keyword] = (
                {"keyword": keyword, "error": str(e)},
                f"Keyword: {keyword}\nError occurred while processing."
            )

        if i < len(keywords):
            time.sleep(0.5)

    logging.info(f"Case law processing complete. Retrieved {len(results)} results.")
    return results