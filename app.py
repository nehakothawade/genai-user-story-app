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
# UI CSS
# ------------------------------------------------
st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}

.block-container {
    max-width: 900px;
    margin: auto;
    padding-top: 2rem;
}

.hero {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 40px 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 40px;
}

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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------------------------------------
# HERO
# ------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 TechVortex</h1>
    <p>AI-Powered Agile User Story Generator</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# CONTEXT
# ------------------------------------------------
st.subheader("🧩 Application Context (Optional)")
application_context = st.text_area("", height=100)

# ------------------------------------------------
# FILE UPLOAD
# ------------------------------------------------
st.subheader("📂 Upload Requirement File (Optional)")
uploaded_file = st.file_uploader("Upload .docx or .pdf file", type=["docx", "pdf"])

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
        height=220
    )

# ------------------------------------------------
# GENERATE STORY
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

Requirement:
{requirement}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content

if st.button("✨ Generate User Story"):
    if requirement_text.strip() == "":
        st.warning("Please enter or upload a requirement.")
    else:
        with st.spinner("Generating..."):
            st.session_state.generated_story = generate_story(
                requirement_text,
                application_context
            )
            st.session_state.chat_history = []
            st.rerun()

# ------------------------------------------------
# DISPLAY STORY (FIXED)
# ------------------------------------------------
if st.session_state.generated_story:

    st.success("🎉 User Story Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    st.divider()
    st.subheader("💬 Ask Clarification")

    user_question = st.text_area(
        "Ask about assumptions, edge cases, logic, workflow, etc.",
        height=120
    )

    if st.button("➤ Ask"):

        if user_question.strip() != "":

            with st.spinner("Thinking..."):

                clarification_prompt = f"""
You are a Senior Agile Business Analyst.

Here is the generated user story:

{st.session_state.generated_story}

User Question:
{user_question}

Answer ONLY the user question clearly.
Do NOT rewrite the full user story.
"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": clarification_prompt}],
                    temperature=0.4,
                )

                answer = response.choices[0].message.content

                st.session_state.chat_history.append({
                    "question": user_question,
                    "answer": answer
                })

                st.rerun()

    # ------------------------------------------------
    # SHOW CHAT HISTORY
    # ------------------------------------------------
    if st.session_state.chat_history:

        st.divider()
        st.subheader("🧠 Clarification Discussion")

        for chat in st.session_state.chat_history:
            st.markdown(f"**You:** {chat['question']}")
            st.markdown(f"**AI:** {chat['answer']}")
            st.divider()

    # ------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------
    if st.button("⬇ Download User Story"):
        doc = Document()
        doc.add_heading("AI Generated User Story", level=1)
        doc.add_paragraph(st.session_state.generated_story)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="Download File",
            data=buffer,
            file_name=f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
