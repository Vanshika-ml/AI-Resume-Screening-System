import pdfplumber
import re

def extract_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_details(text):

    details = {}

    email = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    phone = re.findall(
        r"\+?\d[\d\s-]{8,}\d",
        text
    )

    github = re.findall(
        r"github\.com/[A-Za-z0-9_.-]+",
        text,
        re.IGNORECASE
    )

    linkedin = re.findall(
        r"linkedin\.com/in/[A-Za-z0-9_-]+",
        text,
        re.IGNORECASE
    )

    details["Email"] = email[0] if email else "Not Found"
    details["Phone"] = phone[0] if phone else "Not Found"
    details["GitHub"] = github[0] if github else "Not Found"
    details["LinkedIn"] = linkedin[0] if linkedin else "Not Found"

    return details

def extract_sections(text):

    text = text.lower()

    education = []

    experience = []

    certifications = []

    projects = []

    education_keywords = [
        "b.tech",
        "bachelor",
        "master",
        "m.tech",
        "b.e",
        "degree",
        "university",
        "college"
    ]

    experience_keywords = [
        "intern",
        "experience",
        "worked",
        "company",
        "employment"
    ]

    certification_keywords = [
        "certificate",
        "certification",
        "coursera",
        "udemy",
        "microsoft",
        "google"
    ]

    project_keywords = [
        "project",
        "developed",
        "implemented",
        "built",
        "created"
    ]

    for word in education_keywords:
        if word in text:
            education.append(word)

    for word in experience_keywords:
        if word in text:
            experience.append(word)

    for word in certification_keywords:
        if word in text:
            certifications.append(word)

    for word in project_keywords:
        if word in text:
            projects.append(word)

    return {
        "Education": education,
        "Experience": experience,
        "Certifications": certifications,
        "Projects": projects
    }