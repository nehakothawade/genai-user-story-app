import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO
from datetime import datetime

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="TechVortex - AI User Story Generator",
    layout="centered"
)

# ------------------------------------------------
# SAFE SESSION STATE INIT (IMPORTANT)
# ------------------------------------------------
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

if "conversation" not in st.session_state:
    st.session_state.conversation = []

# ------------------------------------------------
# GROQ CLIENT (Use Secrets in Streamlit Cloud)
# ------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ------------------------------------------------
# BLUE CENTERED UI (UNCHANGED STYLE)
# ------------------------------------------------
st.markdown("""
<style>
.main-container {
    max-width: 900px;
    margin: auto;
    padding: 30px;
    background-color: #0E1A40;
    border-radius: 15px;
    box-shadow: 0px 0px 25px rgba(0,0,0,0.4);
    color: white;
}
h1 {
    text-align: center;
}
.stTextArea textarea {
    background-color: #1B2A60 !important;
    color: white !important;
}
.stTextInput input {
    background-color: #1B2A60 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.title("🚀 TechVortex - AI User Story Generator")

# ------------------------------------------------
# REQUIREMENT INPUT
# ------------------------------------------------
st.subheader("📌 Enter Requirement")

requirement_text = st.text_area("Describe your requirement")

uploaded_file = st.file_uploader("Or upload a .txt file", type=["txt"])

file_content = ""
if uploaded_file is not None:
    file_content = uploaded_file.read().decode("utf-8")

final_requirement = requirement_text if requirement_text else file_content

# ------------------------------------------------
# GENERATE USER STORY
# ------------------------------------------------
if st.button("✨ Generate User Story"):

    if not final_requirement.strip():
        st.warning("Please enter requirement or upload file.")
    else:
        with st.spinner("Generating..."):

            story_prompt = f"""
You are a Senior Agile Business Analyst.

Generate:
- Title
- User Story (As a... I want... So that...)
- Acceptance Criteria
- Assumptions
- Edge Cases

Requirement:
{final_requirement}
"""

            story_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": story_prompt}],
                temperature=0.4,
            )

            story = story_response.choices[0].message.content
            st.session_state.generated_story = story

            # First clarification question
            followup_prompt = f"""
User Story:
{story}

Ask ONE clarification question only.
Do NOT rewrite the story.
"""

            followup_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": followup_prompt}],
                temperature=0.4,
            )

            first_question = followup_response.choices[0].message.content

            st.session_state.conversation = [
                {"role": "assistant", "content": first_question}
            ]

# ------------------------------------------------
# DISPLAY STORY + CHAT
# ------------------------------------------------
if st.session_state.generated_story is not None:

    st.success("✅ User Story Generated")
    st.markdown(st.session_state.generated_story)
    st.divider()

    st.subheader("💬 Clarification Discussion")

    # Show conversation
    for message in st.session_state.conversation:
        if message["role"] == "assistant":
            st.markdown(f"**🤖 AI:** {message['content']}")
        else:
            st.markdown(f"**🙋 You:** {message['content']}")

    st.divider()

    user_input = st.text_input("Type your response")

    col1, col2 = st.columns(2)

    # SEND MESSAGE
    if col1.button("➤ Send"):

        if user_input.strip():

            st.session_state.conversation.append(
                {"role": "user", "content": user_input}
            )

            with st.spinner("Thinking..."):

                messages = [
                    {
                        "role": "system",
                        "content": f"""
You are a Senior Agile Business Analyst.

User Story:
{st.session_state.generated_story}

Do NOT rewrite story.
Ask ONE clarification question at a time.
"""
                    }
                ]

                for msg in st.session_state.conversation:
                    messages.append(msg)

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.4,
                )

                ai_reply = response.choices[0].message.content

                st.session_state.conversation.append(
                    {"role": "assistant", "content": ai_reply}
                )

            st.rerun()

    # DOWNLOAD BUTTON
    if col2.button("⬇ Download & Finish"):

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

st.markdown("</div>", unsafe_allow_html=True)
