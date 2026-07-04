import streamlit as st
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from resume_parser import extract_text,extract_details,extract_sections
from skill_extractor import extract_skills
from ranking import calculate_score
import google.generativeai as genai

genai.configure(api_key="GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")


st.title("AI Resume Screening System")
st.caption(
    "AI Powered ATS Resume Screening & Candidate Ranking System"
)

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric(
    "AI Model",
    "ATS Scanner"
)

col2.metric(
    "Supported",
    "PDF"
)

col3.metric(
    "Version",
    "2.0"
)

jd = st.text_area("Paste Job Description")

resumes = st.file_uploader(
    "Upload Resumes",
    type=["pdf"],
    accept_multiple_files=True
)

if resumes and jd:
    ranking_data = []

    for resume in resumes:

      resume_text = extract_text(resume)
      details = extract_details(resume_text)
      sections = extract_sections(
         resume_text
      )

      score = calculate_score(
        resume_text,
        jd
      )

      ranking_data.append({
        "Resume": resume.name,
        "Score": score
      })

    ranking_data = sorted(
      ranking_data,
      key=lambda x: x["Score"],
      reverse=True
    )

    st.subheader("Candidate Ranking")
    best_candidate = ranking_data[0]

    st.success(
        f"🏆 Best Candidate: {best_candidate['Resume']}"
    )

    st.metric(
       "Highest ATS Score",
       f"{best_candidate['Score']}%"
    )

    st.subheader("Resume Strength")

    if score >= 90:
        st.success("🟢 Excellent Resume")

    elif score >= 75:
        st.success("🟡 Strong Resume")

    elif score >= 60:
        st.warning("🟠 Average Resume")

    else:
        st.error("🔴 Needs Improvement")
    st.table(ranking_data)
    import pandas as pd

    ranking_df = pd.DataFrame(ranking_data)

    st.subheader(
       "Candidate Ranking Chart"
    )

    st.bar_chart(
        ranking_df.set_index("Resume")
    )

    st.subheader(
       "ATS Score Distribution"
    )

    fig, ax = plt.subplots()

    ax.hist(
       ranking_df["Score"],
       bins=10
    )

    st.pyplot(fig)
    col1, col2 = st.columns(2)

    col1.metric(
       "Average ATS Score",
       f"{ranking_df['Score'].mean():.2f}%"
    )

    col2.metric(
       "Total Candidates",
        len(ranking_df)
    )

    st.subheader(
      "Top 5 Candidates"
    )

    top5 = ranking_df.sort_values(
       by="Score",
       ascending=False
    ).head(5)

    st.dataframe(top5)

    resume_text = extract_text(resume)

    score = calculate_score(
        resume_text,
        jd
    )

    skills = extract_skills(
        resume_text
    )
    st.subheader("Candidate Information")
    st.subheader(
        "Resume Summary"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
          "🎓 Education"
        )

        st.write(
          sections["Education"]
        )

        st.write(
           "💼 Experience"
        )

        st.write(
           sections["Experience"]
        )

    with col2:

        st.write(
         "🏆 Certifications"
        )

        st.write(
           sections["Certifications"]
        )

        st.write(
          "📂 Projects"
        )

        st.write(
          sections["Projects"]
        )

    col1, col2 = st.columns(2)

    with col1:
       st.write("📧 Email:", details["Email"])
       st.write("📞 Phone:", details["Phone"])

    with col2:
       st.write("💻 GitHub:", details["GitHub"])
       st.write("🔗 LinkedIn:", details["LinkedIn"])
    
    st.subheader("Analysis")
    st.subheader("Resume Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
      "Skills",
      len(skills)
    )

    col2.metric(
       "Missing Skills",
        len(missing_skills)
    )

    col3.metric(
       "Projects",
        len(sections["Projects"])
    )
    
    completion = (
       (
            len(skills)
            + len(sections["Projects"])
            + len(sections["Education"])
            + len(sections["Experience"])
        )
        * 10
    )

    completion = min(completion, 100)

    st.subheader("Resume Completion")

    st.progress(completion / 100)

    st.write(f"{completion}% Complete")
    st.subheader("ATS Score Breakdown")

    skills_score = min(len(skills) * 10, 40)

    education_score = min(
       len(sections["Education"]) * 15,
       20
    )

    experience_score = min(
      len(sections["Experience"]) * 10,
      20
    )

    project_score = min(
       len(sections["Projects"]) * 5,
      20
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
          "Skills",
          f"{skills_score}/40"
        )

        st.metric(
          "Education",
          f"{education_score}/20"
        )

    with col2:

        st.metric(
            "Experience",
           f"{experience_score}/20"
        )

        st.metric(
          "Projects",
          f"{project_score}/20"
        )
    st.progress(score / 100)

    st.subheader("Resume Strength")

    if score >= 90:

        st.success(
          "★★★★★ Excellent Resume"
        )

    elif score >= 75:

        st.success(
          "★★★★ Strong Resume"
        )

    elif score >= 60:

        st.warning(
         "★★★ Average Resume"
        )

    else:

        st.error(
          "★★ Needs Improvement"
        )
    
    st.subheader("AI Suggestions")
    if st.button("Generate AI Resume Feedback"):

        prompt = f"""
        Analyze this resume.

        Resume:
        {resume_text}

        Job Description:
        {jd}

        Give:

        1. ATS improvement suggestions
        2. Missing skills
        3. Resume strengths
        4. Resume weaknesses
        5. Final recommendation

        Keep the answer concise.
        """

        response = model.generate_content(prompt)

        st.subheader("🤖 AI Resume Feedback")

        st.write(response.text)
 
    suggestions = []

    if len(missing_skills):

        suggestions.append(
           "Add missing technical skills."
        )

    if len(sections["Projects"]) < 2:

        suggestions.append(
           "Include more Machine Learning projects."
        )

    if details["GitHub"] == "Not Found":

        suggestions.append(
          "Add GitHub profile."
        )

    if details["LinkedIn"] == "Not Found":

        suggestions.append(
          "Add LinkedIn profile."
        )

    if len(sections["Certifications"]) == 0:

        suggestions.append(
          "Mention certifications."
        )

    for item in suggestions:

        st.info(item)
        st.subheader("ATS Score")

        st.metric(
           label="ATS Match Score",
           value=f"{score}%"
        )

    st.progress(score / 100)

    st.write(
        "Detected Skills:"
    )

    st.subheader("Detected Skills")

    for skill in skills:
        st.success(f"✅ {skill.title()}")

    if score > 75:
        st.success(
            "Highly Recommended"
        )
    elif score > 50:
        st.warning(
            "Recommended"
        )
    else:
        st.error(
            "Not Recommended"
        )


    st.metric(
      label="Match Score",
      value=f"{score}%"
    )

    st.success(f"Skills Found: {len(skills)}")
    for skill in skills:
        st.write("✅", skill.title())
    jd_skills = extract_skills(jd)

    missing_skills = []

    for skill in jd_skills:
        if skill not in skills:
           missing_skills.append(skill)

    st.subheader("Resume Feedback")

    if missing_skills:
        st.subheader("Missing Skills")

        if missing_skills:
            for skill in missing_skills:
              st.error(f"❌ {skill.title()}")
        else:
            st.success("No Missing Skills Found")
    else:
       st.success(
         "Resume matches all required skills!"
        )        
    st.subheader("Skills Distribution")

    fig, ax = plt.subplots()

    ax.pie(
      [1] * len(skills),
      labels=skills,
      autopct="%1.1f%%"
    )

    st.pyplot(fig)
    st.subheader("Recruiter Decision")

    if score >= 85:

        st.success(
          "🎉 Shortlist Candidate"
        )

    elif score >= 70:

        st.warning(
          "📞 Keep for Interview"
        )

    else:

        st.error(
          "❌ Reject"
        )

    st.subheader(
       "Suggested Interview Questions"
    )

    questions = []

    if "python" in [s.lower() for s in skills]:
        questions.append(
         "Explain Python decorators."
        )

    if "machine learning" in [s.lower() for s in skills]:
        questions.append(
           "Difference between Bagging and Boosting?"
        )

    if "sql" in [s.lower() for s in skills]:
        questions.append(
          "Explain JOINs in SQL."
        )

    if "pandas" in [s.lower() for s in skills]:
        questions.append(
          "Difference between loc and iloc?"
        )

    for q in questions:

      st.write("•", q)    

    pdf_file = "report.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, 800, "AI Resume Screening Report")

    c.setFont("Helvetica", 12)

    c.drawString(50, 760, f"Resume Name: {resume.name}")
    c.drawString(50, 735, f"ATS Match Score: {score}%")

    c.drawString(50, 705, "Detected Skills:")
    y = 685

    for skill in skills:
        c.drawString(70, y, f"• {skill.title()}")
        y -= 18

    c.drawString(50, y-10, "Missing Skills:")
    y -= 30

    c.drawString(
      50,
      y,
      f"Education: {len(sections['Education'])}"
    )

    y -= 20

    c.drawString(
      50,
      y,
      f"Experience: {len(sections['Experience'])}"
    )

    y -= 20

    c.drawString(
      50,
      y,
      f"Projects: {len(sections['Projects'])}"
    )

    y -= 20

    c.drawString(
      50,
      y,
      f"Certifications: {len(sections['Certifications'])}"
    )

    y -= 30
    
    

    if score >= 85:
        recommendation = "Excellent Candidate"

    elif score >= 70:
        recommendation = "Strong Candidate"

    elif score >= 50:
        recommendation = "Average Candidate"

    else:
        recommendation = "Not Recommended"

    c.drawString(50, y, f"Recommendation: {recommendation}")
    
    y -= 30

    c.drawString(
       50,
       y,
      "Suggestions"
    )

    y -= 20

    for item in suggestions:

        c.drawString(
          70,
          y,
          f"- {item}"
        )

    y -= 20
    c.save()

    with open(pdf_file, "rb") as f:
       st.download_button(
           "📄 Download PDF Report",
           f,
           file_name="Resume_Report.pdf",
           mime="application/pdf"
        )