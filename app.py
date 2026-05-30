import streamlit as st
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from resume_parser import extract_text
from skill_extractor import extract_skills
from ranking import calculate_score


st.title("AI Resume Screening System")

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
    st.table(ranking_data)

    resume_text = extract_text(resume)

    score = calculate_score(
        resume_text,
        jd
    )

    skills = extract_skills(
        resume_text
    )

    st.subheader("Analysis")

    st.metric(
        "Match Score",
        f"{score}%"
    )

    st.write(
        "Detected Skills:"
    )

    st.write(skills)

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
    st.progress(int(score))

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
        st.warning(
         "Missing Skills: " +
         ", ".join(missing_skills)
        )
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
    pdf_file = "report.pdf"

    c = canvas.Canvas(pdf_file)

    c.drawString(
      100,
      750,
      f"Resume Match Score: {score}%"
    )

    c.save()

    with open(pdf_file, "rb") as f:
       st.download_button(
         "Download PDF Report",
          f,
          file_name="Resume_Report.pdf"
        ) 