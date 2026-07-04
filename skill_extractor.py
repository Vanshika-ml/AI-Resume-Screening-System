import re

# -----------------------------------------------------------
# Skill Database
# -----------------------------------------------------------
# Key   = canonical skill name (what gets shown/reported)
# Value = list of aliases/variations that should also match
#
# Add more skills here anytime — just add a new key with its
# common spelling variations as aliases.
# -----------------------------------------------------------

SKILL_DB = {
    # Programming Languages
    "python": ["python", "python3"],
    "java": ["java"],
    "c++": ["c\\+\\+", "cpp"],
    "c": ["\\bc\\b"],
    "javascript": ["javascript", "js\\b"],
    "typescript": ["typescript", "ts\\b"],
    "sql": ["sql"],
    "r": ["\\br\\b(?!\\w)"],
    "php": ["php"],
    "go": ["golang", "\\bgo\\b"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    "scala": ["scala"],

    # Data Science / ML / AI
    "machine learning": ["machine learning", "\\bml\\b"],
    "deep learning": ["deep learning", "\\bdl\\b"],
    "natural language processing": ["natural language processing", "\\bnlp\\b"],
    "computer vision": ["computer vision", "\\bcv\\b"],
    "data analysis": ["data analysis", "data analytics"],
    "data science": ["data science"],
    "statistics": ["statistics", "statistical analysis"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch", "torch"],
    "keras": ["keras"],
    "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "opencv": ["opencv", "cv2"],
    "xgboost": ["xgboost"],
    "hugging face": ["hugging face", "huggingface", "transformers"],
    "llm": ["large language model", "\\bllm\\b", "llms"],
    "generative ai": ["generative ai", "genai", "gen ai"],

    # Web Development
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react\\.js", "reactjs", "\\breact\\b"],
    "node.js": ["node\\.js", "nodejs", "\\bnode\\b"],
    "express.js": ["express\\.js", "expressjs", "\\bexpress\\b"],
    "django": ["django"],
    "flask": ["flask"],
    "streamlit": ["streamlit"],
    "fastapi": ["fastapi"],
    "next.js": ["next\\.js", "nextjs"],
    "angular": ["angular"],
    "vue": ["vue\\.js", "vuejs", "\\bvue\\b"],
    "rest api": ["rest api", "restful api", "rest apis"],

    # Databases
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo"],
    "sqlite": ["sqlite"],
    "firebase": ["firebase"],
    "redis": ["redis"],
    "oracle": ["oracle db", "oracle database"],

    # Cloud / DevOps
    "aws": ["amazon web services", "\\baws\\b"],
    "azure": ["microsoft azure", "\\bazure\\b"],
    "gcp": ["google cloud platform", "\\bgcp\\b", "google cloud"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "\\bk8s\\b"],
    "git": ["\\bgit\\b"],
    "github": ["github"],
    "ci/cd": ["ci/cd", "ci cd", "continuous integration"],
    "linux": ["linux"],

    # BI / Visualization Tools
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "ms excel"],
    "google sheets": ["google sheets"],

    # Software Engineering / Other
    "data structures": ["data structures"],
    "algorithms": ["algorithms"],
    "object oriented programming": ["object oriented programming", "\\boop\\b"],
    "agile": ["agile", "scrum"],
    "api development": ["api development"],
    "testing": ["unit testing", "test automation"],
    "communication": ["communication skills"],
    "leadership": ["leadership"],
    "problem solving": ["problem solving", "problem-solving"],
}


def extract_skills(text):
    """
    Extract canonical skill names found in the given text.

    Uses word-boundary aware regex matching so short/common tokens
    (like 'r', 'go', 'c') don't false-positive match inside other
    words (e.g. 'r' inside 'director'), and so multi-word skills and
    common aliases/abbreviations are all recognized under one
    canonical name.
    """
    if not text:
        return []

    text_lower = text.lower()
    found = []

    for canonical_name, patterns in SKILL_DB.items():
        for pattern in patterns:
            # Wrap simple alphanumeric patterns with word boundaries;
            # patterns that already define their own boundaries
            # (contain \b or lookaheads) are used as-is.
            if "\\b" in pattern or "(?!" in pattern:
                regex = pattern
            else:
                regex = r"\b" + pattern + r"\b"

            if re.search(regex, text_lower):
                found.append(canonical_name)
                break  # no need to check other aliases for this skill

    return sorted(set(found))


def get_skill_categories():
    """Optional helper: returns the skill database for reference/UI use."""
    return SKILL_DB