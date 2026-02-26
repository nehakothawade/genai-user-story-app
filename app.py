import streamlit as st
from groq import Groq
from docx import Document
from PyPDF2 import PdfReader

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="TechVortex | AI-Powered User Story Generator",
    page_icon="🚀",
    layout="wide"
)

# ------------------------------------------------
# CLEAN CSS
# ------------------------------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #eef2f3, #dfe9f3); }
.block-container { max-width: 900px; padding: 0 1rem; margin: auto; }
.hero { background: linear-gradient(90deg,#1e3c72,#2a5298); padding:35px; border-radius:0 0 20px 20px; color:white; text-align:center; margin-bottom:40px; }
.stButton>button { border-radius:8px; height:3em; font-weight:600; }
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
if "initial_story" not in st.session_state:
    st.session_state.initial_story = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "followup_input" not in st.session_state:
    st.session_state.followup_input = ""

# ------------------------------------------------
# HERO
# ------------------------------------------------
st.markdown("""
<div class="hero">
<h1>🚀 TechVortex</h1>
<p>Continuous AI User Story Generator with Infinite Follow-ups</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# APPLICATION CONTEXT
# ------------------------------------------------
st.subheader("🧩 Application Context (Optional)")
app_context = st.text_area("", height=100, placeholder="Optional context to guide AI...")

# ------------------------------------------------
# FILE UPLOAD
# ------------------------------------------------
st.subheader("📂 Upload Requirement File (Optional)")
uploaded_file = st.file_uploader("Upload .docx or .pdf file", type=["docx","pdf"])

def extract_text(file):
    text=""
    if file.type=="application/pdf":
        reader=PdfReader(file)
        for page in reader.pages:
            t=page.extract_text()
            if t: text+=t+"\n"
    elif file.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc=Document(file)
        for para in doc.paragraphs:
            text+=para.text+"\n"
    return text

if uploaded_file:
    extracted_text = extract_text(uploaded_file)
    st.success("✅ File uploaded successfully!")
    requirement_text = st.text_area("📌 Requirement (Editable)", value=extracted_text, height=220)
else:
    requirement_text = st.text_area("📌 Enter Requirement", height=220, placeholder="Example: Users should login using OTP verification...")

# ------------------------------------------------
# AI FUNCTIONS
# ------------------------------------------------
def generate_initial_story(requirement, context):
    ctx_block = f"Application Context:\n{context}\n\n" if context.strip() else ""
    prompt = f"""
You are a Senior Agile Business Analyst.

{ctx_block}

Convert this requirement into:
- Atomic user stories
- Acceptance Criteria
- Edge Cases
- Assumptions

STRICT FORMAT:

Requirement:
{requirement}
"""
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0.5
    )
    return resp.choices[0].message.content

def generate_followup(question):
    messages = [{"role":"system","content":"You are a helpful AI Business Analyst."}]
    if st.session_state.initial_story:
        messages.append({"role":"assistant","content":st.session_state.initial_story})
    for f in st.session_state.chat_history:
        messages.append({"role":"assistant","content":f})
    messages.append({"role":"user","content":question})
    
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.5
    )
    ans = resp.choices[0].message.content
    st.session_state.chat_history.append(ans)
    return ans

# ------------------------------------------------
# INITIAL GENERATION
# ------------------------------------------------
st.subheader("✨ Generate Initial User Story")
if st.button("Generate User Story"):
    if requirement_text.strip() == "":
        st.warning("Please enter a requirement.")
    else:
        with st.spinner("Generating initial story..."):
            st.session_state.initial_story = generate_initial_story(requirement_text, app_context)
        st.success("🎉 Initial User Story Generated!")
        st.markdown(st.session_state.initial_story)

# ------------------------------------------------
# FOLLOW-UP LOOP
# ------------------------------------------------
if st.session_state.initial_story:
    st.subheader("💬 Follow-up Questions (Continuous)")

    st.session_state.followup_input = st.text_area(
        "Enter your follow-up question or clarification:",
        value=st.session_state.followup_input,
        height=100
    )

    if st.button("Ask AI"):
        if st.session_state.followup_input.strip() != "":
            with st.spinner("AI is responding..."):
                answer = generate_followup(st.session_state.followup_input)
            st.success("✅ AI Response:")
            st.markdown(answer)
            st.session_state.followup_input = ""  # clear input after sending

# ------------------------------------------------
# DISPLAY CHAT HISTORY
# ------------------------------------------------
if st.session_state.chat_history:
    st.subheader("📝 Follow-up History")
    for idx, f in enumerate(st.session_state.chat_history,1):
        st.markdown(f"**Follow-up {idx}:** {f}")
