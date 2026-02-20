import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="GenAI User Story Generator")
st.title("🧠 GenAI-Powered User Story Generator")
st.write("Paste your raw requirement below and generate structured Agile user stories.")

# -------------------------
# Configure Gemini
# -------------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    st.error("Gemini configuration failed.")
    st.write(str(e))
    st.stop()

# -------------------------
# Text Input
# -------------------------
requirement_text = st.text_area("Enter Raw Requirement", height=200)

# -------------------------
# Generate Stories
# -------------------------
if st.button("Generate User Stories"):

    if not requirement_text.strip():
        st.warning("Please enter a requirement.")
    else:
        prompt = f"""
        You are an expert Agile Business Analyst.

        Convert the following requirement into well-structured Agile User Stories.

        Format:

        ### User Story
        As a <role>
        I want <functionality>
        So that <business value>

        ### Acceptance Criteria
        - Point 1
        - Point 2
        - Edge cases

        Also add:
        - Clarifications Needed (if any)

        Requirement:
        {requirement_text}
        """

        try:
            with st.spinner("Generating user stories using GenAI..."):
                response = model.generate_content(prompt)

            st.subheader("📋 Generated User Stories")
            st.markdown(response.text)

        except Exception as e:
            st.error("Error from Gemini:")
            st.write(str(e))

