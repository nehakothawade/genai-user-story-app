import streamlit as st
import google.generativeai as genai
from docx import Document
import PyPDF2
import os

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="AI Story Generator", layout="centered")

st.title("✨ AI Story Generator")
st.write("Enter raw text OR upload a PDF/Word file to generate structured stories.")

# -------------------------
# API Key
# -------------------------
api_key = st.secrets.get("GOOGLE_API_KEY") or st.text_input("Enter your Gemini API Key", type="password")

if not api_key:
    st.warning("Please enter your Gemini API key to continue.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------
# Text Input
# -------------------------
raw_text = st.text_area("Enter Raw Text Here", height=200)

# -------------------------
# File Upload
# -------------------------
uploaded_file = st.file_uploader("Or Upload a File", type=["pdf", "docx"])

file_text = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_text += page.extract_text()

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            file_text += para.text + "\n"

# -------------------------
# Combine Input
# -------------------------
final_input = raw_text if raw_text else file_text

# -------------------------
# Generate Story
# -------------------------
if st.button("Generate Story"):
    if not final_input.strip():
        st.error("Please enter text or upload a file.")
    else:
        with st.spinner("Generating story..."):
            prompt = f"""
            Convert the following raw content into a well-structured story.
            Use clear headings and engaging narration.

            Content:
            {final_input}
            """

            response = model.generate_content(prompt)
            st.subheader("📖 Generated Story")
            st.write(response.text)
