import streamlit as st
from groq import Groq
from docx import Document
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="TechVortex | AI User Story Generator",
    page_icon="🚀",
    layout="wide"
)

# ------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------
st.markdown("""
<style>

/* Remove default white space */
.block-container {
    padding-top: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}

/* Blue Hero */
.hero {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 35px;
    border-radius: 0px 0px 20px 20px;
    color: white;
    text-align: center;
}

/* Main Center Box */
.main-container {
    max-width: 900px;
    margin: 40px auto;
    background: rgba(255,255,255,0.95);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}

/* Buttons */
.stButton>button {
    border-radius: 8px;
    height: 3em;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# GROQ SETUP
# ------------------------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("⚠ GROQ_API_KEY not configured.")
    st.stop()

# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

# ------------------------------------------------
# BLUE HERO (KEPT AS IS)
# ------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 TechVortex</h1>
    <p>AI-Powered Agile User Story Generator</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# MAIN CENTERED BOX
# ------------------------------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Application Context
st.subheader("🧩 Application Context (Optional)")
application_context = st.text_area("", height=100)

# File Upload
st.subheader("📂 Upload Requirement File (Optional)")
uploaded_file = st.file_uploader(
    "Upload .docx or .pdf file",
    type=["docx", "pdf"]
)

def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

if uploaded_file:
    extracted_text = extract_text(uploaded_file)
    st.success("✅ File uploaded successfully!")
    requirement_text = st.text_area(
        "📌 Extracted Requirement (Editable)",
        value=extracted_text,
        height=220
    )
else:
    requirement_text = st.text_area(
        "📌 Enter Raw Requirement",
        height=220,
        placeholder="Example: Users should login using OTP verification..."
    )

# AI Function
def generate_story(requirement, context):

    context_block = ""
    if context.strip():
        context_block = f"Application Context:\n{context}\n\n"

    prompt = f"""
You are a Senior Agile Business Analyst.

{context_block}

Convert the requirement into:
- Atomic user stories
- Add Acceptance Criteria
- Include Edge Cases
- Mention Assumptions

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

# Generate Button
if st.button("✨ Generate User Story"):
    if requirement_text.strip() == "":
        st.warning("Please enter or upload a requirement.")
    else:
        with st.spinner("Generating AI User Story..."):
            st.session_state.generated_story = generate_story(
                requirement_text,
                application_context
            )

# Output
if st.session_state.generated_story is not None:

    st.success("🎉 User Story Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    col1, col2 = st.columns(2)

    if col1.button("🔄 Regenerate"):
        with st.spinner("Improving quality..."):
            improved_prompt = f"Improve this user story:\n{st.session_state.generated_story}"
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": improved_prompt}],
                temperature=0.3,
            )
            st.session_state.generated_story = response.choices[0].message.content
            st.rerun()

    if col2.button("⬇ Download as Word"):
        doc = Document()
        doc.add_heading("AI Generated User Story", level=1)
        doc.add_paragraph(st.session_state.generated_story)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="Click to Download",
            data=buffer,
            file_name=f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.markdown('</div>', unsafe_allow_html=True)
