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

    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    if email_match:

        email = email_match.group()

    phone_match = re.search(
        r"(\+91[- ]?)?[6-9]\d{9}",
        text
    )

    if phone_match:

        phone = phone_match.group()

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

def extract_sections(text):

    text_lower = text.lower()

    sections = {

        "Education": [],

        "Experience": [],

        "Projects": [],

        "Certifications": []

    }

    lines = text.split("\n")

    current = None

    for line in lines:

        l = line.strip()

        low = l.lower()

        if "education" in low:

            current = "Education"

            continue

        elif "experience" in low:

            current = "Experience"

            continue

        elif "project" in low:

            current = "Projects"

            continue

        elif "certification" in low or "certificate" in low:

            current = "Certifications"

            continue

        if current and l != "":

            sections[current].append(l)

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