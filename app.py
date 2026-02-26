import streamlit as st
from groq import Groq
from docx import Document
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO
import base64
import os

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="AgileGenie - AI Backlog Builder",
    page_icon="🚀",
    layout="wide"
)

# ----------------------------------
# MODERN UI STYLING
# ----------------------------------
st.markdown("""
<style>

body {
    background-color: #f4f6f9;
}

.main-card {
    background-color: #ffffff;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    max-width: 900px;
    margin: auto;
}

.gradient-header {
    background: linear-gradient(90deg, #2E86C1, #28B463);
    color: white;
    padding: 15px 20px;
    border-radius: 12px;
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.counter-box {
    background: rgba(255,255,255,0.25);
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
}

textarea {
    border-radius: 10px !important;
}

.stButton>button {
    border-radius: 8px;
    height: 3em;
    font-weight: 600;
}

.section-divider {
    margin-top: 25px;
    margin-bottom: 25px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------
# GROQ API SETUP
# ----------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("⚠ GROQ_API_KEY not found. Configure in Streamlit secrets.")
    st.stop()

# ----------------------------------
# SESSION STATE
# ----------------------------------
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

# ----------------------------------
# MAIN CARD START
# ----------------------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# Requirement Input Placeholder
requirement_text = st.text_area(
    "Enter Requirement",
    height=200,
    placeholder="Example: System must support biometric login for mobile app..."
)

# Word Counter
word_count = len(requirement_text.split()) if requirement_text else 0
char_count = len(requirement_text) if requirement_text else 0

st.markdown(f"""
<div class="gradient-header">
    Provide Requirements
    <div class="counter-box">
        Words: {word_count} | Characters: {char_count}
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------
# APPLICATION CONTEXT
# ----------------------------------
application_context = st.text_area(
    "Application Context (Optional)",
    height=100,
    placeholder="Example: Banking mobile app integrated with SAP backend..."
)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ----------------------------------
# FILE UPLOAD
# ----------------------------------
uploaded_file = st.file_uploader(
    "Upload Requirement File (.docx or .pdf)",
    type=["docx", "pdf"]
)

def extract_text_from_file(uploaded_file):
    text = ""

    if uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text

if uploaded_file:
    extracted_text = extract_text_from_file(uploaded_file)
    st.success("✅ File uploaded and text extracted!")
    requirement_text = extracted_text

# ----------------------------------
# VALIDATION FUNCTION
# ----------------------------------
def validate_story(output):
    score = 0
    checks = {
        "Role Defined": "As a" in output,
        "Functionality Defined": "I want" in output,
        "Business Value Defined": "So that" in output,
        "Acceptance Criteria Present": "Acceptance Criteria" in output,
    }

    for value in checks.values():
        if value:
            score += 25

    return score, checks

# ----------------------------------
# AI GENERATION FUNCTION
# ----------------------------------
def generate_story(requirement, app_context=None):

    context_section = ""
    if app_context and app_context.strip():
        context_section = f"Application Context:\n{app_context}\n\n"

    prompt = f"""
You are a Senior Agile Business Analyst.

{context_section}

Convert the requirement into:
- Atomic user stories
- Follow INVEST principles
- Add clear acceptance criteria
- Include edge cases
- Mention assumptions
- Ask clarifications if needed

STRICT FORMAT:

---
### User Story
As a <role>
I want <functionality>
So that <business value>

Acceptance Criteria:
1.
2.

Edge Cases:
-

Assumptions:
-

Clarifications Needed:
-
---

Requirement:
{requirement}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content

# ----------------------------------
# BUTTONS
# ----------------------------------
col1, col2 = st.columns(2)

if col1.button("✨ Generate"):
    if requirement_text.strip() == "":
        st.warning("Please enter a requirement.")
    else:
        with st.spinner("Generating structured user stories..."):
            st.session_state.generated_story = generate_story(
                requirement_text,
                application_context
            )

if col2.button("🔄 Clear"):
    st.session_state.generated_story = None
    st.rerun()

# ----------------------------------
# OUTPUT SECTION
# ----------------------------------
if st.session_state.generated_story:

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.success("🎉 User Stories Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    # Quality Score
    score, checks = validate_story(st.session_state.generated_story)

    st.subheader("📊 Quality Score")
    st.progress(score / 100)
    st.write(f"Score: {score}/100")

    for key, value in checks.items():
        st.write(f"{'✅' if value else '❌'} {key}")

    # Export
    if st.button("✅ Approve & Download Word File"):
        doc = Document()
        doc.add_heading("AI Generated User Stories", level=1)
        doc.add_paragraph(st.session_state.generated_story)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        b64 = base64.b64encode(buffer.read()).decode()
        file_name = f"user_stories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

        download_html = f"""
        <html>
        <body>
        <a id="download_link"
           href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}"
           download="{file_name}">
        </a>
        <script>
            document.getElementById('download_link').click();
        </script>
        </body>
        </html>
        """

        st.success("Download starting...")
        st.components.v1.html(download_html, height=0)

# Close main card
st.markdown('</div>', unsafe_allow_html=True)
