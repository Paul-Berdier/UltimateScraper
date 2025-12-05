# src/ultimate_crawler/dataset/builder.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class Seq2SeqExample:
    id: str
    input_text: str
    target_text: str
    meta: Dict[str, Any]


class Seq2SeqDatasetBuilder:
    """
    Construit un dataset (JSONL) pour entraînement d'un modèle encodeur-décodeur.
    v1 : summarization naïf (target = premières phrases).
    """

    def __init__(self, max_input_len: int = 2048, max_target_len: int = 256):
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len

    def _split_sentences(self, text: str) -> List[str]:
        # mini splitter naif, tu pourras le remplacer par spacy ou autre
        sents = []
        for part in text.replace("?", ".").replace("!", ".").split("."):
            p = part.strip()
            if p:
                sents.append(p)
        return sents

    def build_from_docs(
        self,
        docs: Iterable[Dict[str, Any]],
    ) -> Iterable[Seq2SeqExample]:
        """
        docs = dict contenant au moins 'text' et 'url'
        """
        for idx, doc in enumerate(docs):
            text = doc.get("text", "").strip()
            if not text:
                continue

            # tronquer input
            if len(text) > self.max_input_len:
                text_in = text[: self.max_input_len]
            else:
                text_in = text

            sents = self._split_sentences(text)
            if not sents:
                continue

            # simple résumé = join des 2–3 premières phrases
            target_sents = sents[:3]
            target = ". ".join(target_sents)
            if len(target) > self.max_target_len:
                target = target[: self.max_target_len]

            ex = Seq2SeqExample(
                id=f"doc_{idx}",
                input_text=text_in,
                target_text=target,
                meta={
                    "url": doc.get("url"),
                    "lang": doc.get("lang"),
                    "score_relevance": doc.get("score_relevance"),
                    "wine_slots": doc.get("wine_slots", {}),
                },
            )
            yield ex

    def write_jsonl(
        self,
        examples: Iterable[Seq2SeqExample],
        out_path: Path,
    ) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        n = 0
        with out_path.open("w", encoding="utf-8") as f:
            for ex in examples:
                obj = {
                    "id": ex.id,
                    "input": ex.input_text,
                    "target": ex.target_text,
                    "meta": ex.meta,
                }
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
                n += 1
        logger.info("Wrote %d seq2seq examples to %s", n, out_path)
