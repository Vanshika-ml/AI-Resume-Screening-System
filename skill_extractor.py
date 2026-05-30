skills_list = [
    "python","machine learning","sql",
    "tensorflow","pandas","numpy",
    "data analysis","deep learning",
    "power bi","excel","java"
]

def extract_skills(text):
    text = text.lower()
    found = []

    for skill in skills_list:
        if skill in text:
            found.append(skill)

    return list(set(found))