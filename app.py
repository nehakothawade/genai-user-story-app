import streamlit as st
from google import genai

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(page_title="GenAI User Story Generator", page_icon="🧠")
st.title("🧠 GenAI-Powered User Story Generator")
st.write("Convert raw requirements into structured Agile User Stories using Gemini.")

# ----------------------------------
# Configure Gemini Client
# ----------------------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("🚨 Gemini configuration failed.")
    st.exception(e)
    st.stop()

# ----------------------------------
# User Input
# ----------------------------------
requirement_text = st.text_area("Enter Raw Requirement", height=250)

story_count = st.selectbox(
    "Number of User Stories to Generate",
    [1, 2, 3, 4, 5],
    index=1
)

# ----------------------------------
# Generate Stories
# ----------------------------------
if st.button("Generate User Stories"):

    if not requirement_text.strip():
        st.warning("Please enter a requirement.")
        st.stop()

    prompt = f"""
You are a highly experienced Agile Business Analyst.

Convert the following requirement into EXACTLY {story_count} well-structured Agile User Stories.

For EACH story use this format:

### User Story
As a <role>
I want <functionality>
So that <business value>

### Acceptance Criteria
- Functional requirement points
- Validation rules
- Edge cases
- Error handling scenarios

### Clarifications Needed
- Any missing business rules
- Any assumptions made

Make output clean, professional, and hackathon-demo ready.

Requirement:
{requirement_text}
"""

    try:
        with st.spinner("Generating user stories using Gemini..."):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

        st.success("✅ User Stories Generated Successfully!")

        st.subheader("📋 Generated User Stories")
        st.markdown(response.text)

    except Exception as e:
        st.error("🚨 Error from Gemini API")
        st.exception(e)
