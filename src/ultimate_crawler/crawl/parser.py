# src/ultimate_crawler/crawl/parser.py

from __future__ import annotations

import logging
import re
from typing import Optional

import trafilatura

logger = logging.getLogger(__name__)

# Lignes JSON complètes (config, API, etc.)
JSON_LINE_RE = re.compile(r'^\s*[\{\[].*[\}\]]\s*$')

# Blobs encodés type base64/HTML encodé (ex: PHA+PGEgaHRlZj0i...)
# On matche une ligne assez longue uniquement composée de A-Z a-z 0-9 + / = et quelques ponctuations.
BASE64_LIKE_RE = re.compile(r'^[A-Za-z0-9+/=]{40,}$')


def clean_extracted_text(text: str) -> str:
    """
    Nettoie le texte extrait :
    - supprime les lignes vides
    - supprime les lignes JSON-like ({...}, [...])
    - supprime les blobs encodés "base64-like"
    """

    if not text:
        return ""

    cleaned_lines: list[str] = []

    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue

        # Skip lignes JSON/structured data (ex: {"api": {...}}, {}, etc.)
        if JSON_LINE_RE.match(s):
            logger.debug("Dropping JSON-like line: %s", s[:80])
            continue

        # Skip blobs type "PHA+PGEgaHRlZj0i..." (HTML encodé/base64-like)
        # Heuristique : très long, pas d'espaces, alphabet base64
        if BASE64_LIKE_RE.match(s):
            logger.debug("Dropping base64-like blob: %s", s[:80])
            continue

        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).strip()
    return cleaned


def html_to_text(html: str, url: Optional[str] = None) -> Optional[str]:
    """
    Wrapper autour trafilatura.extract pour obtenir un texte "article"
    puis appliquer un nettoyage maison pour virer le bruit (JSON, blobs encodés).
    """
    if not html:
        return None

    # extraction principale
    extracted = trafilatura.extract(
        html,
        url=url,
        output_format="txt",
        include_comments=False,
        include_links=False,
        include_tables=False,
        include_formatting=False,
        no_fallback=True,      # on ne veut pas du fallback super sale
        deduplicate=True,
    )

    if not extracted:
        logger.debug("trafilatura returned no content for %s", url)
        return None

    cleaned = clean_extracted_text(extracted)
    if not cleaned:
        logger.debug("clean_extracted_text() returned empty for %s", url)
        return None

    return cleaned
