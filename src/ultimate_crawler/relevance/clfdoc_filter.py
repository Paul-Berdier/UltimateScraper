# src/ultimate_crawler/relevance/clfdoc_filter.py

from __future__ import annotations

import logging

from .embedding_model import EmbeddingRelevanceModel
from .clfdoc_model import ClfDocModel

logger = logging.getLogger(__name__)


class HybridRelevanceFilter:
    """
    Combine un score d'embedding (similarité) et un score ClfDoc (P(wine|text)).
    score_final = alpha * embedding + (1 - alpha) * clfdoc
    """

    def __init__(
        self,
        emb_model: EmbeddingRelevanceModel,
        clfdoc_model: ClfDocModel,
        alpha: float = 0.5,
    ):
        self.emb_model = emb_model
        self.clfdoc_model = clfdoc_model
        self.alpha = alpha
        logger.info(
            "HybridRelevanceFilter initialized with alpha=%.2f (embedding) / %.2f (clfdoc)",
            alpha,
            1 - alpha,
        )

    def score(self, text: str) -> float:
        se = self.emb_model.score(text)
        sc = self.clfdoc_model.score(text)
        final = self.alpha * se + (1.0 - self.alpha) * sc
        logger.debug(
            "Hybrid relevance: emb=%.4f, clfdoc=%.4f, final=%.4f",
            se,
            sc,
            final,
        )
        return final
