# src/ultimate_crawler/relevance/keyword_filter.py

from typing import List


class KeywordRelevanceFilter:
    """
    Filtre basique par mots-clés :
    score = nb_occurrences_normalisées (0..1)
    """

    def __init__(self, keywords: List[str]):
        self.keywords = [k.lower() for k in keywords]

    def score(self, text: str) -> float:
        if not text:
            return 0.0
        t = text.lower()
        total_len = len(t)
        if total_len == 0:
            return 0.0

        count = 0
        for kw in self.keywords:
            count += t.count(kw)

        # normalisation très simple
        return min(1.0, count / 10.0)
