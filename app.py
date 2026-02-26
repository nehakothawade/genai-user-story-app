import streamlit as st
from groq import Groq
from docx import Document
from datetime import datetime
from io import BytesIO

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="TechVortex | GenAI User Story Generator",
    page_icon="🚀",
    layout="wide"
)

# ------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #eef2f3, #dfe9f3);
}

/* Hero */
.hero {
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 30px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
}

/* Glass Card */
.card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    max-width: 1000px;
    margin: auto;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    height: 3em;
    font-weight: 600;
    font-size: 15px;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# SIDEBAR SETTINGS
# ------------------------------------------------
with st.sidebar:
    st.title("⚙ AI Settings")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.3)
    model_choice = st.selectbox(
        "Model",
        ["llama3-8b-8192", "llama3-70b-8192"]
    )
    st.markdown("---")
    st.caption("GenAI Agile Backlog Builder")

# ------------------------------------------------
# HERO HEADER
# ------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 TechVortex</h1>
    <p>AI-Powered User Story Generator</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# MAIN CARD
# ------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("Enter Raw Requirement or Upload File")

# Text Input
requirement_text = st.text_area(
    "Requirement Input",
    height=180,
    placeholder="Example: Users should be able to reset password via OTP..."
)

# File Upload
uploaded_file = st.file_uploader(
    "Or Upload Requirement File (.txt or .docx)",
    type=["txt", "docx"]
)

file_text = ""

# Read file content
if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        file_text = "\n".join([para.text for para in doc.paragraphs])

# Final input selection priority
final_input = requirement_text.strip() if requirement_text.strip() else file_text.strip()

# Word Counter
word_count = len(final_input.split()) if final_input else 0
char_count = len(final_input) if final_input else 0
st.caption(f"Words: {word_count} | Characters: {char_count}")

# ------------------------------------------------
# GROQ CLIENT
# ------------------------------------------------
client = Groq(api_key="YOUR_GROQ_API_KEY")

def generate_user_story(requirement):
    prompt = f"""
Convert the raw requirement into:

1. Structured User Story (As a..., I want..., So that...)
2. Acceptance Criteria (bullet points)
3. Edge Cases
4. Business Rules

Requirement:
{requirement}
"""
    response = client.chat.completions.create(
        model=model_choice,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )

    return response.choices[0].message.content

# ------------------------------------------------
# GENERATE BUTTON
# ------------------------------------------------
generate_clicked = st.button("✨ Generate User Story")

if generate_clicked:
    if final_input == "":
        st.warning("Please enter or upload a requirement.")
    else:
        with st.spinner("Generating high-quality user story..."):
            output = generate_user_story(final_input)
            st.session_state.generated_story = output

# ------------------------------------------------
# OUTPUT SECTION
# ------------------------------------------------
if "generated_story" in st.session_state:

    st.markdown("---")
    st.markdown("### 📄 Generated User Story")
    st.markdown(st.session_state.generated_story)

    col1, col2 = st.columns(2)

    # Regenerate
    with col1:
        if st.button("🔄 Regenerate"):
            with st.spinner("Regenerating..."):
                output = generate_user_story(final_input)
                st.session_state.generated_story = output

    # Download
    with col2:
        doc = Document()
        doc.add_heading("Generated User Story", level=1)
        doc.add_paragraph(st.session_state.generated_story)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇ Download as DOCX",
            data=buffer,
            file_name=f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.markdown('</div>', unsafe_allow_html=True)
