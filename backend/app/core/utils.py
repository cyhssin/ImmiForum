import re

def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug (unicode-aware, e.g. Persian titles)."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text