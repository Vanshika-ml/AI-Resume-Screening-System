import re
from functools import lru_cache
 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
 
 
# ---------------------------------------------------------------
# Try to load the semantic model once (cached), fall back cleanly
# ---------------------------------------------------------------
_SEMANTIC_AVAILABLE = True
try:
    from sentence_transformers import SentenceTransformer, util as st_util
except ImportError:
    _SEMANTIC_AVAILABLE = False
 
 
@lru_cache(maxsize=1)
def _get_model():
    """
    Loads the embedding model once and reuses it for every call.
    'all-MiniLM-L6-v2' is small (~80MB), fast, and good enough for
    resume/JD matching — no GPU needed.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")
 
 
def _clean_text(text):
    """Light cleanup so scoring isn't thrown off by extra whitespace/bullets."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[•▪●]", " ", text)
    return text.strip()
 
 
# ---------------------------------------------------------------
# TF-IDF fallback (original method — kept as a safety net)
# ---------------------------------------------------------------
def _tfidf_score(resume_text, jd_text):
    tfidf = TfidfVectorizer(stop_words="english")
    vectors = tfidf.fit_transform([resume_text, jd_text])
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(score * 100, 2)
 
 
# ---------------------------------------------------------------
# Semantic scoring (new method)
# ---------------------------------------------------------------
def _semantic_score(resume_text, jd_text):
    model = _get_model()
 
    # Long resumes can exceed the model's token limit — chunk and
    # average, so nothing important gets silently truncated.
    resume_chunks = _chunk_text(resume_text)
 
    resume_embeddings = model.encode(resume_chunks, convert_to_tensor=True)
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
 
    similarities = st_util.cos_sim(jd_embedding, resume_embeddings)[0]
    best_score = float(similarities.max())
 
    # cosine similarity from sentence embeddings is usually 0.2–0.9 in
    # practice rather than the full 0-1 range, so we rescale gently
    # for a more intuitive 0-100 ATS-style score.
    score = max(0.0, min(1.0, (best_score - 0.2) / 0.6))
    return round(score * 100, 2)
 
 
def _chunk_text(text, max_words=200):
    words = text.split()
    if len(words) <= max_words:
        return [text]
    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]
 
 
# ---------------------------------------------------------------
# Public function used by app.py — signature unchanged
# ---------------------------------------------------------------
def calculate_score(resume_text, jd_text):
    resume_text = _clean_text(resume_text)
    jd_text = _clean_text(jd_text)
 
    if not resume_text or not jd_text:
        return 0.0
 
    if _SEMANTIC_AVAILABLE:
        try:
            return _semantic_score(resume_text, jd_text)
        except Exception:
            # Model failed to load/run (e.g. no internet on first run
            # to download it) — fall back rather than crash the app.
            return _tfidf_score(resume_text, jd_text)
 
    return _tfidf_score(resume_text, jd_text)
