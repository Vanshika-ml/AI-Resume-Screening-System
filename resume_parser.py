import pdfplumber
import re

# -----------------------------
# Extract Resume Text
# -----------------------------
def extract_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# -----------------------------
# Extract Contact Details
# -----------------------------
def extract_details(text):
    email = "Not Found"
    phone = "Not Found"
    github = "Not Found"
    linkedin = "Not Found"

    # TLD is matched against a whitelist (instead of a bare [A-Za-z]{2,})
    # so that words glued onto the email by PDF text extraction (e.g.
    # "test@test.comPhone:...") don't get swallowed into the match.
    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\."
        r"(?:com|in|org|net|edu|co|io|ai|gov|info|biz|me|dev)\b",
        text,
        re.IGNORECASE
    )
    if email_match:
        email = email_match.group()

    # Broader phone matching: Indian numbers (with/without +91),
    # and general international formats with optional country code,
    # spaces, dashes, or parentheses.
    phone_patterns = [
        r"(\+91[-\s]?)?[6-9]\d{9}",                       # India
        r"\+\d{1,3}[-\s]?\(?\d{2,4}\)?[-\s]?\d{3,4}[-\s]?\d{3,4}",  # generic intl
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = phone_match.group().strip()
            break

    github_match = re.search(
        r"github\.com/[A-Za-z0-9_.-]+",
        text,
        re.IGNORECASE
    )
    if github_match:
        github = github_match.group()

    linkedin_match = re.search(
        r"linkedin\.com/in/[A-Za-z0-9_-]+",
        text,
        re.IGNORECASE
    )
    if linkedin_match:
        linkedin = linkedin_match.group()

    return {
        "Email": email,
        "Phone": phone,
        "GitHub": github,
        "LinkedIn": linkedin
    }


# -----------------------------
# Resume Sections
# -----------------------------

# Each canonical section maps to the different heading words resumes
# commonly use for it. Add more synonyms here anytime a resume format
# slips through.
SECTION_SYNONYMS = {
    "Education": [
        "education", "academic background", "academics",
        "qualification", "educational qualification", "academic details"
    ],
    "Experience": [
        "experience", "work experience", "work history",
        "employment history", "employment", "professional experience",
        "internship", "internships"
    ],
    "Projects": [
        "project", "projects", "key projects", "academic projects",
        "personal projects", "major projects"
    ],
    "Certifications": [
        "certification", "certifications", "certificate", "certificates",
        "licenses", "courses & certifications", "achievements",
        "training"
    ],
}

# Headings that mark the START of a section we don't care about,
# so we stop dumping lines into the previous section once we hit one.
# (Otherwise e.g. a "Skills" section right after "Experience" would
# get swallowed into Experience.)
KNOWN_OTHER_HEADINGS = [
    "skills", "technical skills", "summary", "objective",
    "contact", "languages", "hobbies", "interests", "references",
    "declaration", "personal details"
]


def _clean_line(line):
    """Remove bullet symbols and excess whitespace from a line."""
    line = re.sub(r"^[•▪●\-\*\u2022]+\s*", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def _match_heading(line_lower):
    """
    Returns the canonical section name if this line looks like a
    section heading (short line, matches a known synonym), else None.
    """
    # Heading lines are typically short — a long sentence containing
    # the word "project" (e.g. "I built a project using...") should
    # NOT be treated as a heading.
    if len(line_lower) > 40:
        return None

    # A heading line should BE the heading (optionally with a trailing
    # colon), not just start with the word — otherwise short bullets
    # like "Project: Churn model in Python" under Experience get
    # mistaken for a new "Projects" section header.
    for canonical, synonyms in SECTION_SYNONYMS.items():
        for syn in synonyms:
            if line_lower == syn or line_lower.rstrip(":").strip() == syn:
                return canonical

    for other in KNOWN_OTHER_HEADINGS:
        if line_lower == other or line_lower.rstrip(":").strip() == other:
            return "__OTHER__"

    return None


def extract_sections(text):
    sections = {
        "Education": [],
        "Experience": [],
        "Projects": [],
        "Certifications": []
    }

    lines = text.split("\n")
    current = None

    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line:
            continue

        low = line.lower().strip(" :-")
        heading = _match_heading(low)

        if heading == "__OTHER__":
            current = None
            continue
        elif heading is not None:
            current = heading
            continue

        if current and line:
            sections[current].append(line)

    return sections


# -----------------------------
# Resume Statistics
# -----------------------------
def get_resume_statistics(text):
    words = len(text.split())
    characters = len(text)
    sentences = len(re.findall(r"[.!?]", text))
    return {
        "Words": words,
        "Characters": characters,
        "Sentences": sentences
    }


# -----------------------------
# Resume Completion Score
# -----------------------------
def completion_score(sections):
    score = 0
    if len(sections["Education"]) > 0:
        score += 25
    if len(sections["Experience"]) > 0:
        score += 25
    if len(sections["Projects"]) > 0:
        score += 25
    if len(sections["Certifications"]) > 0:
        score += 25
    return score


# -----------------------------
# Resume Strength
# -----------------------------
def resume_strength(score):
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Strong"
    elif score >= 60:
        return "Average"
    else:
        return "Needs Improvement"