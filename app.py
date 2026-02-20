import streamlit as st
from docx import Document
import PyPDF2
import io

st.set_page_config(page_title="GenAI User Story Generator")
st.title("🧠 GenAI-Powered User Story Generator")

st.write("Enter requirement text OR upload a PDF/Word document.")

# --- INPUT OPTIONS ---
input_option = st.radio(
    "Choose input type:",
    ("Enter Text", "Upload File")
)

requirement_text = ""

# --- OPTION 1: Direct Text ---
if input_option == "Enter Text":
    requirement_text = st.text_area("Enter Raw Requirement", height=200)

# --- OPTION 2: File Upload ---
elif input_option == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload PDF or Word file",
        type=["pdf", "docx"]
    )

    if uploaded_file is not None:

        # If PDF
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            requirement_text = text

        # If Word
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            requirement_text = text

        st.success("File processed successfully!")
        st.text_area("Extracted Text Preview", requirement_text, height=200)

# --- MOCK GENAI FUNCTION (Replace Later) ---
def generate_user_stories(text):
    if not text.strip():
        return "Please provide requirement text."

    return f"""
### 📋 Generated User Stories

**User Story 1**  
As a user, I want functionality described in the requirement, so that I achieve the intended goal.

**Acceptance Criteria**
- System processes request successfully
- Works across specified platforms
- Performance meets defined standards

**Edge Cases**
- Invalid input handling
- Network delays
- Concurrent requests

**Clarifications Needed**
- What is the expected response time?
- Are there security constraints?
"""

# --- BUTTON ---
if st.button("Generate User Stories"):

    if requirement_text.strip() == "":
        st.warning("Please enter or upload requirement text.")
    else:
        with st.spinner("Generating user stories..."):
            output = generate_user_stories(requirement_text)
            st.markdown(output)
