# sentiment.py — Analyse de sentiment TextBlob (FR + EN)

from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    """Retourne 'fr', 'en', ou 'unknown'."""
    try:
        lang = detect(text)
        return lang if lang in ("fr", "en") else "unknown"
    except LangDetectException:
        return "unknown"


def _polarity_label(polarity: float) -> str:
    if polarity > 0.1:
        return "positif"
    if polarity < -0.1:
        return "négatif"
    return "neutre"


def analyze(text: str, lang: str | None = None) -> dict:
    """
    Analyse le sentiment d'un texte en FR ou EN.

    Retourne :
        {
            "language": str,          # 'fr' | 'en' | 'unknown'
            "polarity": float,        # [-1.0, 1.0]
            "subjectivity": float,    # [0.0, 1.0]  (EN uniquement, sinon None)
            "label": str,             # 'positif' | 'négatif' | 'neutre'
        }
    """
    if not text or not text.strip():
        return {"language": "unknown", "polarity": 0.0, "subjectivity": None, "label": "neutre"}

    detected = lang or detect_language(text)

    if detected == "fr":
        blob = TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
        polarity = blob.sentiment[0]
        subjectivity = None
    else:
        # Fallback EN pour 'unknown' également
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

    return {
        "language": detected,
        "polarity": round(polarity, 4),
        "subjectivity": round(subjectivity, 4) if subjectivity is not None else None,
        "label": _polarity_label(polarity),
    }
