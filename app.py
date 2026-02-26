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
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

if "current_question" not in st.session_state:
    st.session_state.current_question = None

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
# APPLICATION CONTEXT
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

    prompt = f"""
You are a Senior Agile Business Analyst.

Application Context:
{context}

Convert the requirement into:
- Atomic user stories
- Acceptance Criteria
- Edge Cases
- Assumptions

After generating the story,
ask ONE intelligent clarification question at the end.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": requirement + "\n\n" + prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content

if st.button("✨ Generate User Story"):
    if requirement_text.strip() == "":
        st.warning("Please enter or upload requirement.")
    else:
        with st.spinner("Generating..."):
            full_output = generate_story(requirement_text, application_context)

            parts = full_output.strip().split("?")
            story = "?".join(parts[:-1])
            question = parts[-1] + "?"

            st.session_state.generated_story = story
            st.session_state.current_question = question
            st.session_state.chat_history = []
            st.rerun()

# ------------------------------------------------
# DISPLAY STORY + FOLLOW-UP LOOP
# ------------------------------------------------
if st.session_state.generated_story:

    st.success("🎉 User Story Generated")
    st.markdown(st.session_state.generated_story)
    st.divider()

    if st.session_state.current_question:

        st.info(f"🤖 Follow-up Question:\n\n{st.session_state.current_question}")

        user_answer = st.text_area("Your Answer:", height=20)

        col1, col2 = st.columns(2)

     
        if col1.button("➤ Submit Query"):

            if user_answer.strip() != "":

                with st.spinner("Thinking..."):

                    follow_prompt = f"""
User Story:
{st.session_state.generated_story}

Previous Question:
{st.session_state.current_question}

Answer:
{user_answer}

1. Acknowledge briefly.
2. Ask ONE new intelligent clarification question.
Do NOT rewrite the story.
"""

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": follow_prompt}],
                        temperature=0.4,
                    )

                    output = response.choices[0].message.content

                    parts = output.strip().split("?")
                    acknowledgement = "?".join(parts[:-1])
                    next_question = parts[-1] + "?"

                    st.session_state.chat_history.append({
                        "question": st.session_state.current_question,
                        "answer": user_answer,
                        "ai_ack": acknowledgement
                    })

                    st.session_state.current_question = next_question
                    st.rerun()

        # Download & Finish
        if col2.button("✅ Download & Finish"):

            doc = Document()
            doc.add_heading("AI Generated User Story", level=1)
            doc.add_paragraph(st.session_state.generated_story)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="⬇ Download File",
                data=buffer,
                file_name=f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # ------------------------------------------------
    # DISCUSSION HISTORY
    # ------------------------------------------------
    if st.session_state.chat_history:

        st.divider()
        st.subheader("💬 Clarification Discussion")

        for chat in st.session_state.chat_history:
            st.markdown(f"**AI Asked:** {chat['question']}")
            st.markdown(f"**You Answered:** {chat['answer']}")
            st.markdown(f"**AI Response:** {chat['ai_ack']}")
            st.divider()


