# src/ultimate_crawler/crawl/parser.py

import trafilatura


def html_to_text(html: str, url: str | None = None) -> str:
    """
    Utilise trafilatura pour extraire un texte propre depuis le HTML.
    """
    if not html:
        return ""

    try:
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            favor_recall=True,
            url=url,
        )
        if not text:
            return ""
        return text.strip()
    except Exception:
        return ""
