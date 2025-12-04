# src/ultimate_crawler/core/utils.py

def estimate_bytes(s: str) -> int:
    if not s:
        return 0
    return len(s.encode("utf-8"))
