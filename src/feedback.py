# feedback.py — Générateur de feedback

from __future__ import annotations

# ---------------------------------------------------------------------------
# Feedback sentiment
# ---------------------------------------------------------------------------

def _feedback_sentiment(sentiment: dict) -> list[str]:
    lines = []
    label = sentiment.get("label", "neutre")
    polarity = sentiment.get("polarity", 0.0)
    subjectivity = sentiment.get("subjectivity")
    lang = sentiment.get("language", "fr")

    if label == "positif":
        lines.append(f"Le ton général est **positif** (polarité : {polarity:+.2f}).")
    elif label == "négatif":
        lines.append(f"Le ton général est **négatif** (polarité : {polarity:+.2f}).")
    else:
        lines.append(f"Le ton général est **neutre** (polarité : {polarity:+.2f}).")

    if subjectivity is not None:
        if subjectivity > 0.6:
            lines.append("Le texte est très **subjectif** : il reflète davantage une opinion personnelle qu'un propos factuel.")
        elif subjectivity < 0.3:
            lines.append("Le texte est très **objectif** : le propos s'appuie sur des faits.")
        else:
            lines.append(f"Le niveau de subjectivité est modéré ({subjectivity:.0%}).")

    return lines


# ---------------------------------------------------------------------------
# Feedback mots parasites
# ---------------------------------------------------------------------------

def _feedback_fillers(speech: dict) -> list[str]:
    lines = []
    fillers = speech.get("filler_words", {})
    filler_ratio = speech.get("filler_ratio", 0.0)
    warning = speech.get("filler_warning", False)

    if not fillers:
        lines.append("Aucun mot parasite détecté. Bravo !")
        return lines

    top = sorted(fillers.items(), key=lambda x: x[1], reverse=True)[:5]
    top_str = ", ".join(f'« {w} » ({n}×)' for w, n in top)
    lines.append(f"Mots parasites détectés : {top_str}.")

    if warning:
        lines.append(
            f"Le ratio de mots parasites est élevé ({filler_ratio:.1%} des mots). "
            "Essayez de les remplacer par des silences ou des formulations plus précises."
        )
    else:
        lines.append(f"Le ratio reste acceptable ({filler_ratio:.1%}).")

    return lines


# ---------------------------------------------------------------------------
# Feedback structure
# ---------------------------------------------------------------------------

def _feedback_structure(speech: dict) -> list[str]:
    lines = []
    structure = speech.get("structure", {})
    label = structure.get("structure_label", "insuffisante")
    score = structure.get("structure_score", 0)

    lines.append(f"Structure du discours : **{label}** ({score}/3).")

    if not structure.get("has_intro"):
        lines.append("- Ajoutez une **introduction** avec un marqueur d'ouverture (ex. : « Pour commencer… »).")
    if not structure.get("has_body"):
        lines.append("- Le **développement** est trop court : développez votre argumentation en plusieurs phrases.")
    if not structure.get("has_conclusion"):
        lines.append("- Concluez explicitement (ex. : « En résumé… », « Pour conclure… »).")

    if score == 3:
        lines.append("Les trois parties sont bien présentes.")

    return lines


# ---------------------------------------------------------------------------
# Feedback clarté
# ---------------------------------------------------------------------------

def _feedback_clarity(speech: dict) -> list[str]:
    lines = []
    clarity = speech.get("clarity", {})
    score = clarity.get("clarity_score", 0)
    avg_wps = clarity.get("avg_words_per_sentence", 0)
    long_ratio = clarity.get("long_sentence_ratio", 0.0)
    ttr = clarity.get("lexical_diversity", 0.0)

    if score >= 80:
        lines.append(f"Clarté : **excellente** ({score}/100).")
    elif score >= 60:
        lines.append(f"Clarté : **correcte** ({score}/100).")
    elif score >= 40:
        lines.append(f"Clarté : **à améliorer** ({score}/100).")
    else:
        lines.append(f"Clarté : **insuffisante** ({score}/100).")

    if avg_wps > 25:
        lines.append(
            f"Vos phrases sont longues en moyenne ({avg_wps:.0f} mots/phrase). "
            "Fractionnez-les pour faciliter la compréhension."
        )
    elif avg_wps > 0:
        lines.append(f"Longueur moyenne des phrases : {avg_wps:.0f} mots — bonne lisibilité.")

    if long_ratio > 0.3:
        lines.append(
            f"{long_ratio:.0%} de vos phrases dépassent 25 mots. "
            "Privilégiez des phrases courtes et directes."
        )

    if ttr < 0.4:
        lines.append(
            f"La richesse lexicale est faible (TTR : {ttr:.0%}). "
            "Variez votre vocabulaire pour éviter les répétitions."
        )
    elif ttr > 0.7:
        lines.append(f"Vocabulaire varié et riche (TTR : {ttr:.0%}).")

    return lines


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def generate(sentiment: dict, speech: dict) -> dict:
    """
    Génère un rapport de feedback structuré à partir des résultats
    de sentiment.analyze() et speech.analyze().

    Retourne :
        {
            "sentiment": list[str],
            "fillers":   list[str],
            "structure": list[str],
            "clarity":   list[str],
            "summary":   str,          # phrase de synthèse globale
        }
    }
    """
    sentiment_fb = _feedback_sentiment(sentiment)
    filler_fb = _feedback_fillers(speech)
    structure_fb = _feedback_structure(speech)
    clarity_fb = _feedback_clarity(speech)

    summary = _build_summary(sentiment, speech)

    return {
        "sentiment": sentiment_fb,
        "fillers": filler_fb,
        "structure": structure_fb,
        "clarity": clarity_fb,
        "summary": summary,
    }


def _build_summary(sentiment: dict, speech: dict) -> str:
    """Phrase de synthèse globale combinant sentiment, structure et clarté."""
    label = sentiment.get("label", "neutre")
    structure_score = speech.get("structure", {}).get("structure_score", 0)
    clarity_score = speech.get("clarity", {}).get("clarity_score", 0)
    filler_warning = speech.get("filler_warning", False)

    parts = []

    tone_map = {"positif": "positif", "négatif": "négatif", "neutre": "neutre"}
    parts.append(f"Ton {tone_map.get(label, 'neutre')}")

    if structure_score == 3:
        parts.append("structure complète")
    elif structure_score == 2:
        parts.append("structure partielle")
    else:
        parts.append("structure à renforcer")

    if clarity_score >= 80:
        parts.append("bonne clarté")
    elif clarity_score >= 60:
        parts.append("clarté correcte")
    else:
        parts.append("clarté à améliorer")

    if filler_warning:
        parts.append("trop de mots parasites")

    return " · ".join(parts) + "."
