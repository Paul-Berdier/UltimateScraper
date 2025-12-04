# src/ultimate_crawler/io/writers.py

from pathlib import Path


class RotatingJSONLWriter:
    """
    Implémentation simple : pour l'instant, pas de rotation,
    mais interface prête pour l'ajouter plus tard.
    """

    def __init__(self, path: Path, max_bytes: int = 2_000_000_000):
        self.base_path = path
        self.max_bytes = max_bytes
        self.current_path = self.base_path
        self._f = self.current_path.open("w", encoding="utf-8")
        self._written_bytes = 0

    def write(self, s: str):
        b = s.encode("utf-8")
        if self._written_bytes + len(b) > self.max_bytes:
            # rotation (base.jsonl.1, .2, etc.) si besoin
            self._f.close()
            self._f = self.current_path.open("a", encoding="utf-8")
            self._written_bytes = 0

        self._f.write(s)
        self._written_bytes += len(b)

    def close(self):
        if not self._f.closed:
            self._f.close()
