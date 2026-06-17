# speech.py — Analyse du discours : mots parasites, structure, clarté

from .utils import (
    word_count,
    sentence_count,
    avg_words_per_sentence,
    lexical_diversity,
    find_filler_words,
    tokenize_sentences,
    tokenize_words,
)

# ---------------------------------------------------------------------------
# Seuils de clarté
# ---------------------------------------------------------------------------

# Nombre de mots par phrase au-delà duquel la phrase est considérée longue
LONG_SENTENCE_THRESHOLD = 25

# Ratio de mots parasites / total mots au-delà duquel c'est problématique
FILLER_RATIO_WARNING = 0.05


# ---------------------------------------------------------------------------
# Structure du discours
# ---------------------------------------------------------------------------

def detect_structure(text: str) -> dict:
    """
    Évalue la présence d'une introduction, d'un développement et d'une conclusion
    en cherchant des marqueurs discursifs typiques.
    """
    INTRO_MARKERS = {
        "fr": ["tout d'abord", "premièrement", "pour commencer", "je vais",
               "dans cet", "dans cette", "aujourd'hui", "nous allons", "je souhaite"],
        "en": ["first", "firstly", "to begin", "in this", "today", "i will",
               "we will", "i would like", "let me"],
    }
    CONCLUSION_MARKERS = {
        "fr": ["en conclusion", "pour conclure", "en résumé", "ainsi",
               "en définitive", "finalement", "pour terminer", "en somme"],
        "en": ["in conclusion", "to conclude", "in summary", "finally",
               "to sum up", "therefore", "in short", "overall"],
    }

    text_lower = text.lower()
    sentences = tokenize_sentences(text)
    n = len(sentences)

    # Détecte la langue dominante des marqueurs
    fr_intro = sum(1 for m in INTRO_MARKERS["fr"] if m in text_lower)
    en_intro = sum(1 for m in INTRO_MARKERS["en"] if m in text_lower)
    lang_hint = "fr" if fr_intro >= en_intro else "en"

    intro_markers = INTRO_MARKERS[lang_hint]
    conclusion_markers = CONCLUSION_MARKERS[lang_hint]

    has_intro = any(m in text_lower for m in intro_markers)
    has_conclusion = any(m in text_lower for m in conclusion_markers)
    # Le développement est présent si le texte a au moins 3 phrases
    has_body = n >= 3

    score = sum([has_intro, has_body, has_conclusion])  # 0-3

    return {
        "has_intro": has_intro,
        "has_body": has_body,
        "has_conclusion": has_conclusion,
        "structure_score": score,          # /3
        "structure_label": _structure_label(score),
    }


def _structure_label(score: int) -> str:
    if score == 3:
        return "complète"
    if score == 2:
        return "partielle"
    return "insuffisante"


# ---------------------------------------------------------------------------
# Clarté
# ---------------------------------------------------------------------------

def analyze_clarity(text: str, lang: str = "fr") -> dict:
    """
    Mesure la clarté du discours :
    - longueur moyenne des phrases
    - proportion de phrases longues
    - richesse lexicale (TTR)
    - score de clarté global [0-100]
    """
    sentences = tokenize_sentences(text)
    if not sentences:
        return {"avg_words_per_sentence": 0, "long_sentence_ratio": 0.0,
                "lexical_diversity": 0.0, "clarity_score": 0}

    word_counts = [len(tokenize_words(s)) for s in sentences]
    avg_wps = round(sum(word_counts) / len(word_counts), 2)
    long_ratio = round(
        sum(1 for c in word_counts if c > LONG_SENTENCE_THRESHOLD) / len(word_counts), 4
    )
    ttr = lexical_diversity(text)

    # Score clarté : pénalise les phrases trop longues et la faible diversité
    clarity = 100
    clarity -= min(40, long_ratio * 100)          # jusqu'à -40 pour phrases longues
    clarity -= max(0, (0.4 - ttr) * 50)           # jusqu'à -20 pour faible TTR
    clarity = max(0, round(clarity))

    return {
        "avg_words_per_sentence": avg_wps,
        "long_sentence_ratio": long_ratio,
        "lexical_diversity": ttr,
        "clarity_score": clarity,
    }


# ---------------------------------------------------------------------------
# Point d'entrée principal
# ---------------------------------------------------------------------------

def analyze(text: str, lang: str = "fr") -> dict:
    """
    Analyse complète du discours.

    Retourne :
        {
            "word_count": int,
            "sentence_count": int,
            "filler_words": dict[str, int],
            "filler_ratio": float,
            "structure": dict,
            "clarity": dict,
        }
    """
    wc = word_count(text)
    sc = sentence_count(text)
    fillers = find_filler_words(text, lang=lang)
    filler_total = sum(fillers.values())
    filler_ratio = round(filler_total / wc, 4) if wc else 0.0

    return {
        "word_count": wc,
        "sentence_count": sc,
        "filler_words": fillers,
        "filler_ratio": filler_ratio,
        "filler_warning": filler_ratio > FILLER_RATIO_WARNING,
        "structure": detect_structure(text),
        "clarity": analyze_clarity(text, lang=lang),
    }
