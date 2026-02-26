import streamlit as st
from groq import Groq
from docx import Document
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="TechVortex | AI User Story Generator",
    page_icon="🚀",
    layout="wide"
)

# ---------------------------
# CLEAN CSS
# ---------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}
.block-container {
    max-width: 900px;
    padding: 0 1rem;
    margin: auto;
}
.hero {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 35px;
    border-radius: 0 0 20px 20px;
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

# ---------------------------
# GROQ SETUP
# ---------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("⚠ GROQ_API_KEY not configured.")
    st.stop()

# ---------------------------
# SESSION STATE
# ---------------------------
if "initial_story" not in st.session_state:
    st.session_state.initial_story = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------
# HERO
# ---------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 TechVortex</h1>
    <p>AI-Powered Agile User Story Generator with Follow-ups</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# APPLICATION CONTEXT
# ---------------------------
st.subheader("🧩 Application Context (Optional)")
application_context = st.text_area("", height=100, placeholder="Optional context to guide AI...")

# ---------------------------
# FILE UPLOAD
# ---------------------------
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
    requirement_text = st.text_area("📌 Extracted Requirement (Editable)", value=extracted_text, height=220)
else:
    requirement_text = st.text_area("📌 Enter Requirement", height=220, placeholder="Example: Users should login using OTP verification...")

# ---------------------------
# AI FUNCTIONS
# ---------------------------
def generate_user_story(requirement, context):
    context_block = f"Application Context:\n{context}\n\n" if context.strip() else ""
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

def follow_up_response(user_question):
    # Include initial story + previous chat history for context
    messages = [{"role": "system", "content": "You are a helpful AI Business Analyst."}]
    if st.session_state.initial_story:
        messages.append({"role": "assistant", "content": st.session_state.initial_story})
    messages += st.session_state.chat_history
    messages.append({"role": "user", "content": user_question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.5,
    )
    answer = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    return answer

# ---------------------------
# PHASE 1: INITIAL GENERATION
# ---------------------------
st.subheader("✨ Generate Initial User Story")
if st.button("Generate User Story"):
    if requirement_text.strip() == "":
        st.warning("Please enter or upload a requirement.")
    else:
        with st.spinner("Generating initial user story..."):
            st.session_state.initial_story = generate_user_story(requirement_text, application_context)
            st.success("🎉 User Story Generated!")
            st.markdown(st.session_state.initial_story)

# ---------------------------
# PHASE 2: FOLLOW-UP QUESTIONS
# ---------------------------
if st.session_state.initial_story:
    st.subheader("💬 Ask Follow-up Questions")
    follow_up_input = st.text_area("Enter your question or clarification about the user story:")

    if st.button("Ask AI"):
        if follow_up_input.strip() == "":
            st.warning("Please enter your follow-up question.")
        else:
            with st.spinner("AI is responding..."):
                answer = follow_up_response(follow_up_input)
            st.success("✅ AI Response:")
            st.markdown(answer)

# ---------------------------
# DISPLAY FOLLOW-UP CHAT
# ---------------------------
if st.session_state.chat_history:
    st.subheader("📝 Follow-up Chat History")
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.markdown(f"**AI:** {msg['content']}")

# ---------------------------
# DOWNLOAD FINAL DOCUMENT
# ---------------------------
if st.session_state.initial_story:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬇ Download User Story as Word"):
            doc = Document()
            doc.add_heading("AI Generated User Story", level=1)
            doc.add_paragraph(st.session_state.initial_story)
            for msg in st.session_state.chat_history:
                doc.add_paragraph(f"Follow-up AI Response:\n{msg['content']}")

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                label="Download File",
                data=buffer,
                file_name=f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    with col2:
        if st.button("🔄 Clear All"):
            st.session_state.initial_story = None
            st.session_state.chat_history = []
            st.experimental_rerun()
