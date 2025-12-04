# src/ultimate_crawler/relevance/language.py

from langdetect import detect, DetectorFactory

# pour que langdetect soit déterministe
DetectorFactory.seed = 42

SUPPORTED_MAP = {
    "fr": "fr",
    "en": "en",
    "es": "es",
    "zh-cn": "zh",
    "zh-tw": "zh",
    "zh": "zh",
}


def detect_lang(text: str) -> str:
    try:
        code = detect(text)
    except Exception:
        return "other"

    # map simple
    code = code.lower()
    if code in SUPPORTED_MAP:
        return SUPPORTED_MAP[code]
    return code
