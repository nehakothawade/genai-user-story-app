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
# CSS
# ---------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #eef2f3, #dfe9f3);}
.block-container {max-width: 900px; padding: 0 1rem; margin:auto;}
.hero {background: linear-gradient(90deg,#1e3c72,#2a5298); padding:35px; border-radius:0 0 20px 20px; color:white; text-align:center; margin-bottom:40px;}
.stButton>button {border-radius:8px; height:3em; font-weight:600;}
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
if "story" not in st.session_state:
    st.session_state.story = None   # initial user story
if "followups" not in st.session_state:
    st.session_state.followups = [] # list of follow-up AI responses

# ---------------------------
# HERO
# ---------------------------
st.markdown("""
<div class="hero">
<h1>🚀 TechVortex</h1>
<p>AI-Powered Agile User Story Generator with Continuous Follow-ups</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# APP CONTEXT
# ---------------------------
st.subheader("🧩 Application Context (Optional)")
app_context = st.text_area("", height=100, placeholder="Optional context to guide AI...")

# ---------------------------
# FILE UPLOAD
# ---------------------------
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
    req_text = st.text_area("📌 Requirement (Editable)", value=extracted_text, height=220)
else:
    req_text = st.text_area("📌 Enter Requirement", height=220, placeholder="Example: Users should login using OTP verification...")

# ---------------------------
# AI FUNCTIONS
# ---------------------------
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
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0.5
    )
    return resp.choices[0].message.content

def generate_followup(question):
    # Context: initial story + previous follow-ups
    messages = [{"role":"system","content":"You are a helpful AI Business Analyst."}]
    if st.session_state.story:
        messages.append({"role":"assistant","content":st.session_state.story})
    for f in st.session_state.followups:
        messages.append({"role":"assistant","content":f})
    messages.append({"role":"user","content":question})
    
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.5
    )
    ans = resp.choices[0].message.content
    st.session_state.followups.append(ans)
    return ans

# ---------------------------
# PHASE 1: INITIAL GENERATION
# ---------------------------
st.subheader("✨ Generate Initial User Story")
if st.button("Generate User Story"):
    if req_text.strip()=="":
        st.warning("Please enter a requirement.")
    else:
        with st.spinner("Generating initial user story..."):
            st.session_state.story = generate_initial_story(req_text, app_context)
        st.success("🎉 Initial User Story Generated!")
        st.markdown(st.session_state.story)

# ---------------------------
# PHASE 2: FOLLOW-UP LOOP
# ---------------------------
if st.session_state.story:
    st.subheader("💬 Ask Follow-up Questions (Continuous Loop)")
    followup_input = st.text_area("Enter follow-up question or instruction:")

    if st.button("Ask AI"):
        if followup_input.strip()=="":
            st.warning("Please enter a follow-up question.")
        else:
            with st.spinner("AI is responding..."):
                followup_ans = generate_followup(followup_input)
            st.success("✅ AI Response:")
            st.markdown(followup_ans)

# ---------------------------
# DISPLAY ALL FOLLOW-UPS
# ---------------------------
if st.session_state.followups:
    st.subheader("📝 Follow-up History")
    for idx, f in enumerate(st.session_state.followups,1):
        st.markdown(f"**Follow-up {idx}:** {f}")

# ---------------------------
# DOWNLOAD FINAL DOC
# ---------------------------
if st.session_state.story:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬇ Download User Story + Follow-ups as Word"):
            doc = Document()
            doc.add_heading("AI Generated User Story",level=1)
            doc.add_paragraph(st.session_state.story)
            for idx,f in enumerate(st.session_state.followups,1):
                doc.add_paragraph(f"Follow-up {idx}:\n{f}")
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
            st.session_state.story=None
            st.session_state.followups=[]
            st.experimental_rerun()
