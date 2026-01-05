import re

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
