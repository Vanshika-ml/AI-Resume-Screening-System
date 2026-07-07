# AI Resume Screening System

A resume screening tool built with Python, NLP, and Streamlit. Upload one or more resumes, paste a job description, and get a match score, skill-gap analysis, AI-generated feedback, and a downloadable PDF report.

Built as a learning project to practice applied NLP and GenAI integration — not a production ATS replacement.

## What It Does

- **Ranks multiple resumes** against a single job description and highlights the best match
- **Scores relevance using sentence embeddings** (semantic similarity), with a TF-IDF fallback if the embedding model isn't available
- **Extracts skills** from a ~65-skill list with alias/regex matching (e.g. "ML" → "machine learning")
- **Parses resume sections and contact info** — Education, Experience, Projects, Certifications, email, phone, GitHub, LinkedIn
- **Generates AI feedback and interview questions** via the Gemini API, based on the resume-JD gap
- **Exports a PDF report** summarizing the match score, missing skills, and feedback

## Why Semantic Matching Instead of Just TF-IDF

The first version only used TF-IDF, which is pure keyword overlap — "built ML models" wouldn't match a JD asking for "machine learning experience" unless the exact words lined up. Switching to sentence embeddings fixes that, since it compares meaning instead of exact words.

TF-IDF is kept as a fallback in case the embedding model fails to load, so the app degrades instead of crashing.

Ran a small comparison (`evaluate.py`) on 6 labeled resume/JD pairs to check semantic scoring actually does better than TF-IDF, instead of just assuming it: semantic scoring correctly identified relevant matches in 6/6 cases, vs 3/6 for TF-IDF. It's a small sample, not a rigorous benchmark, but it clearly shows keyword overlap alone misses relevant matches that use different wording.

## Tech Stack

**Language:** Python
**Frontend:** Streamlit
**NLP / ML:** Sentence-Transformers (`all-MiniLM-L6-v2`), Scikit-Learn (TF-IDF fallback)
**GenAI:** Google Gemini API (feedback + interview questions)
**Parsing:** PDFPlumber
**Reporting:** ReportLab, Matplotlib
**Testing:** Pytest

## How It Works

```
Resume (PDF) ──► resume_parser.py ──► sections, contact info, raw text
                                              │
Job Description ─────────────────────────────┼──► ranking.py ──► match score
                                              │      (semantic, TF-IDF fallback)
                                              ├──► skill_extractor.py ──► skills found / missing
                                              │
                                              └──► Gemini API ──► feedback + interview questions
                                                          │
                                                          ▼
                                                  app.py (Streamlit UI + PDF report)
```

## Installation

```bash
git clone https://github.com/Vanshika-ml/AI-Resume-Screening-System.git
cd AI-Resume-Screening-System
pip install -r requirements.txt
```

Add your Gemini API key in `.streamlit/secrets.toml`:

Then run:

```bash
streamlit run app.py
```

## Testing

Unit tests cover skill extraction and ranking logic:

```bash
pytest -v
```

Run the TF-IDF vs semantic comparison:

```bash
python evaluate.py
```

## Known Limitations

- Skill list is hand-maintained — new tools won't be detected until added manually
- Assumes a mostly single-column resume layout; multi-column PDFs can confuse section detection
- Soft-skill detection is keyword-based, so it won't infer things like "led a team of 5" as leadership
- Only the top-ranked resume gets full AI feedback and interview questions; others are shown in the ranking table only

## Possible Next Steps

- Expand the evaluation set beyond 6 pairs for a more reliable accuracy benchmark
- Generate PDF reports in-memory instead of writing to disk
- Surface which alias matched each detected skill, for transparency

## Screenshots

![Dashboard](screenshots/dashboard1.png)
![Analysis](screenshots/dashboard2.png)
![Ranking](screenshots/dashboard3.png)
![PDF Report](screenshots/dashboard4.png)

## Author

**Vanshika Varshney**
[GitHub](https://github.com/Vanshika-ml)
