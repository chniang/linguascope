# app.py — Point d'entrée Gradio pour LinguaScope

import gradio as gr
from src import sentiment as sentiment_mod
from src import speech as speech_mod
from src import feedback as feedback_mod

# ---------------------------------------------------------------------------
# Logique métier
# ---------------------------------------------------------------------------

LANG_MAP = {"Détection auto": None, "Français": "fr", "Anglais": "en"}


def run_analysis(text: str, lang_choice: str) -> tuple[str, str, str, str, str]:
    """
    Orchestre les trois modules et retourne 5 chaînes Markdown
    pour les 5 composants de sortie Gradio.
    """
    if not text or not text.strip():
        empty = "_Entrez un texte pour lancer l'analyse._"
        return empty, empty, empty, empty, empty

    lang = LANG_MAP.get(lang_choice)

    sent = sentiment_mod.analyze(text, lang=lang)
    spch = speech_mod.analyze(text, lang=sent["language"] if lang is None else lang)
    fb   = feedback_mod.generate(sent, spch)

    return (
        _render_summary(fb["summary"], sent),
        _render_sentiment(fb["sentiment"], sent),
        _render_speech(fb, spch),
        _render_structure(fb["structure"], spch),
        _render_clarity(fb["clarity"], spch),
    )


# ---------------------------------------------------------------------------
# Rendus Markdown
# ---------------------------------------------------------------------------

def _render_summary(summary: str, sent: dict) -> str:
    lang_label = {"fr": "Français", "en": "Anglais"}.get(sent["language"], "Inconnu")
    polarity = sent["polarity"]
    bar = _polarity_bar(polarity)
    return (
        f"### Synthèse\n"
        f"{summary}\n\n"
        f"**Langue détectée :** {lang_label}\n\n"
        f"**Polarité** `{polarity:+.4f}`\n\n{bar}"
    )


def _render_sentiment(lines: list[str], sent: dict) -> str:
    body = "\n\n".join(lines)
    sub = sent.get("subjectivity")
    sub_line = f"\n\n**Subjectivité :** `{sub:.0%}`" if sub is not None else ""
    return f"### Sentiment\n{body}{sub_line}"


def _render_speech(fb: dict, spch: dict) -> str:
    wc = spch["word_count"]
    sc = spch["sentence_count"]
    fillers = "\n\n".join(fb["fillers"])
    return (
        f"### Mots parasites\n"
        f"**{wc} mots** · **{sc} phrases**\n\n"
        f"{fillers}"
    )


def _render_structure(lines: list[str], spch: dict) -> str:
    s = spch["structure"]
    checks = (
        f"{'✅' if s['has_intro'] else '❌'} Introduction  "
        f"{'✅' if s['has_body'] else '❌'} Développement  "
        f"{'✅' if s['has_conclusion'] else '❌'} Conclusion"
    )
    body = "\n\n".join(lines)
    return f"### Structure\n{checks}\n\n{body}"


def _render_clarity(lines: list[str], spch: dict) -> str:
    c = spch["clarity"]
    score = c["clarity_score"]
    bar = _score_bar(score)
    body = "\n\n".join(lines)
    return f"### Clarté\n{bar}\n\n{body}"


def _polarity_bar(polarity: float) -> str:
    """Barre textuelle [-1 … +1] avec curseur."""
    pos = int((polarity + 1) / 2 * 20)
    pos = max(0, min(20, pos))
    bar = "─" * pos + "●" + "─" * (20 - pos)
    return f"`−1 {bar} +1`"


def _score_bar(score: int) -> str:
    """Barre de progression 0-100."""
    filled = int(score / 100 * 20)
    bar = "█" * filled + "░" * (20 - filled)
    return f"`{bar}` **{score}/100**"


# ---------------------------------------------------------------------------
# Interface Gradio
# ---------------------------------------------------------------------------

EXAMPLE_FR = (
    "Pour commencer, je voudrais aborder la question de l'environnement. "
    "Euh, donc, du coup, il est, euh, vraiment essentiel de réduire nos émissions. "
    "Les énergies renouvelables offrent une alternative viable et durable. "
    "En conclusion, agir maintenant est absolument indispensable pour les générations futures."
)

EXAMPLE_EN = (
    "First, I would like to talk about climate change. "
    "So, like, you know, it's basically the most pressing issue of our time. "
    "Renewable energy is a viable and sustainable alternative. "
    "In conclusion, we must act now to protect future generations."
)

with gr.Blocks(title="LinguaScope") as demo:

    gr.Markdown("# LinguaScope\nAnalyse de sentiment et de discours — FR & EN")

    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="Texte à analyser",
                placeholder="Collez ou tapez votre discours ici…",
                lines=8,
            )
            lang_radio = gr.Radio(
                choices=list(LANG_MAP.keys()),
                value="Détection auto",
                label="Langue",
            )
            with gr.Row():
                submit_btn = gr.Button("Analyser", variant="primary")
                clear_btn  = gr.Button("Effacer")

            gr.Examples(
                examples=[[EXAMPLE_FR, "Français"], [EXAMPLE_EN, "Anglais"]],
                inputs=[text_input, lang_radio],
                label="Exemples",
            )

        with gr.Column(scale=3):
            out_summary   = gr.Markdown()
            with gr.Row():
                out_sentiment = gr.Markdown()
                out_speech    = gr.Markdown()
            with gr.Row():
                out_structure = gr.Markdown()
                out_clarity   = gr.Markdown()

    outputs = [out_summary, out_sentiment, out_speech, out_structure, out_clarity]

    submit_btn.click(fn=run_analysis, inputs=[text_input, lang_radio], outputs=outputs)
    text_input.submit(fn=run_analysis, inputs=[text_input, lang_radio], outputs=outputs)
    clear_btn.click(
        fn=lambda: ("", "Détection auto") + ("",) * 5,
        outputs=[text_input, lang_radio] + outputs,
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
