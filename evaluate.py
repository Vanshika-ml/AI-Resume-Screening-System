from ranking import _semantic_score, _tfidf_score, _clean_text, _SEMANTIC_AVAILABLE
 
# ---------------------------------------------------------------
# STEP 1: Add your own labeled resume/JD pairs here.
# label = 1 means "a human would consider this resume relevant to the JD"
# label = 0 means "a human would consider this resume NOT relevant"
# ---------------------------------------------------------------
LABELED_PAIRS = [
    {
        "resume": "Python developer with 2 years experience in machine learning, "
                  "pandas, scikit-learn, and building REST APIs with FastAPI.",
        "jd": "Looking for a Python developer with machine learning and API "
              "development experience.",
        "label": 1,
    },
    {
        "resume": "Graphic designer with 5 years experience in Photoshop, "
                  "Illustrator, and brand identity design.",
        "jd": "Looking for a Python developer with machine learning and API "
              "development experience.",
        "label": 0,
    },
    {
        "resume": "Data analyst skilled in SQL, Excel, Power BI, and building "
                  "dashboards for business reporting.",
        "jd": "Hiring a data analyst with strong SQL and dashboarding skills.",
        "label": 1,
    },
    {
        "resume": "Mechanical engineer with experience in CAD design and "
                  "manufacturing process optimization.",
        "jd": "Hiring a data analyst with strong SQL and dashboarding skills.",
        "label": 0,
    },
    {
        "resume": "Full-stack developer experienced in React, Node.js, MongoDB, "
                  "and deploying applications on AWS.",
        "jd": "Looking for a full-stack engineer familiar with React and "
              "cloud deployment.",
        "label": 1,
    },
    {
        "resume": "Content writer with experience in SEO, blogging, and "
                  "social media copywriting.",
        "jd": "Looking for a full-stack engineer familiar with React and "
              "cloud deployment.",
        "label": 0,
    },
    # Add more pairs below for a stronger, more convincing evaluation.
]
 
THRESHOLD = 50  # score above this = "predicted relevant"
 
 
def run_evaluation():
    if not _SEMANTIC_AVAILABLE:
        print("sentence-transformers is not installed — install it to run "
              "the full comparison:\n    pip install sentence-transformers")
        return
 
    print(f"{'Label':<8}{'TF-IDF':<10}{'Semantic':<10}{'Resume (truncated)'}")
    print("-" * 70)
 
    tfidf_correct = 0
    semantic_correct = 0
    total = len(LABELED_PAIRS)
 
    for pair in LABELED_PAIRS:
        resume = _clean_text(pair["resume"])
        jd = _clean_text(pair["jd"])
        label = pair["label"]
 
        tfidf_score = _tfidf_score(resume, jd)
        semantic_score = _semantic_score(resume, jd)
 
        tfidf_pred = 1 if tfidf_score >= THRESHOLD else 0
        semantic_pred = 1 if semantic_score >= THRESHOLD else 0
 
        tfidf_correct += int(tfidf_pred == label)
        semantic_correct += int(semantic_pred == label)
 
        preview = pair["resume"][:40] + "..."
        print(f"{label:<8}{tfidf_score:<10}{semantic_score:<10}{preview}")
 
    print("-" * 70)
    print(f"TF-IDF accuracy:   {tfidf_correct}/{total} "
          f"({100 * tfidf_correct / total:.1f}%)")
    print(f"Semantic accuracy: {semantic_correct}/{total} "
          f"({100 * semantic_correct / total:.1f}%)")
 
 
if __name__ == "__main__":
    run_evaluation()
