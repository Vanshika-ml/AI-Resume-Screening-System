import json
import time

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
from reportlab.pdfgen import canvas

from resume_parser import (
    extract_text,
    extract_details,
    extract_sections
)
from skill_extractor import extract_skills
from ranking import calculate_score

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)

# -------------------------------
# Gemini API
# -------------------------------
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)
model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def call_gemini_with_retry(prompt, max_retries=3):
    """
    Calls Gemini with automatic retry + exponential backoff for
    transient errors (like rate limits / 429s). Returns the response
    text, or raises the last error if every retry fails.
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            error_text = str(e)
            # Only worth retrying on rate-limit / transient errors —
            # no point retrying on a bad API key, for example.
            if "429" in error_text or "quota" in error_text.lower():
                wait_time = (2 ** attempt) + 1  # 2s, 3s, 5s...
                time.sleep(wait_time)
                continue
            else:
                raise
    raise last_error


def get_ai_analysis(resume_text, jd_text):
    """
    Single combined Gemini call that returns BOTH the resume feedback
    AND the interview questions in one structured JSON response.
    This replaces two separate API calls with one, cutting Gemini
    quota usage in half per resume screened.
    """
    prompt = f"""
You are an ATS Resume Expert and technical interviewer.

Job Description:
{jd_text}

Resume:
{resume_text}

Return ONLY valid JSON (no markdown, no code fences, no extra text)
in exactly this structure:

