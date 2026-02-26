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
# CLEAN UI CSS
# ------------------------------------------------
st.markdown("""
<style>

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}

/* Fix content width */
.block-container {
    max-width: 900px;
    margin: auto;
    padding-top: 2rem;
}

/* Blue Hero - FIXED (no top cut) */
.hero {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 40px 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 40px;
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

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# ------------------------------------------------
# HERO SECTION
# ------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 TechVortex</h1>
    <p>AI-Powered Agile User Story Generator</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# APPLICATION CONTEXT
# ------------------------------------------------
st.subheader("🧩 Application Context (Optional)")
application_context = st.text_area("", height=100)

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
        height=220
    )
else:
    requirement_text = st.text_area(
        "📌 Enter Raw Requirement",
        height=220,
        placeholder="Example: Users should login using OTP verification..."
    )

# ------------------------------------------------
# AI GENERATION FUNCTION
# ------------------------------------------------
def generate_story(requirement, context):

    context_block = ""
    if context.strip():
        context_block = f"Application Context:\n{context}\n\n"

    prompt = f"""
You are a Senior Agile Business Analyst.

{context_block}

Convert the requirement into:
- Atomic user stories
- Acceptance Criteria
- Edge Cases
- Assumptions

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

# ------------------------------------------------
# GENERATE BUTTON
# ------------------------------------------------
if st.button("✨ Generate User Story"):
    if requirement_text.strip() == "":
        st.warning("Please enter or upload a requirement.")
    else:
        with st.spinner("Generating AI User Story..."):
            st.session_state.generated_story = generate_story(
                requirement_text,
                application_context
            )
            st.session_state.conversation_history = []
            st.rerun()

# ------------------------------------------------
# CONVERSATIONAL REFINEMENT MODE
# ------------------------------------------------
if st.session_state.generated_story is not None:

    st.success("🎉 User Story Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    st.divider()
    st.subheader("🧠 Let's Refine Further")

    clarification_input = st.text_area(
        "Add clarification (Assumption, Edge Case, Workflow detail, Business rule, etc.)",
        height=120,
        placeholder="Example: Explain OTP expiry behavior..."
    )

    col1, col2 = st.columns(2)

    # Submit clarification
    if col1.button("➤ Submit Clarification"):

        if clarification_input.strip() != "":

            with st.spinner("Refining user story..."):

                refinement_prompt = f"""
You are a Senior Agile Business Analyst.

Current User Story:
{st.session_state.generated_story}

User Clarification:
{clarification_input}

1. Update the user story accordingly.
2. Improve assumptions and edge cases.
3. Ask ONE intelligent follow-up clarification question at the end.

Return updated story + follow-up question.
"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": refinement_prompt}],
                    temperature=0.4,
                )

                updated_story = response.choices[0].message.content
                st.session_state.generated_story = updated_story

                st.session_state.conversation_history.append({
                    "user": clarification_input,
                    "ai": updated_story
                })

                st.rerun()

    # Finalize
    if col2.button("✅ Finalize Story"):
        st.success("✔ Story Finalized Successfully!")

        doc = Document()
        doc.add_heading("AI Generated User Story", level=1)
        doc.add_paragraph(st.session_state.generated_story)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇ Download Final Story",
            data=buffer,
            file_name=f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # Show refinement conversation
    if st.session_state.conversation_history:

        st.divider()
        st.subheader("💬 Refinement Conversation")

        for chat in st.session_state.conversation_history:
            st.markdown(f"**You:** {chat['user']}")
            st.markdown(f"**AI Response:**")
            st.markdown(chat['ai'])
            st.divider()
