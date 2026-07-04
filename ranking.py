from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------------------
# ATS Score Calculation
# -----------------------------------------

def calculate_score(resume_text, job_description):

    documents = [
        resume_text.lower(),
        job_description.lower()
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf[0:1],
        tfidf[1:2]
    )[0][0]

    score = round(similarity * 100, 2)

    return score


# -----------------------------------------
# Rank Multiple Candidates
# -----------------------------------------

def rank_candidates(resume_list, job_description):

    ranked = []

    for candidate in resume_list:

        score = calculate_score(
            candidate["Text"],
            job_description
        )

        candidate["Score"] = score

        ranked.append(candidate)

    ranked = sorted(
        ranked,
        key=lambda x: x["Score"],
        reverse=True
    )

    return ranked


# -----------------------------------------
# Recruiter Decision
# -----------------------------------------

def recruiter_decision(score):

    if score >= 85:
        return "Highly Recommended"

    elif score >= 70:
        return "Recommended"

    elif score >= 55:
        return "Consider"

    else:
        return "Not Recommended"


# -----------------------------------------
# Resume Strength
# -----------------------------------------

def resume_strength(score):

    if score >= 90:
        return "★★★★★ Excellent"

    elif score >= 80:
        return "★★★★ Strong"

    elif score >= 65:
        return "★★★ Average"

    elif score >= 50:
        return "★★ Needs Improvement"

    else:
        return "★ Poor"


# -----------------------------------------
# Skill Match Percentage
# -----------------------------------------

def skill_match(resume_skills, jd_skills):

    if len(jd_skills) == 0:
        return 0

    matched = 0

    for skill in jd_skills:

        if skill.lower() in [
            s.lower() for s in resume_skills
        ]:

            matched += 1

    percentage = round(
        (matched / len(jd_skills)) * 100,
        2
    )

    return percentage


# -----------------------------------------
# Missing Skills
# -----------------------------------------

def missing_skills(resume_skills, jd_skills):

    missing = []

    resume_lower = [
        s.lower()
        for s in resume_skills
    ]

    for skill in jd_skills:

        if skill.lower() not in resume_lower:

            missing.append(skill)

    return missing