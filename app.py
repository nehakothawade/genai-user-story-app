import streamlit as st
import google.generativeai as genai
from docx import Document
from pypdf import PdfReader

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="AI User Story Generator", layout="centered")

st.title("🚀 AI-Powered User Story Generator")
st.write("Enter raw text or upload a PDF/Word file to generate structured Agile user stories.")

# -------------------------
# Configure Gemini API
# -------------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-flash")
except Exception as e:
    st.error("Gemini API key not found or invalid. Please check Streamlit Secrets.")
    st.stop()

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
final_input = raw_text.strip() if raw_text.strip() else file_text.strip()

# -------------------------
# Generate User Story
# -------------------------
if st.button("Generate AI User Stories"):

    if not final_input:
        st.error("Please enter text or upload a file.")
    else:
        with st.spinner("Generating user stories using Gemini AI..."):

            prompt = f"""
            You are a professional Business Analyst.

            Convert the following requirement into structured Agile User Stories.

            Format strictly as:

            ### User Story
            As a <role>
            I want <functionality>
            So that <business value>

            ### Acceptance Criteria
            - Criteria 1
            - Criteria 2
            - Criteria 3

            Requirement:
            {final_input}
            """

            try:
                response = model.generate_content(prompt)
                st.subheader("📌 Generated User Story")
                st.markdown(response.text)

            except Exception as e:
                st.error("Error generating content. Please check API key or model access.")
