# AI Resume Screening System

A resume screening tool built with Python, NLP, and Streamlit. Upload resumes, paste a job description, and get a match score, skill-gap analysis, and AI-generated feedback.

Built as a learning project to practice applied NLP and GenAI integration — not a production ATS replacement.

## Features

- Upload multiple resumes, ranks them against one job description
- Match score using sentence embeddings (semantic similarity), with a TF-IDF fallback if the embedding model isn't available
- Skill extraction from a ~65-skill list with common alias matching (e.g. "ML" → "machine learning")
- Extracts contact info and resume sections (Education, Experience, Projects, Certifications)
- AI feedback and interview questions generated via Gemini API
- Downloadable PDF report

## Why Semantic Matching Instead of Just TF-IDF

The first version only used TF-IDF, which is pure keyword overlap — "built ML models" wouldn't match a JD asking for "machine learning experience" unless the exact words lined up. Switching to sentence embeddings fixes that, since it compares meaning instead of exact words.

TF-IDF is kept as a fallback in case the embedding model fails to load, so the app degrades instead of crashing.

Ran a small comparison (`evaluate.py`) on a handful of labeled resume/JD pairs to check semantic scoring actually does better than TF-IDF, instead of just assuming it. It's a small sample, not a rigorous benchmark, but it's a starting point.

## Tech Stack

Python, Streamlit, Sentence-Transformers, Scikit-Learn, Google Gemini API, PDFPlumber, Matplotlib, ReportLab

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

Add your Gemini API key to `.streamlit/secrets.toml`:

## Testing

Basic unit tests for skill extraction and ranking:

```bash
pytest -v
```

## Known Limitations

- Skill list is hand-maintained — new tools won't be detected until added manually
- Assumes a mostly single-column resume layout; multi-column PDFs can confuse section detection
- Soft-skill detection is keyword-based, so it won't infer things like "led a team of 5" as leadership

## Screenshots

![Dashboard](screenshots/dashboard1.png)
![Analysis](screenshots/dashboard2.png)
![Ranking](screenshots/dashboard3.png)
![PDF Report](screenshots/dashboard4.png)

## Author

Vanshika Varshney
