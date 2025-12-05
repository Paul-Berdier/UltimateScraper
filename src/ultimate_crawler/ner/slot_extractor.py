# src/ultimate_crawler/ner/slot_extractor.py

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class WineSlots:
    grapes: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    appellations: List[str] = field(default_factory=list)
    styles: List[str] = field(default_factory=list)   # rouge, blanc, rosé, etc.
    vintages: List[int] = field(default_factory=list)
    alcohol_vol: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WineSlotExtractor:
    """
    SlotNER ultra simple, basé sur dictionnaires + regex.
    Tu pourras le rendre plus smart plus tard (spaCy, CRF, etc.).
    """

    def __init__(
        self,
        grape_lexicon: List[str] | None = None,
        region_lexicon: List[str] | None = None,
        appellation_lexicon: List[str] | None = None,
    ):
        self.grape_lexicon = [g.lower() for g in (grape_lexicon or [])]
        self.region_lexicon = [r.lower() for r in (region_lexicon or [])]
        self.appellation_lexicon = [a.lower() for a in (appellation_lexicon or [])]

        # styles simples
        self.styles_terms = [
            "rouge", "blanc", "rosé", "rose", "sparkling", "champagne",
            "orange wine", "vin jaune", "vin doux", "sweet", "dry",
        ]

        # regex millésimes
        self.vintage_re = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")
        # regex alcool : 12.5%, 14 %, 13,5% vol
        self.alcohol_re = re.compile(r"(\d{1,2}(?:[\.,]\d)?)\s*%")

    def _match_lexicon(self, text: str, lexicon: List[str]) -> List[str]:
        found = []
        low = text.lower()
        for w in lexicon:
            if w in low:
                found.append(w)
        return sorted(set(found))

    def extract(self, text: str) -> WineSlots:
        s = WineSlots()

        # lexiques
        if self.grape_lexicon:
            s.grapes = self._match_lexicon(text, self.grape_lexicon)
        if self.region_lexicon:
            s.regions = self._match_lexicon(text, self.region_lexicon)
        if self.appellation_lexicon:
            s.appellations = self._match_lexicon(text, self.appellation_lexicon)

        low = text.lower()

        # styles
        s.styles = sorted({st for st in self.styles_terms if st in low})

        # millésimes
        vintages = [int(m.group(1)) for m in self.vintage_re.finditer(text)]
        s.vintages = sorted(set(vintages))

        # alcool
        vols = []
        for m in self.alcohol_re.finditer(text):
            try:
                v = float(m.group(1).replace(",", "."))
                vols.append(v)
            except ValueError:
                continue
        s.alcohol_vol = vols

        logger.debug("Extracted slots: %s", s.to_dict())
        return s
