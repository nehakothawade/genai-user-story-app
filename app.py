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
# CUSTOM UI (UNCHANGED PREMIUM STYLE)
# ------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}

.hero {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 30px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
}

.card {
    background: rgba(255,255,255,0.9);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    max-width: 1000px;
    margin: auto;
}

.stButton>button {
    border-radius: 10px;
    height: 3em;
    font-weight: 600;
    font-size: 15px;
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
    st.error("⚠ GROQ_API_KEY not found in Streamlit secrets.")
    st.stop()

# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

# ------------------------------------------------
# HERO SECTION
# ------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 TechVortex</h1>
    <p>AI-Powered Agile User Story Generator</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

# ------------------------------------------------
# APPLICATION CONTEXT
# ------------------------------------------------
st.subheader("🧩 Application Context (Optional)")
application_context = st.text_area(
    "Describe the application/domain context",
    height=120
)

st.write("---")

# ------------------------------------------------
# FILE UPLOAD
# ------------------------------------------------
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
        height=250
    )
else:
    requirement_text = st.text_area(
        "📌 Enter Raw Requirement",
        height=250,
        placeholder="Example: Users should login using OTP verification..."
    )

# ------------------------------------------------
# AI FUNCTION
# ------------------------------------------------
def generate_story(requirement, context):

    context_block = ""
    if context and context.strip() != "":
        context_block = f"Application Context:\n{context}\n\n"

    prompt = f"""
You are a Senior Agile Business Analyst.

{context_block}

Convert the requirement into:
- Atomic user stories
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

# ------------------------------------------------
# GENERATE BUTTON (STRICT LOGIC)
# ------------------------------------------------
generate_clicked = st.button("✨ Generate User Story")

if generate_clicked:
    if requirement_text.strip() == "":
        st.warning("Please enter or upload a requirement.")
    else:
        with st.spinner("Generating AI User Story..."):
            st.session_state.generated_story = generate_story(
                requirement_text,
                application_context
            )

# ------------------------------------------------
# OUTPUT (ONLY IF GENERATED)
# ------------------------------------------------
if st.session_state.generated_story is not None:

    st.markdown("---")
    st.success("🎉 User Story Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    col1, col2 = st.columns(2)

    # 🔄 Regenerate
    if col1.button("🔄 Regenerate"):
        with st.spinner("Improving quality..."):
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

    # ⬇ Download
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
