from pathlib import Path

import streamlit as st
from PIL import Image

# --- PATH SETTINGS ----
# creates starting point of app as the current dir
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "assets" / "css" / "cv.css"
resume_file = current_dir / "assets" / "docs" / "JohnWalsheCVpdf.pdf"


# --- GENERAL SETTINGS ---
PAGE_TITLE = "Digital CV | John Walshe"
PAGE_ICON = ":wave:"
NAME = "John Walshe"
DESCRIPTION = """
Junior Software Developer
"""
EMAIL = "jwalshedev@gmail.com"
SOCIAL_MEDIA = {
    "LinkedIn": "//www.linkedin.com/in/john-walshe86",
    "GitHub": "https://github.com/JWalshe86/",
    "Medium": "https://medium.com/@walshejohnnyw7",
}
CONTACT = {
    "☎️  087 6470692": "+353876470692",
    "📫 jwalshedev@gmail.com": "jwalshedev@gmail.com",
}
PROJECTS = {
    "🏆 Sales Dashboard - Comparing sales across three stores": "https://youtu.be/Sb0A9i6d320",
    "🏆 Income and Expense Tracker - Web app with NoSQL database": "https://youtu.be/3egaMfE9388",
    "🏆 Desktop Application - Excel2CSV converter with user settings & menubar": "https://youtu.be/LzCfNanQ_9c",
    "🏆 MyToolBelt - Custom MS Excel add-in to combine Python & Excel": "https://pythonandvba.com/mytoolbelt/",
}


st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)


# --- LOAD CSS, PDF & PROFIL PIC ---
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
with open(resume_file, "rb") as pdf_file:
    PDFbyte = pdf_file.read()


# --- HERO SECTION ---

st.title(NAME)
st.write(DESCRIPTION)



# --- EXPERIENCE & QUALIFICATIONS ---
st.write('\n')
st.subheader("Experience & Qulifications")
st.write(
    """
- ✔️  Worked in an Agile Software development process using JIRA to manage customer driven tasks, which
spanned the entire tech stack, including: Backend Framework coupled with Frontend Framework most of
our CSS was done with CSSFrameWork
- ✔️  Maintained project infrastructure by boosting docker integration on our projects which helped
cross-team and cross-project tasks
- ✔️  Built automated test suites to reduce time spent on manual QA of customer projects
- ✔️  Gathered requirements by directly interfacing with clients regularly, integrating new requests into our agile
workflow
- ✔️  Participated in the PR review process to bolster code quality
- ✔️  Played a key role in enhancing the performance of third party software (https://plane.so) through effective
- ✔️  While working on one of the UK's largest motorcycle clubs site (nortonownersclub.org) I ensured continuous
updates to documents based on resolved issues and shared new knowledge with team members,
enhancing their software proficiency. 
- ✔️  Gathered requirements by directly interfacing with clients regularly, integrating new requests into our agile
"""
)


# --- Projects ---
st.write('\n')
st.subheader("Portfolios")
st.write(
    """
- 👩‍💻 * To see as live sites visit https://github.com/JWalshe86
- 👩‍💻 McPlantsNavan - Online Plant store. Use of stripe so customers could purchase plants safely. Designated
users could update/delete and add plants. Site linked to gmail, so customers could subscribe to newsletter.
- 📊 Nags-with-notions2.0. - Website whereby clients can order the services of a mobile pizzeria. Use of php to
access stored data.
- 📚 Pizza Ordering System - Python-based system for ordering pizza. Use of pytest to validate code.
Continuous feedback integrated to improve user experience. 
- 🗄️ DCareer - Website displaying my portfolio and career journey. Use of django framework.
- Mickey Mouse Memory Game - Themed card matching game. Built using javascript, html and css.
"""
)


# --- Education ---
st.write('\n')
st.subheader("Education")
st.write("---")

# --- Education 1
st.write("🚧", "**Diploma in Full Stack Software Development | Code Institute**")
st.write("06/2023 - 06/24")

# --- Education 2
st.write('\n')
st.write("🚧", "**MSc Applied Psychology | Trinity College Dublin**")
st.write("01/2011 - 02/2012")

# --- Education 3
st.write('\n')
st.write("🚧", "**Bsc Psychology | NUI Maynooth**")
st.write("09/2005 - 05/2009")


# --- Contact ---
st.write('\n')
st.subheader("Contact")
# --- SOCIAL LINKS ---
st.write('\n')
cols = st.columns(len(CONTACT))
for index, (platform, link) in enumerate(CONTACT.items()):
    cols[index].write(f"[{platform}]({link})")
cols = st.columns(len(SOCIAL_MEDIA))
for index, (platform, link) in enumerate(SOCIAL_MEDIA.items()):
    cols[index].write(f"[{platform}]({link})")
