# src/ultimate_crawler/discovery/search_api.py

from dataclasses import dataclass
from typing import List


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str


class SearchEngine:
    """
    Interface générique pour un moteur de recherche externe (SerpAPI, Bing, etc.)
    """

    def search(self, query: str, lang: str, num_results: int = 20) -> List[SearchResult]:
        raise NotImplementedError


class DummySearchEngine(SearchEngine):
    """
    Implémentation vide pour l’instant.
    À remplacer par une intégration réelle.
    """

    def search(self, query: str, lang: str, num_results: int = 20) -> List[SearchResult]:
        # Ici tu ajouteras ton vrai appel API.
        print(f"[DummySearchEngine] search(query={query!r}, lang={lang}, n={num_results})")
        return []
