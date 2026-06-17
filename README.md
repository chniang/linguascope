---
title: Linguascope
emoji: 🔭
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.18.0
python_version: '3.12'
app_file: app.py
pinned: false
license: mit
---

# LinguaScope

> Analyse de sentiment et de discours en français et en anglais — propulsé par Gradio.

LinguaScope est une application NLP légère qui évalue simultanément le **sentiment** d'un texte (polarité, subjectivité) et la **qualité de son discours** (mots parasites, structure, clarté). Elle prend en charge le français et l'anglais, avec détection automatique de la langue.

---

## Fonctionnalités

| Module | Ce qu'il mesure |
|---|---|
| **Sentiment** | Polarité (−1 → +1), subjectivité (EN), label positif / neutre / négatif |
| **Mots parasites** | Détection et comptage de fillers (euh, du coup, like, you know…) |
| **Structure** | Présence d'une introduction, d'un développement et d'une conclusion |
| **Clarté** | Longueur des phrases, diversité lexicale, score /100 |
| **Feedback** | Retours synthétiques actionnables sur chaque dimension |

---

## Aperçu

| Page d'accueil | Résultats d'analyse (exemple FR) |
|:-:|:-:|
| ![Accueil](https://raw.githubusercontent.com/chniang/linguascope/main/screenshots/01-accueil.png) | ![Résultats](https://raw.githubusercontent.com/chniang/linguascope/main/screenshots/02-resultats-fr.png) |

> Accordion "Comment ça marche" — documentation des 4 modules intégrée dans l'interface
>
> ![Comment ça marche](https://raw.githubusercontent.com/chniang/linguascope/main/screenshots/03-comment-ca-marche.png)

---

## Stack technique

- **[Gradio](https://www.gradio.app/)** — interface web interactive
- **[TextBlob](https://textblob.readthedocs.io/)** — analyse de sentiment EN
- **[textblob-fr](https://github.com/sloria/textblob-fr)** — analyse de sentiment FR (PatternAnalyzer)
- **[langdetect](https://github.com/Mimino666/langdetect)** — détection automatique de la langue
- Python 3.10+

---

## Architecture

```
linguascope/
├── app.py                  # Point d'entrée Gradio (UI + orchestration)
├── src/
│   ├── sentiment.py        # Analyse polarity / subjectivity FR & EN
│   ├── speech.py           # Mots parasites, structure, clarté
│   ├── feedback.py         # Génération des retours textuels
│   └── utils.py            # Tokenisation, TTR, nettoyage de texte
├── data/
│   └── sample_reviews.csv  # Jeu de données de validation interne (voir ci-dessous)
└── requirements.txt
```

### `src/sentiment.py`
Enveloppe TextBlob (EN) et textblob-fr (FR). Renvoie `{language, polarity, subjectivity, label}`.

### `src/speech.py`
Analyse l'oral / le discours : détection des fillers par regex, score de structure sur 3 marqueurs (intro / corps / conclusion), score de clarté sur 100 pénalisé par les phrases longues et la faible diversité lexicale.

### `src/feedback.py`
Agrège les résultats des deux modules et génère des retours lisibles par dimension ainsi qu'une synthèse en une ligne.

### `src/utils.py`
Primitives partagées : `tokenize_words`, `tokenize_sentences`, `lexical_diversity` (Type-Token Ratio), `find_filler_words`.

---

## Lancer l'application en local

```bash
# 1. Cloner le dépôt
git clone https://github.com/chniang/linguascope.git
cd linguascope

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer
python app.py
```

L'interface s'ouvre sur **http://localhost:7860**.

---

## Données de validation

`data/sample_reviews.csv` est un jeu de 20 textes courts (10 FR, 10 EN) couvrant les trois labels de sentiment et différents profils de qualité orale (texte structuré, filler-heavy, neutre).  
Ce fichier sert uniquement à tester les modules en local — il n'est **pas** exposé dans l'interface utilisateur.

| Colonnes | Description |
|---|---|
| `text` | Texte brut |
| `language` | `fr` ou `en` |
| `label` | `positif`, `négatif` ou `neutre` |

---

## Démo

> **Hugging Face Space :** https://huggingface.co/spaces/TIJAANI/linguascope

---

## Licence

MIT
