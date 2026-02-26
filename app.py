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
    page_title="TechVortex | AI User Story Chat",
    page_icon="🚀",
    layout="wide"
)

# ------------------------------------------------
# CLEAN CSS FIX
# ------------------------------------------------
st.markdown("""
<style>
/* Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}

/* Container */
.block-container {
    max-width: 900px;
    padding-top: 0rem;
    padding-left: 1rem;
    padding-right: 1rem;
    margin: auto;
}

/* Hero Header */
.hero {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 35px;
    border-radius: 0 0 20px 20px;
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
# SESSION STATE FOR CHAT
# ------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------------------------------------
# HERO SECTION
# ------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 TechVortex</h1>
    <p>AI-Powered Agile User Story Chat Generator</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# APPLICATION CONTEXT
# ------------------------------------------------
st.subheader("🧩 Application Context (Optional)")
application_context = st.text_area("", height=100, placeholder="Optional context to guide AI...")

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
    user_input = st.text_area(
        "📌 Extracted Requirement (Editable)",
        value=extracted_text,
        height=220
    )
else:
    user_input = st.text_area(
        "📌 Enter Requirement",
        height=220,
        placeholder="Example: Users should login using OTP verification..."
    )

# ------------------------------------------------
# AI FUNCTION
# ------------------------------------------------
def ai_chat_response(user_message):
    context_block = ""
    if application_context.strip():
        context_block = f"Application Context:\n{application_context}\n\n"

    prompt = f"""
You are a Senior Agile Business Analyst AI Assistant.

{context_block}

User Input / Requirement:
{user_message}

Instructions:
- Reply in a friendly conversational style.
- Convert requirement into atomic user stories.
- Include acceptance criteria, edge cases, and assumptions.
- Allow follow-up questions and clarifications in a chat style.

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
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=st.session_state.chat_history + [{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    # Add AI response to chat history
    ai_msg = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": ai_msg})
    return ai_msg

# ------------------------------------------------
# SEND BUTTON
# ------------------------------------------------
if st.button("✨ Send Requirement / Question"):
    if user_input.strip() == "":
        st.warning("Please enter or upload a requirement.")
    else:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("AI is generating response..."):
            ai_response = ai_chat_response(user_input)
        st.success("🎉 AI Response Generated!")

# ------------------------------------------------
# DISPLAY CHAT HISTORY
# ------------------------------------------------
st.subheader("💬 Chat History")
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**AI:** {msg['content']}")

# ------------------------------------------------
# DOWNLOAD FINAL USER STORY
# ------------------------------------------------
if st.session_state.chat_history:
    all_stories = "\n\n".join([m["content"] for m in st.session_state.chat_history if m["role"] == "assistant"])
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬇ Download Chat as Word"):
            doc = Document()
            doc.add_heading("AI Generated User Stories (Chat)", level=1)
            doc.add_paragraph(all_stories)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="Download File",
                data=buffer,
                file_name=f"user_stories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    with col2:
        if st.button("🔄 Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()
