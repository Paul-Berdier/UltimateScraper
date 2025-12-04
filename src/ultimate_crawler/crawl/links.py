# src/ultimate_crawler/crawl/links.py

from typing import List, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


def extract_links_same_domain(html: str, base_url: str) -> List[str]:
    """
    Extrait les liens <a href="..."> dans la page, normalisés en URLs absolues,
    et filtrés pour ne garder que :
      - schéma http/https
      - même domaine que base_url
    """

    if not html:
        return []

    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc

    soup = BeautifulSoup(html, "lxml")

    links: Set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a.get("href")

        # Skip ancres, mailto, tel, javascript:
        if not href:
            continue
        href = href.strip()
        if href.startswith("#"):
            continue
        if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
            continue

        # Résoudre en URL absolue
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Schéma valide
        if parsed.scheme not in ("http", "https"):
            continue

        # Même domaine uniquement (crawl "profond" par site)
        if parsed.netloc != base_domain:
            continue

        # Normalisation simple (pas de fragment)
        normalized = parsed._replace(fragment="").geturl()
        links.add(normalized)

    logger.debug(
        "Extracted %d same-domain links from %s",
        len(links),
        base_url,
    )

    return list(links)
