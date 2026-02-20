import streamlit as st
from groq import Groq

# ----------------------------------
# Page Setup
# ----------------------------------
st.set_page_config(page_title="Groq GenAI User Story Generator", page_icon="🚀")
st.title("🚀 Groq-Powered User Story Generator")
st.write("Generate Agile user stories using LLaMA 3 via Groq (Free Tier).")

# ----------------------------------
# Configure Groq
# ----------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception as e:
    st.error("Groq configuration failed.")
    st.exception(e)
    st.stop()

# ----------------------------------
# Input
# ----------------------------------
requirement_text = st.text_area("Enter Raw Requirement", height=250)

# ----------------------------------
# Generate
# ----------------------------------
if st.button("Generate User Stories"):

    if not requirement_text.strip():
        st.warning("Please enter a requirement.")
        st.stop()

    prompt = f"""
You are an expert Agile Business Analyst.

Convert the following requirement into structured Agile User Stories.

Format:

### User Story
As a <role>
I want <functionality>
So that <business value>

### Acceptance Criteria
- Functional requirement
- Validation rules
- Edge cases

### Clarifications Needed

Requirement:
{requirement_text}
"""

    try:
        with st.spinner("Generating with Groq LLaMA 3..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

        output = response.choices[0].message.content

        st.success("User Stories Generated Successfully!")
        st.markdown(output)

    except Exception as e:
        st.error("Error from Groq API")
        st.exception(e)

