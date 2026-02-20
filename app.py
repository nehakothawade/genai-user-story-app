import streamlit as st
import google.generativeai as genai
from docx import Document
from pypdf import PdfReader

st.set_page_config(page_title="AI User Story Generator", layout="centered")

st.title("🚀 AI-Powered User Story Generator")
st.write("Enter raw text or upload a file to generate structured user stories using GenAI.")

# -------------------------
# Configure API Key
# -------------------------
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Gemini API Key not found. Please add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------
# Text Input
# -------------------------
raw_text = st.text_area("Enter Raw Requirement", height=200)

# -------------------------
# File Upload
# -------------------------
uploaded_file = st.file_uploader("Or Upload PDF/Word File", type=["pdf", "docx"])

file_text = ""

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            file_text += page.extract_text() or ""

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            file_text += para.text + "\n"

# -------------------------
# Combine Input
# -------------------------
final_input = raw_text if raw_text.strip() else file_text

# -------------------------
# Generate User Story with GenAI
# -------------------------
if st.button("Generate AI User Stories"):

    if not final_input.strip():
        st.error("Please enter text or upload a file.")
    else:
        with st.spinner("Generating user stories using AI..."):

            prompt = f"""
            You are a Business Analyst.

            Convert the following requirement into professional Agile User Stories.

            Format strictly as:

            ### User Story
            As a <role>
            I want <functionality>
            So that <business value>

            ### Acceptance Criteria
            - Point 1
            - Point 2
            - Point 3

            Requirement:
            {final_input}
            """

            response = model.generate_content(prompt)

            st.subheader("📌 Generated User Stories")
            st.markdown(response.text)
