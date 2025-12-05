# src/ultimate_crawler/relevance/clfdoc_model.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import logging

import joblib
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ClfDocConfig:
    model_path: str
    vectorizer_path: str
    positive_label: str = "wine"   # label pour lequel on veut la proba


class ClfDocModel:
    """
    Wrapper pour un modèle sklearn de classification de documents.
    On attend :
      - un vectorizer (TfidfVectorizer ou autre)
      - un modèle (LogisticRegression, LinearSVC avec calibrage, etc.)
    """

    def __init__(self, cfg: ClfDocConfig):
        self.cfg = cfg
        logger.info(
            "Loading ClfDoc model from %s and vectorizer from %s",
            cfg.model_path,
            cfg.vectorizer_path,
        )
        self.vectorizer = joblib.load(cfg.vectorizer_path)
        self.model = joblib.load(cfg.model_path)

        if hasattr(self.model, "classes_"):
            self.classes_ = list(self.model.classes_)
            logger.info("ClfDoc classes: %s", self.classes_)
        else:
            self.classes_ = None
            logger.warning("Model has no 'classes_' attribute (is it a sklearn classifier?).")

    def score(self, text: str) -> float:
        """
        Retourne P(positive_label | text) si possible, sinon un score 0..1 approximatif.
        """
        if not text:
            return 0.0

        X = self.vectorizer.transform([text])

        # cas standard : modèle probabiliste
        if hasattr(self.model, "predict_proba") and self.classes_ is not None:
            proba = self.model.predict_proba(X)[0]
            try:
                idx = self.classes_.index(self.cfg.positive_label)
            except ValueError:
                # label absent => on prend la plus haute proba
                logger.warning(
                    "Positive label '%s' not in classes %s, taking max proba.",
                    self.cfg.positive_label,
                    self.classes_,
                )
                return float(np.max(proba))
            return float(proba[idx])

        # fallback : décision binaire de type SVM
        if hasattr(self.model, "decision_function"):
            df = self.model.decision_function(X)[0]
            # squashing -> [0,1] via logistic
            s = float(1.0 / (1.0 + np.exp(-df)))
            return s

        logger.warning("Model has no predict_proba or decision_function, returning 0.5.")
        return 0.5
