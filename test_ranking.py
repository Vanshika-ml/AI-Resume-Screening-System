from ranking import calculate_score
 
 
def test_empty_inputs_return_zero():
    assert calculate_score("", "") == 0.0
    assert calculate_score("Python developer", "") == 0.0
    assert calculate_score("", "Python developer") == 0.0
 
 
def test_identical_text_scores_high():
    text = "Experienced Python developer skilled in machine learning and SQL."
    score = calculate_score(text, text)
    # Identical text should score very high (not necessarily 100,
    # since semantic embeddings rarely hit a perfect 1.0)
    assert score > 70
 
 
def test_completely_unrelated_text_scores_low():
    resume = "Experienced chef specializing in Italian cuisine and pastry."
    jd = "Looking for a backend engineer with Kubernetes and Go experience."
    score = calculate_score(resume, jd)
    assert score < 50
 
 
def test_relevant_match_scores_higher_than_irrelevant():
    jd = "Looking for a Python developer with machine learning experience."
    relevant_resume = "Python developer with 2 years experience in machine learning and pandas."
    irrelevant_resume = "Graphic designer skilled in Photoshop and Illustrator."
 
    relevant_score = calculate_score(relevant_resume, jd)
    irrelevant_score = calculate_score(irrelevant_resume, jd)
 
    assert relevant_score > irrelevant_score
 
 
def test_score_is_within_valid_range():
    resume = "Data scientist with Python, SQL, and statistics background."
    jd = "Hiring a data analyst with SQL and Excel skills."
    score = calculate_score(resume, jd)
    assert 0 <= score <= 100
 
 
def test_long_resume_does_not_crash():
    # Simulates a resume long enough to require chunking
    long_resume = "Python developer with experience in machine learning. " * 300
    jd = "Looking for a Python and machine learning engineer."
    score = calculate_score(long_resume, jd)
    assert 0 <= score <= 100
 
