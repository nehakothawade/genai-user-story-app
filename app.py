import streamlit as st
from groq import Groq
from docx import Document
from datetime import datetime
from io import BytesIO

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="TechVortex - User Story Generator",
    page_icon="🚀",
    layout="wide"
)

# -------------------------------
# CUSTOM CSS
# -------------------------------
st.markdown("""
<style>

/* Background */
body {
    background-color: #f4f6f9;
}

/* Top Header */
.top-bar {
    background-color: #3f51b5;
    padding: 15px 30px;
    color: white;
    font-size: 20px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Center Card */
.center-card {
    background: white;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.08);
    max-width: 900px;
    margin: 60px auto;
}

/* Gradient Title */
.gradient-title {
    background: linear-gradient(90deg, #2E86C1, #28B463);
    color: white;
    padding: 15px 25px;
    border-radius: 12px;
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 20px;
}

/* Counter */
.counter-box {
    text-align: right;
    font-size: 13px;
    color: gray;
    margin-bottom: 10px;
}

/* Buttons */
.stButton>button {
    border-radius: 8px;
    height: 3em;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER BAR
# -------------------------------
st.markdown("""
<div class="top-bar">
    <div>🚀 TechVortex</div>
    <div>Bosch Digital</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# MAIN CENTER CARD
# -------------------------------
st.markdown('<div class="center-card">', unsafe_allow_html=True)

st.markdown('<div class="gradient-title">User Story Generator</div>', unsafe_allow_html=True)

# -------------------------------
# INPUT AREA
# -------------------------------
requirement_text = st.text_area(
    "Provide your raw requirement:",
    height=200,
    placeholder="Enter raw requirement here..."
)

# Word & Character Counter
word_count = len(requirement_text.split()) if requirement_text else 0
char_count = len(requirement_text) if requirement_text else 0

st.markdown(f"""
<div class="counter-box">
Words: {word_count} | Characters: {char_count}
</div>
""", unsafe_allow_html=True)

# -------------------------------
# GROQ CLIENT
# -------------------------------
client = Groq(api_key="YOUR_GROQ_API_KEY")

def generate_user_story(requirement):
    prompt = f"""
Convert the following raw requirement into:
1. Structured User Story (As a..., I want..., So that...)
2. Acceptance Criteria (bullet points)
3. Edge Cases
4. Business Rules (if any)

Requirement:
{requirement}
"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content

# -------------------------------
# GENERATE BUTTON
# -------------------------------
if st.button("Generate User Story"):
    if requirement_text.strip() == "":
        st.warning("Please enter a requirement.")
    else:
        with st.spinner("Generating user story..."):
            output = generate_user_story(requirement_text)
            st.session_state.generated_story = output

# -------------------------------
# OUTPUT SECTION
# -------------------------------
if "generated_story" in st.session_state:

    st.markdown("### Generated Output")
    st.markdown(st.session_state.generated_story)

    col1, col2 = st.columns(2)

    # Regenerate Button
    with col1:
        if st.button("Regenerate"):
            with st.spinner("Regenerating..."):
                output = generate_user_story(requirement_text)
                st.session_state.generated_story = output

    # Download DOCX
    with col2:
        doc = Document()
        doc.add_heading("Generated User Story", level=1)
        doc.add_paragraph(st.session_state.generated_story)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="Download as DOCX",
            data=buffer,
            file_name=f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# Close Card Div
st.markdown('</div>', unsafe_allow_html=True)
