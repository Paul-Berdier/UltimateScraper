# src/ultimate_crawler/relevance/embedding_model.py

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingRelevanceModel:
    """
    Wrap de SentenceTransformer pour calcul de similarité
    texte <-> requête mots-clés.
    """

    def __init__(self, model_name: str, keywords: List[str]):
        if not model_name:
            raise ValueError("embedding_model_name must be set in config for embedding mode.")
        logger.info("Loading SentenceTransformer model: %s", model_name)
        self.model = SentenceTransformer(model_name)
        query = " ".join(keywords)
        logger.info("Building query embedding from keywords=%s", keywords)
        self.query_vec = self.model.encode(query, normalize_embeddings=True)

    def score(self, text: str) -> float:
        if not text:
            return 0.0
        snippet = text[:3000]
        vec = self.model.encode(snippet, normalize_embeddings=True)
        sim = float(np.dot(self.query_vec, vec))
        logger.debug("Embedding similarity score=%f", sim)
        return sim
