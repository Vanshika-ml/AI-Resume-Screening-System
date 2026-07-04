import re

# -----------------------------------
# Skill Database
# -----------------------------------

SKILLS = {

    # Programming
    "python","java","c","c++","c#","javascript","typescript",
    "r","matlab","php","go","ruby","swift","kotlin",

    # Data Science
    "numpy","pandas","matplotlib","seaborn","plotly",
    "scipy","statsmodels","scikit-learn","sklearn",

    # Machine Learning
    "machine learning",
    "deep learning",
    "supervised learning",
    "unsupervised learning",
    "reinforcement learning",
    "feature engineering",
    "feature selection",
    "model deployment",
    "cross validation",
    "gridsearchcv",
    "random forest",
    "decision tree",
    "xgboost",
    "lightgbm",
    "catboost",
    "svm",
    "knn",
    "naive bayes",
    "logistic regression",
    "linear regression",

    # AI
    "artificial intelligence",
    "generative ai",
    "llm",
    "gpt",
    "gemini",
    "langchain",
    "rag",
    "huggingface",
    "transformers",

    # NLP
    "nlp",
    "text mining",
    "sentiment analysis",
    "tokenization",
    "bert",

    # Computer Vision
    "opencv",
    "cnn",
    "image processing",
    "object detection",
    "yolo",

    # Frameworks
    "tensorflow",
    "keras",
    "pytorch",

    # Database
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",

    # Visualization
    "power bi",
    "tableau",
    "excel",

    # Cloud
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",

    # Deployment
    "streamlit",
    "flask",
    "fastapi",
    "django",

    # Tools
    "git",
    "github",
    "linux",
    "jira",

    # Soft Skills
    "communication",
    "leadership",
    "problem solving",
    "teamwork",
    "critical thinking",
    "presentation"
}


# -----------------------------------
# Extract Skills
# -----------------------------------

def extract_skills(text):

    text = text.lower()

    found = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):

            found.append(skill.title())

    return sorted(list(set(found)))