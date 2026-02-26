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
# CSS FIX (Hero Not Cut + Proper Width)
# ------------------------------------------------
st.markdown("""
<style>

/* App Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}

/* Keep proper top spacing */
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    margin: auto;
}

/* Blue Hero */
.hero {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 40px;
    border-radius: 20px;
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

.chat-box {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
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
# INPUT SECTION
# ------------------------------------------------
st.subheader("🧩 Application Context (Optional)")
application_context = st.text_area("", height=100)

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
        height=220
    )

# ------------------------------------------------
# AI FUNCTIONS
# ------------------------------------------------
def generate_story(requirement, context):
    context_block = f"Application Context:\n{context}\n\n" if context.strip() else ""

    prompt = f"""
You are a Senior Agile Business Analyst.

{context_block}

Convert the requirement into structured user stories
with acceptance criteria, edge cases and assumptions.

Requirement:
{requirement}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content


def followup_response(question):
    prompt = f"""
You previously generated the following user story:

{st.session_state.generated_story}

User follow-up question:
{question}

Respond clearly and structured.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
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
            st.session_state.chat_history = []

# ------------------------------------------------
# OUTPUT
# ------------------------------------------------
if st.session_state.generated_story:

    st.success("🎉 User Story Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    st.markdown("---")
    st.subheader("💬 Ask Follow-up Questions")

    user_question = st.text_input(
        "Type your question (e.g., Explain assumptions one by one)"
    )

    if st.button("Ask"):
        if user_question.strip() != "":
            answer = followup_response(user_question)
            st.session_state.chat_history.append(("You", user_question))
            st.session_state.chat_history.append(("AI", answer))

    # Display chat
    for role, message in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"**🧑 You:** {message}")
        else:
            st.markdown(f"**🤖 AI:** {message}")

    # Download
    if st.button("⬇ Download as Word"):
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
