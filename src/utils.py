# utils.py — Nettoyage de texte et fonctions helpers

import re
import unicodedata

# ---------------------------------------------------------------------------
# Mots parasites par langue
# ---------------------------------------------------------------------------

FILLER_WORDS: dict[str, list[str]] = {
    "fr": [
        "euh", "bah", "ben", "bref", "donc", "voilà", "du coup", "en fait",
        "genre", "quoi", "hein", "bon", "eh bien", "alors", "enfin",
        "c'est-à-dire", "tu vois", "vous voyez", "machin", "truc", "chose",
    ],
    "en": [
        "uh", "um", "like", "you know", "so", "basically", "literally",
        "actually", "right", "okay", "well", "i mean", "kind of", "sort of",
        "you see", "stuff", "thing", "things",
    ],
}


# ---------------------------------------------------------------------------
# Nettoyage
# ---------------------------------------------------------------------------

def normalize_whitespace(text: str) -> str:
    """Remplace toute séquence d'espaces/tabulations/retours par un espace simple."""
    return re.sub(r"[ \t]+", " ", text).strip()


def clean_text(text: str, *, lower: bool = False) -> str:
    """
    Nettoyage léger : normalise les espaces, supprime les caractères de contrôle.
    Conserve la ponctuation (nécessaire pour la segmentation en phrases).
    """
    # Normalisation Unicode (NFD → NFC)
    text = unicodedata.normalize("NFC", text)
    # Supprime les caractères de contrôle sauf \n
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = normalize_whitespace(text)
    return text.lower() if lower else text


def strip_punctuation(text: str) -> str:
    """Supprime toute ponctuation d'un texte."""
    return re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)


# ---------------------------------------------------------------------------
# Tokenisation
# ---------------------------------------------------------------------------

def tokenize_words(text: str, *, remove_stopwords: bool = False) -> list[str]:
    """
    Retourne la liste des tokens (mots) en minuscules, sans ponctuation.
    `remove_stopwords` est un hook réservé à une extension future.
    """
    cleaned = strip_punctuation(clean_text(text, lower=True))
    tokens = [t for t in cleaned.split() if t]
    return tokens


def tokenize_sentences(text: str) -> list[str]:
    """Segmente le texte en phrases sur . ! ? et les variantes avec guillemets."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


# ---------------------------------------------------------------------------
# Statistiques de base
# ---------------------------------------------------------------------------

def word_count(text: str) -> int:
    return len(tokenize_words(text))


def sentence_count(text: str) -> int:
    return len(tokenize_sentences(text))


def avg_words_per_sentence(text: str) -> float:
    sentences = tokenize_sentences(text)
    if not sentences:
        return 0.0
    counts = [len(tokenize_words(s)) for s in sentences]
    return round(sum(counts) / len(counts), 2)


def lexical_diversity(text: str) -> float:
    """Type-Token Ratio : proportion de mots uniques. Retourne 0.0 si texte vide."""
    tokens = tokenize_words(text)
    if not tokens:
        return 0.0
    return round(len(set(tokens)) / len(tokens), 4)


# ---------------------------------------------------------------------------
# Détection de mots parasites
# ---------------------------------------------------------------------------

def find_filler_words(text: str, lang: str = "fr") -> dict[str, int]:
    """
    Retourne un dict {mot_parasite: nombre_d_occurrences} pour la langue donnée.
    La recherche est insensible à la casse et porte sur des mots entiers.
    """
    fillers = FILLER_WORDS.get(lang, FILLER_WORDS["fr"])
    text_lower = text.lower()
    result: dict[str, int] = {}
    for filler in fillers:
        pattern = rf"\b{re.escape(filler)}\b"
        count = len(re.findall(pattern, text_lower))
        if count:
            result[filler] = count
    return result
