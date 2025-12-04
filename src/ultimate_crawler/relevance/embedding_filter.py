# src/ultimate_crawler/relevance/embedding_filter.py

from .embedding_model import EmbeddingRelevanceModel


class EmbeddingRelevanceFilter:
    """
    Filtre de pertinence basé sur similarité cosinus via EmbeddingRelevanceModel.
    """

    def __init__(self, model: EmbeddingRelevanceModel):
        self.model = model

    def score(self, text: str) -> float:
        return self.model.score(text)
