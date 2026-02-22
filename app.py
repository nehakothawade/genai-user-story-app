import streamlit as st
from groq import Groq
from docx import Document
from datetime import datetime
import os

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="AgileGenie - AI Backlog Builder",
    page_icon="🚀",
    layout="wide"
)

# ----------------------------------
# HEADER UI
# ----------------------------------
st.markdown("""
<style>
.big-title {
    font-size: 40px;
    font-weight: bold;
    color: #4B8BBE;
}
.subtitle {
    font-size: 18px;
    color: gray;
}
.stButton>button {
    border-radius: 8px;
    height: 3em;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🚀 AgileGenie</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Agile Backlog Builder</div>', unsafe_allow_html=True)
st.write("---")

# ----------------------------------
# GROQ API SETUP
# ----------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("Groq API key not configured. Please set it in Streamlit secrets.")
    st.stop()

# ----------------------------------
# SESSION STATE
# ----------------------------------
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

# ----------------------------------
# VALIDATION FUNCTION
# ----------------------------------
def validate_story(output):
    score = 0
    checks = {
        "Role Defined": "As a" in output,
        "Functionality Defined": "I want" in output,
        "Business Value Defined": "So that" in output,
        "Acceptance Criteria Present": "Acceptance Criteria" in output,
    }

    for value in checks.values():
        if value:
            score += 25

    return score, checks

# ----------------------------------
# AI GENERATION FUNCTION
# ----------------------------------
def generate_story(requirement):
    prompt = f"""
You are a Senior Agile Business Analyst.

Convert the requirement into:
- Atomic user stories
- Follow INVEST principles
- Add acceptance criteria
- Include edge cases
- Mention assumptions
- Ask clarifications if needed

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

# ----------------------------------
# WORD EXPORT FUNCTION
# ----------------------------------
def export_to_word(content):
    doc = Document()
    doc.add_heading("AI Generated User Stories", level=1)
    doc.add_paragraph(content)

    file_name = f"user_stories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.save(file_name)
    return file_name

# ----------------------------------
# INPUT
# ----------------------------------
requirement_text = st.text_area(
    "📌 Enter Raw Requirement",
    height=200,
    placeholder="Example: The system should allow users to login using OTP..."
)

col1, col2 = st.columns(2)

# ----------------------------------
# GENERATE BUTTON
# ----------------------------------
if col1.button("✨ Generate User Stories"):
    if requirement_text.strip() == "":
        st.warning("Please enter a requirement.")
    else:
        with st.spinner("Generating User Stories..."):
            st.session_state.generated_story = generate_story(requirement_text)

# ----------------------------------
# DISPLAY OUTPUT
# ----------------------------------
if st.session_state.generated_story:

    st.success("User Stories Generated Successfully!")
    st.markdown(st.session_state.generated_story)

    # Quality Score
    score, checks = validate_story(st.session_state.generated_story)

    st.write("---")
    st.subheader("📊 Quality Score")
    st.progress(score / 100)
    st.write(f"Score: {score}/100")

    for key, value in checks.items():
        st.write(f"{'✅' if value else '❌'} {key}")

    col3, col4 = st.columns(2)

    # ----------------------------------
    # REGENERATE
    # ----------------------------------
    if col3.button("🔄 Regenerate (Improve)"):
        with st.spinner("Improving user stories..."):
            improved_prompt = f"""
Improve the following user stories to make them more clear,
detailed and testable:

{st.session_state.generated_story}
"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": improved_prompt}],
                temperature=0.3,
            )
            st.session_state.generated_story = response.choices[0].message.content
            st.rerun()

    # ----------------------------------
    # APPROVE
    # ----------------------------------
    if col4.button("✅ Approve & Generate Word File"):
        file_path = export_to_word(st.session_state.generated_story)
        with open(file_path, "rb") as file:
            st.download_button(
                label="📄 Download Word File",
                data=file,
                file_name=file_path,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
