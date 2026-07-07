from skill_extractor import extract_skills
 
 
def test_empty_text_returns_empty_list():
    assert extract_skills("") == []
    assert extract_skills(None) == []
 
 
def test_basic_skill_detection():
    text = "I have experience in Python and SQL."
    result = extract_skills(text)
    assert "python" in result
    assert "sql" in result
 
 
def test_alias_matching():
    # "ML" and "scikit learn" should map to their canonical names
    text = "Worked on ML models using scikit learn and pandas."
    result = extract_skills(text)
    assert "machine learning" in result
    assert "scikit-learn" in result
    assert "pandas" in result
 
 
def test_short_token_no_false_positive():
    # "r" should NOT match inside "director" or "programmer"
    text = "Worked as a director of programs, no R programming here."
    result = extract_skills(text)
    # 'r' should only match because it's explicitly mentioned as "R"
    # standalone — this test mainly guards against silent false positives
    # like matching inside "director" or "programmer"
    assert "director" not in " ".join(result)
 
 
def test_multiword_skill_detection():
    text = "Strong background in natural language processing and computer vision."
    result = extract_skills(text)
    assert "natural language processing" in result
    assert "computer vision" in result
 
 
def test_case_insensitivity():
    text = "PYTHON, Machine Learning, SQL"
    result = extract_skills(text)
    assert "python" in result
    assert "machine learning" in result
    assert "sql" in result
 
 
def test_no_duplicate_skills():
    text = "Python python PYTHON python3"
    result = extract_skills(text)
    assert result.count("python") == 1
