# app.py — Point d'entrée Gradio pour LinguaScope

import gradio as gr
from src import sentiment as sentiment_mod
from src import speech as speech_mod
from src import feedback as feedback_mod

# ---------------------------------------------------------------------------
# Logique métier
# ---------------------------------------------------------------------------

LANG_MAP = {"Détection auto": None, "Français": "fr", "Anglais": "en"}


def run_analysis(text: str, lang_choice: str) -> tuple:
    """
    Orchestre les trois modules et retourne 7 valeurs pour les composants Gradio :
    summary_md, polarity_float, sentiment_md, speech_md,
    structure_md, clarity_md, clarity_score_int
    """
    if not text or not text.strip():
        empty = "_Entrez un texte pour lancer l'analyse._"
        return empty, 0.0, empty, empty, empty, empty, 0

    lang = LANG_MAP.get(lang_choice)

    sent = sentiment_mod.analyze(text, lang=lang)
    spch = speech_mod.analyze(text, lang=sent["language"] if lang is None else lang)
    fb   = feedback_mod.generate(sent, spch)

    return (
        _render_summary(fb["summary"], sent),
        sent["polarity"],
        _render_sentiment(fb["sentiment"], sent),
        _render_speech(fb, spch),
        _render_structure(fb["structure"], spch),
        _render_clarity(fb["clarity"], spch),
        spch["clarity"]["clarity_score"],
    )


# ---------------------------------------------------------------------------
# Rendus Markdown
# ---------------------------------------------------------------------------

def _render_summary(summary: str, sent: dict) -> str:
    lang_label = {"fr": "Français", "en": "Anglais"}.get(sent["language"], "Inconnu")
    polarity = sent["polarity"]
    pol_color = "#22c55e" if polarity > 0.1 else "#ef4444" if polarity < -0.1 else "#94a3b8"
    return (
        f"### Synthèse\n"
        f"{summary}\n\n"
        f"**Langue détectée :** {lang_label} &nbsp;·&nbsp; "
        f'**Polarité** <span style="color:{pol_color};font-weight:700">{polarity:+.4f}</span>'
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
    body = "\n\n".join(lines)
    return f"### Clarté\n{body}"


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

# Force dark mode + polling accent-color dynamique sur les sliders
_DARK_JS = """() => {
    document.documentElement.classList.add('dark');

    function lerp(a, b, t) { return a + (b - a) * t; }

    function pctToColor(pct) {
        const r = pct < 0.5 ? 239 : Math.round(lerp(239, 34,  (pct - 0.5) * 2));
        const g = pct < 0.5 ? Math.round(lerp(68, 197, pct * 2)) : 197;
        const b = 68;
        return `rgb(${r},${g},${b})`;
    }

    setInterval(() => {
        const pol = document.querySelector('.ls-slider-polarity input[type="range"]');
        if (pol) pol.style.accentColor = pctToColor((parseFloat(pol.value) + 1) / 2);

        const clr = document.querySelector('.ls-slider-clarity input[type="range"]');
        if (clr) clr.style.accentColor = pctToColor(parseFloat(clr.value) / 100);
    }, 150);
}"""

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

/* ── Sliders (gradient track + accent-color via JS) ──────────────── */
.ls-slider-polarity input[type="range"],
.ls-slider-clarity  input[type="range"] {
    cursor: default !important;
    height: 6px;
}

.ls-slider-polarity input[type="range"]::-webkit-slider-runnable-track {
    background: linear-gradient(to right, #ef4444 0%, #64748b 50%, #22c55e 100%);
    height: 6px; border-radius: 4px;
}
.ls-slider-polarity input[type="range"]::-moz-range-track {
    background: linear-gradient(to right, #ef4444 0%, #64748b 50%, #22c55e 100%);
    height: 6px; border-radius: 4px;
}

.ls-slider-clarity input[type="range"]::-webkit-slider-runnable-track {
    background: linear-gradient(to right, #ef4444 0%, #f59e0b 45%, #22c55e 100%);
    height: 6px; border-radius: 4px;
}
.ls-slider-clarity input[type="range"]::-moz-range-track {
    background: linear-gradient(to right, #ef4444 0%, #f59e0b 45%, #22c55e 100%);
    height: 6px; border-radius: 4px;
}

/* ── Examples table ───────────────────────────────────────────────── */
.table-wrap {
    background-color: #0f0f1a !important;
    border: 1px solid #2d2d44 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

.table-wrap table {
    background-color: #0f0f1a !important;
}

.table-wrap th {
    background-color: #1e1e2e !important;
    color: #a5b4fc !important;
    border-bottom: 1px solid #2d2d44 !important;
    padding: 0.5rem 0.75rem !important;
    font-weight: 600 !important;
}

.table-wrap td {
    background-color: #13131f !important;
    color: #e2e8f0 !important;
    border-color: #1e1e2e !important;
    padding: 0.45rem 0.75rem !important;
}

.table-wrap td span,
.table-wrap td .table {
    color: #e2e8f0 !important;
    background: transparent !important;
}

.table-wrap tbody tr:hover td {
    background-color: #1e1e2e !important;
    cursor: pointer !important;
}

/* ── Container & spacing ──────────────────────────────────────────── */
.gradio-container { width: 100% !important; max-width: 100% !important; padding: 1.5rem 2.5rem !important; box-sizing: border-box !important; }

/* Gradio inner wrapper — also caps width, must be overridden */
.main.fillable { max-width: 100% !important; }

@media (max-width: 640px) {
    .gradio-container { padding: 1rem 1rem !important; }
}

.ls-results-col { gap: 0.85rem !important; }
"""

_HEADER_MD = """<div class="ls-logo">🔭</div>

# LinguaScope

<p class="ls-subtitle">Analyse de sentiment et de discours — FR & EN</p>"""

with gr.Blocks(title="LinguaScope", js=_DARK_JS, css=CSS, fill_width=False) as demo:

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
            out_summary     = gr.Markdown(elem_classes=["ls-summary"])
            slider_polarity = gr.Slider(
                minimum=-1, maximum=1, step=0.0001, value=0,
                interactive=False, label="Polarité  ( −1 négatif · 0 neutre · +1 positif )",
                elem_classes=["ls-slider-polarity"],
            )
            with gr.Row():
                out_sentiment = gr.Markdown(elem_classes=["ls-card"])
                out_speech    = gr.Markdown(elem_classes=["ls-card"])
            with gr.Row():
                out_structure = gr.Markdown(elem_classes=["ls-card"])
                out_clarity   = gr.Markdown(elem_classes=["ls-card"])
            slider_clarity = gr.Slider(
                minimum=0, maximum=100, step=1, value=0,
                interactive=False, label="Score de clarté  ( 0 insuffisant · 100 excellent )",
                elem_classes=["ls-slider-clarity"],
            )

    outputs = [out_summary, slider_polarity, out_sentiment, out_speech,
               out_structure, out_clarity, slider_clarity]

    submit_btn.click(fn=run_analysis, inputs=[text_input, lang_radio], outputs=outputs)
    text_input.submit(fn=run_analysis, inputs=[text_input, lang_radio], outputs=outputs)
    clear_btn.click(
        fn=lambda: ("", "Détection auto", "", 0.0, "", "", "", "", 0),
        outputs=[text_input, lang_radio] + outputs,
    )


if __name__ == "__main__":
    demo.launch(theme=THEME)
