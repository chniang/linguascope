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
    pos = int((polarity + 1) / 2 * 20)
    pos = max(0, min(20, pos))
    bar = "─" * pos + "●" + "─" * (20 - pos)
    return f"`−1 {bar} +1`"


def _score_bar(score: int) -> str:
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

THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.indigo,
    secondary_hue=gr.themes.colors.purple,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
).set(
    body_background_fill="#0f0f1a",
    body_background_fill_dark="#0f0f1a",
    body_text_color="#e2e8f0",
    body_text_color_dark="#e2e8f0",
    body_text_color_subdued="#94a3b8",
    body_text_color_subdued_dark="#94a3b8",
    block_background_fill="#1e1e2e",
    block_background_fill_dark="#1e1e2e",
    block_border_color="#2d2d44",
    block_border_color_dark="#2d2d44",
    block_label_text_color="#a5b4fc",
    block_label_text_color_dark="#a5b4fc",
    block_title_text_color="#c7d2fe",
    block_title_text_color_dark="#c7d2fe",
    button_primary_background_fill="#6366f1",
    button_primary_background_fill_dark="#6366f1",
    button_primary_background_fill_hover="#4f46e5",
    button_primary_background_fill_hover_dark="#4f46e5",
    button_primary_text_color="#ffffff",
    button_primary_text_color_dark="#ffffff",
    button_secondary_background_fill="#1e1e2e",
    button_secondary_background_fill_dark="#1e1e2e",
    button_secondary_background_fill_hover="#2d2d44",
    button_secondary_background_fill_hover_dark="#2d2d44",
    button_secondary_border_color="#3d3d5c",
    button_secondary_border_color_dark="#3d3d5c",
    button_secondary_text_color="#a5b4fc",
    button_secondary_text_color_dark="#a5b4fc",
    input_background_fill="#13131f",
    input_background_fill_dark="#13131f",
    input_border_color="#2d2d44",
    input_border_color_dark="#2d2d44",
    input_border_color_focus="#6366f1",
    input_border_color_focus_dark="#6366f1",
    input_placeholder_color="#475569",
    input_placeholder_color_dark="#475569",
    slider_color="#6366f1",
    slider_color_dark="#6366f1",
)

_DARK_JS = "() => { document.documentElement.classList.add('dark'); }"

CSS = """
/* ── Header ───────────────────────────────────────────────────────── */
#ls-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #1e1b4b 100%);
    border: 1px solid #3730a3;
    border-radius: 16px;
    padding: 2rem 2rem 1.75rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
    margin-bottom: 1.75rem;
}

#ls-header .ls-logo { font-size: 3rem; line-height: 1; margin-bottom: 0.4rem; }

#ls-header h1 {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #c7d2fe, #a5b4fc, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0.2rem 0 !important;
    letter-spacing: -0.03em;
}

#ls-header p.ls-subtitle {
    color: #94a3b8 !important;
    font-size: 0.95rem !important;
    margin: 0.5rem 0 0 !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Result cards ─────────────────────────────────────────────────── */
.ls-card {
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    transition: box-shadow 0.25s ease, border-color 0.25s ease !important;
}

.ls-card:hover {
    box-shadow: 0 6px 30px rgba(99, 102, 241, 0.18) !important;
    border-color: #4338ca !important;
}

.ls-summary {
    border-color: #4338ca !important;
    box-shadow: 0 4px 28px rgba(99, 102, 241, 0.28) !important;
    border-radius: 12px !important;
    margin-bottom: 1rem !important;
}

/* ── Buttons ──────────────────────────────────────────────────────── */
.ls-btn-primary > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    box-shadow: 0 2px 10px rgba(99, 102, 241, 0.4) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}

.ls-btn-primary > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(99, 102, 241, 0.6) !important;
}

.ls-btn-primary > button:active { transform: translateY(0) !important; }

.ls-btn-secondary > button {
    border-radius: 8px !important;
    transition: transform 0.15s ease, border-color 0.15s ease !important;
}

.ls-btn-secondary > button:hover {
    transform: translateY(-1px) !important;
    border-color: #6366f1 !important;
    color: #a5b4fc !important;
}

/* ── Container & spacing ──────────────────────────────────────────── */
.gradio-container { max-width: 1300px !important; padding: 1.5rem 2rem !important; }

.ls-results-col { gap: 0.85rem !important; }
"""

_HEADER_MD = """<div class="ls-logo">🔭</div>

# LinguaScope

<p class="ls-subtitle">Analyse de sentiment et de discours — FR & EN</p>"""

with gr.Blocks(title="LinguaScope", js=_DARK_JS, css=CSS) as demo:

    gr.Markdown(_HEADER_MD, elem_id="ls-header")

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
                submit_btn = gr.Button("Analyser", variant="primary",
                                       elem_classes=["ls-btn-primary"])
                clear_btn  = gr.Button("Effacer",
                                       elem_classes=["ls-btn-secondary"])

            gr.Examples(
                examples=[[EXAMPLE_FR, "Français"], [EXAMPLE_EN, "Anglais"]],
                inputs=[text_input, lang_radio],
                label="Exemples",
            )

        with gr.Column(scale=3, elem_classes=["ls-results-col"]):
            out_summary   = gr.Markdown(elem_classes=["ls-summary"])
            with gr.Row():
                out_sentiment = gr.Markdown(elem_classes=["ls-card"])
                out_speech    = gr.Markdown(elem_classes=["ls-card"])
            with gr.Row():
                out_structure = gr.Markdown(elem_classes=["ls-card"])
                out_clarity   = gr.Markdown(elem_classes=["ls-card"])

    outputs = [out_summary, out_sentiment, out_speech, out_structure, out_clarity]

    submit_btn.click(fn=run_analysis, inputs=[text_input, lang_radio], outputs=outputs)
    text_input.submit(fn=run_analysis, inputs=[text_input, lang_radio], outputs=outputs)
    clear_btn.click(
        fn=lambda: ("", "Détection auto") + ("",) * 5,
        outputs=[text_input, lang_radio] + outputs,
    )


if __name__ == "__main__":
    demo.launch(theme=THEME)
