import streamlit as st
from groq import Groq
from docx import Document
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO
import base64

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="TechVortex - AI User Story Generator",
    page_icon="🚀",
    layout="wide"
)

# ----------------------------------
# GROQ API SETUP
# ----------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("⚠ GROQ_API_KEY not found in Streamlit secrets.")
    st.stop()

# ----------------------------------
# SESSION STATE INIT
# ----------------------------------
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

# ----------------------------------
# TITLE
# ----------------------------------
st.title("🚀 TechVortex")
st.subheader("AI-Powered Agile User Story Generator")
st.write("---")

# ----------------------------------
# APPLICATION CONTEXT (OPTIONAL)
# ----------------------------------
st.subheader("🧩 Application Context (Optional)")
application_context = st.text_area(
    "Describe the application/domain",
    height=120,
    placeholder="Example: Retail banking mobile app integrated with SAP backend..."
)

st.write("---")

# ----------------------------------
# FILE UPLOAD (OPTIONAL)
# ----------------------------------
st.subheader("📂 Upload Requirement File (Optional)")

uploaded_file = st.file_uploader(
    "Upload .docx or .pdf file",
    type=["docx", "pdf"]
)

def extract_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
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
    extracted_text = extract_text(uploaded_file)
    st.success("✅ File uploaded successfully!")
    requirement_text = st.text_area(
        "📌 Extracted Requirement (Editable)",
        value=extracted_text,
        height=250
    )
else:
    requirement_text = st.text_area(
        "📌 Enter Raw Requirement",
        height=250,
        placeholder="Example: Users should be able to login using OTP..."
    )

# ----------------------------------
# AI GENERATION FUNCTION
# ----------------------------------
def generate_story(requirement, app_context=None):

    context_block = ""
    if app_context and app_context.strip() != "":
        context_block = f"Application Context:\n{app_context}\n\n"

    prompt = f"""
You are a Senior Agile Business Analyst.

{context_block}

Convert the requirement into:
- Atomic User Stories
- Follow INVEST principles
- Add Acceptance Criteria
- Include Edge Cases
- Mention Assumptions
- Ask Clarifications if needed

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
# GENERATE BUTTON (STRICT CONTROL)
# ----------------------------------
col1, col2 = st.columns(2)

if col1.button("✨ Generate User Story"):
    if requirement_text.strip() == "":
        st.warning("Please enter or upload a requirement.")
    else:
        with st.spinner("Generating AI User Story..."):
            st.session_state.generated_story = generate_story(
                requirement_text,
                application_context
            )

# ----------------------------------
# DISPLAY OUTPUT (ONLY IF EXISTS)
# ----------------------------------
if st.session_state.generated_story:

    st.success("🎉 User Story Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    st.write("---")

    col3, col4 = st.columns(2)

    # REGENERATE
    if col3.button("🔄 Regenerate"):
        with st.spinner("Improving story quality..."):
            improved_prompt = f"""
Improve the following user story to make it:
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

    # DOWNLOAD
    if col4.button("⬇ Download as Word"):
        doc = Document()
        doc.add_heading("AI Generated User Story", level=1)
        doc.add_paragraph(st.session_state.generated_story)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        b64 = base64.b64encode(buffer.read()).decode()
        file_name = f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

        href = f"""
        <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}"
        download="{file_name}">
        Click here if download does not start automatically
        </a>
        """

        st.success("Download starting...")
        st.markdown(href, unsafe_allow_html=True)