{{
  "overall_ats_score": <number 0-100>,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "missing_skills": ["...", "..."],
  "resume_improvements": ["...", "..."],
  "recruiter_decision": "Shortlist" or "Reject",
  "interview_questions": ["...", "...", "...", "...", "..."]
}}
"""
    raw_text = call_gemini_with_retry(prompt)

    # Strip accidental markdown code fences if the model adds them
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    return json.loads(cleaned)


# -------------------------------
# Header
# -------------------------------
st.title("🤖 AI Resume Screening System")
st.markdown(
    """
    Professional ATS Resume Screening
    with Candidate Ranking & AI Feedback
    """
)
st.divider()

# -------------------------------
# Dashboard
# -------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("AI Model", "Gemini")
c2.metric("Supported", "PDF")
c3.metric("Version", "4.0")
st.divider()

# -------------------------------
# Job Description
# -------------------------------
jd = st.text_area("📋 Paste Job Description", height=220)

# -------------------------------
# Resume Upload
# -------------------------------
uploaded_files = st.file_uploader(
    "📄 Upload Resume(s)",
    type=["pdf"],
    accept_multiple_files=True
)

# -------------------------------
# Start Screening
# -------------------------------
if uploaded_files and jd:

    ranking_data = []
    for resume in uploaded_files:
        resume_text = extract_text(resume)
        details = extract_details(resume_text)
        sections = extract_sections(resume_text)
        skills = extract_skills(resume_text)
        score = calculate_score(resume_text, jd)

        ranking_data.append({
            "Resume": resume.name,
            "Score": score,
            "Skills": skills,
            "Details": details,
            "Sections": sections,
            "Text": resume_text
        })

    ranking_data = sorted(ranking_data, key=lambda x: x["Score"], reverse=True)

    st.subheader("🏆 Candidate Ranking")
    ranking_df = pd.DataFrame([
        {"Resume": x["Resume"], "Score": x["Score"]}
        for x in ranking_data
    ])
    st.dataframe(ranking_df, use_container_width=True)

    best = ranking_data[0]
    st.success(f"Best Candidate : {best['Resume']}")
    st.metric("Highest ATS Score", f"{best['Score']}%")
    st.bar_chart(ranking_df.set_index("Resume"))
    st.divider()

    resume_text = best["Text"]
    details = best["Details"]
    sections = best["Sections"]
    skills = best["Skills"]
    score = best["Score"]

    # -------------------------------
    # Candidate Information
    # -------------------------------
    st.subheader("👤 Candidate Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write("📧 Email")
        st.info(details["Email"])
        st.write("📞 Phone")
        st.info(details["Phone"])
    with col2:
        st.write("💻 GitHub")
        st.info(details["GitHub"])
        st.write("🔗 LinkedIn")
        st.info(details["LinkedIn"])

    # -------------------------------
    # Resume Summary
    # -------------------------------
    st.subheader("📄 Resume Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.write("🎓 Education")
        if sections["Education"]:
            for item in sections["Education"]:
                st.success(item)
        else:
            st.warning("Not Found")

        st.write("💼 Experience")
        if sections["Experience"]:
            for item in sections["Experience"]:
                st.success(item)
        else:
            st.warning("Not Found")

    with col2:
        st.write("📂 Projects")
        if sections["Projects"]:
            for item in sections["Projects"]:
                st.success(item)
        else:
            st.warning("Not Found")

        st.write("🏆 Certifications")
        if sections["Certifications"]:
            for item in sections["Certifications"]:
                st.success(item)
        else:
            st.warning("Not Found")

    st.divider()

    # -------------------------------
    # Resume Statistics
    # -------------------------------
    jd_skills = extract_skills(jd)
    missing_skills = [s for s in jd_skills if s not in skills]

    st.subheader("📊 Resume Statistics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Skills", len(skills))
    c2.metric("Missing Skills", len(missing_skills))
    c3.metric("Projects", len(sections["Projects"]))

    completion = (
        len(skills)
        + len(sections["Projects"])
        + len(sections["Education"])
        + len(sections["Experience"])
    ) * 10
    completion = min(completion, 100)

    st.subheader("✅ Resume Completion")
    st.progress(completion / 100)
    st.write(f"{completion}% Complete")
    st.divider()

    # -------------------------------
    # ATS Breakdown
    # -------------------------------
    st.subheader("📈 ATS Score Breakdown")
    skills_score = min(len(skills) * 10, 40)
    education_score = min(len(sections["Education"]) * 15, 20)
    experience_score = min(len(sections["Experience"]) * 10, 20)
    project_score = min(len(sections["Projects"]) * 5, 20)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Skills", f"{skills_score}/40")
        st.metric("Education", f"{education_score}/20")
    with c2:
        st.metric("Experience", f"{experience_score}/20")
        st.metric("Projects", f"{project_score}/20")

    st.progress(score / 100)
    st.metric("ATS Match Score", f"{score}%")
    st.divider()

    # -------------------------------
    # Resume Strength
    # -------------------------------
    st.subheader("💪 Resume Strength")
    if score >= 90:
        st.success("★★★★★ Excellent Resume")
    elif score >= 75:
        st.success("★★★★ Strong Resume")
    elif score >= 60:
        st.warning("★★★ Average Resume")
    else:
        st.error("★★ Needs Improvement")

    # ------------------------------------------
    # AI Resume Feedback + Interview Questions
    # (single combined Gemini call)
    # ------------------------------------------
    st.divider()
    st.subheader("🤖 AI Resume Feedback")

    ai_result = None
    try:
        with st.spinner("Analyzing resume with Gemini..."):
            ai_result = get_ai_analysis(resume_text, jd)
    except Exception as e:
        st.error(
            "AI feedback is temporarily unavailable "
            "(the Gemini free tier has a daily request limit). "
            "Everything else above is unaffected."
        )
        with st.expander("Error details"):
            st.code(str(e))

    if ai_result:
        st.metric("Gemini ATS Score", f"{ai_result.get('overall_ats_score', 'N/A')}/100")

        col1, col2 = st.columns(2)
        with col1:
            st.write("✅ Strengths")
            for item in ai_result.get("strengths", []):
                st.success(item)
        with col2:
            st.write("⚠️ Weaknesses")
            for item in ai_result.get("weaknesses", []):
                st.warning(item)

        st.write("🧩 Missing Skills (per AI)")
        for item in ai_result.get("missing_skills", []):
            st.info(item)

        st.write("💡 Resume Improvements")
        for item in ai_result.get("resume_improvements", []):
            st.info(item)

        decision = ai_result.get("recruiter_decision", "N/A")
        if decision.lower() == "shortlist":
            st.success(f"Recruiter Decision: {decision}")
        else:
            st.error(f"Recruiter Decision: {decision}")

    # ------------------------------------------
    # Missing Skills (keyword-based, always shown)
    # ------------------------------------------
    st.divider()
    st.subheader("❌ Missing Skills")
    if len(missing_skills) == 0:
        st.success("Excellent! No missing skills found.")
    else:
        for skill in missing_skills:
            st.warning(f"• {skill}")

    # ------------------------------------------
    # Resume Suggestions
    # ------------------------------------------
    st.divider()
    st.subheader("💡 Resume Suggestions")
    suggestions = []
    if len(sections["Projects"]) < 2:
        suggestions.append("Add more Machine Learning projects.")
    if len(sections["Experience"]) == 0:
        suggestions.append("Add internship or work experience.")
    if len(missing_skills) > 0:
        suggestions.append("Add missing skills mentioned above.")
    if len(sections["Certifications"]) == 0:
        suggestions.append("Add relevant certifications.")

    if len(suggestions) == 0:
        st.success("Your resume looks strong.")
    else:
        for s in suggestions:
            st.info(s)

    # ------------------------------------------
    # Skills
    # ------------------------------------------
    st.divider()
    st.subheader("🛠 Skills Detected")
    for skill in skills:
        st.success(skill)

    # ------------------------------------------
    # Skill Distribution Chart
    # ------------------------------------------
    st.divider()
    st.subheader("📊 Skill Distribution")
    if len(skills) > 0:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie([1] * len(skills), labels=skills, autopct="%1.1f%%")
        st.pyplot(fig)

    # ------------------------------------------
    # Recruiter Decision (rule-based, always shown)
    # ------------------------------------------
    st.divider()
    st.subheader("👨‍💼 Recruiter Decision")
    if score >= 85:
        st.success("✅ Highly Recommended")
    elif score >= 70:
        st.warning("🟡 Recommended")
    else:
        st.error("❌ Not Recommended")

    # ------------------------------------------
    # AI Interview Questions (from combined call)
    # ------------------------------------------
    st.divider()
    st.subheader("🎯 AI Interview Questions")
    if ai_result and ai_result.get("interview_questions"):
        for i, q in enumerate(ai_result["interview_questions"], start=1):
            st.write(f"{i}. {q}")
    else:
        st.info("Interview questions unavailable (AI feedback did not load).")

    # ------------------------------------------
    # PDF Report Generation
    # ------------------------------------------
    st.divider()
    st.subheader("📄 Generate PDF Report")

    pdf_file = "Resume_Report.pdf"
    c = canvas.Canvas(pdf_file)
    y = 800

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "AI Resume Screening Report")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Candidate : {best['Resume']}")
    y -= 25
    c.drawString(50, y, f"ATS Score : {score}%")
    y -= 25
    c.drawString(50, y, f"Skills Found : {len(skills)}")
    y -= 25
    c.drawString(50, y, f"Missing Skills : {len(missing_skills)}")
    y -= 40

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Candidate Details")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Email : {details['Email']}")
    y -= 20
    c.drawString(50, y, f"Phone : {details['Phone']}")
    y -= 20
    c.drawString(50, y, f"GitHub : {details['GitHub']}")
    y -= 20
    c.drawString(50, y, f"LinkedIn : {details['LinkedIn']}")
    y -= 35

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Resume Statistics")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Education : {len(sections['Education'])}")
    y -= 20
    c.drawString(50, y, f"Experience : {len(sections['Experience'])}")
    y -= 20
    c.drawString(50, y, f"Projects : {len(sections['Projects'])}")
    y -= 20
    c.drawString(50, y, f"Certifications : {len(sections['Certifications'])}")
    y -= 35

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Missing Skills")
    y -= 25
    c.setFont("Helvetica", 11)
    if len(missing_skills) == 0:
        c.drawString(70, y, "No Missing Skills")
        y -= 20
    else:
        for skill in missing_skills:
            c.drawString(70, y, f"- {skill}")
            y -= 18
    y -= 20

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Resume Suggestions")
    y -= 25
    c.setFont("Helvetica", 11)
    if len(suggestions) == 0:
        c.drawString(70, y, "Resume looks excellent.")
    else:
        for item in suggestions:
            c.drawString(70, y, f"- {item}")
            y -= 18
    y -= 25

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Recruiter Decision")
    y -= 25
    c.setFont("Helvetica", 12)
    if score >= 85:
        rule_decision = "Highly Recommended"
    elif score >= 70:
        rule_decision = "Recommended"
    else:
        rule_decision = "Not Recommended"
    c.drawString(70, y, rule_decision)

    c.save()

    with open(pdf_file, "rb") as f:
        st.download_button(
            "📥 Download PDF Report",
            f,
            file_name="Resume_Report.pdf"
        )

    # ------------------------------------------
    # Final Dashboard
    # ------------------------------------------
    st.divider()
    st.subheader("📊 Final Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ATS Score", f"{score}%")
    col2.metric("Skills", len(skills))
    col3.metric("Missing", len(missing_skills))
    col4.metric("Projects", len(sections["Projects"]))

    st.success("✅ Resume Screening Completed Successfully!")
    st.balloons()

    st.divider()
    st.caption(
        "Built with ❤️ using Python, Streamlit, Scikit-Learn, "
        "Sentence-Transformers, Google Gemini AI, Pandas, "
        "Matplotlib & ReportLab"
    )