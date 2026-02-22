import streamlit as st
from groq import Groq
from docx import Document
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="AgileGenie - AI Backlog Builder",
    page_icon="🚀",
    layout="wide"
)

# ----------------------------------
# CUSTOM UI STYLING
# ----------------------------------
st.markdown("""
<style>
.big-title {
    font-size: 42px;
    font-weight: bold;
    color: #4B8BBE;
}
.subtitle {
    font-size: 20px;
    color: gray;
}
.stButton>button {
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🚀 AgileGenie</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Agile Backlog Builder</div>', unsafe_allow_html=True)
st.write("---")

# ----------------------------------
# GROQ API SETUP
# ----------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("⚠ GROQ_API_KEY not found. Please configure it in Streamlit Secrets.")
    st.stop()

# ----------------------------------
# SESSION STATE
# ----------------------------------
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

# ----------------------------------
# FILE UPLOAD SECTION
# ----------------------------------
st.subheader("📂 Upload Requirement File (Optional)")

uploaded_file = st.file_uploader(
    "Upload a Word (.docx) or PDF (.pdf) file",
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

# ----------------------------------
# REQUIREMENT INPUT
# ----------------------------------
if uploaded_file:
    extracted_text = extract_text_from_file(uploaded_file)
    st.success("✅ File uploaded and text extracted successfully!")
    requirement_text = st.text_area(
        "📌 Extracted Requirement (Editable)",
        value=extracted_text,
        height=250
    )
else:
    requirement_text = st.text_area(
        "📌 Enter Raw Requirement",
        height=250,
        placeholder="Example: The system should allow users to login using OTP..."
    )

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
def generate_story(requirement):
    prompt = f"""
You are a Senior Agile Business Analyst.

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
# WORD EXPORT FUNCTION
# ----------------------------------
def export_to_word(content):
    doc = Document()
    doc.add_heading("AI Generated User Stories", level=1)
    doc.add_paragraph(content)

    file_name = f"user_stories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.save(file_name)
    return file_name

# ----------------------------------
# BUTTONS
# ----------------------------------
col1, col2 = st.columns(2)

if col1.button("✨ Generate User Stories"):
    if requirement_text.strip() == "":
        st.warning("Please enter or upload a requirement.")
    else:
        with st.spinner("Generating AI Backlog..."):
            st.session_state.generated_story = generate_story(requirement_text)

# ----------------------------------
# DISPLAY OUTPUT
# ----------------------------------
if st.session_state.generated_story:

    st.success("🎉 User Stories Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    # --------------------------
    # QUALITY SCORE
    # --------------------------
    score, checks = validate_story(st.session_state.generated_story)

    st.write("---")
    st.subheader("📊 Quality Score")
    st.progress(score / 100)
    st.write(f"Score: {score}/100")

    for key, value in checks.items():
        st.write(f"{'✅' if value else '❌'} {key}")

    st.write("---")

    col3, col4 = st.columns(2)

    # --------------------------
    # REGENERATE BUTTON
    # --------------------------
    if col3.button("🔄 Regenerate (Improve Quality)"):
        with st.spinner("Improving user stories..."):
            improved_prompt = f"""
Improve the following user stories to make them:
- More clear
- More detailed
- More testable
- Better structured

{st.session_state.generated_story}
"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": improved_prompt}],
                temperature=0.3,
            )
            st.session_state.generated_story = response.choices[0].message.content
            st.rerun()

    # --------------------------
    # APPROVE BUTTON
    # --------------------------
    if col4.button("✅ Approve & Generate Word File"):
        file_path = export_to_word(st.session_state.generated_story)

        with open(file_path, "rb") as file:
            st.download_button(
                label="📄 Download Word File",
                data=file,
                file_name=file_path,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
