import streamlit as st
import google.generativeai as genai

# Add your API key here
genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    generation_config={
        "temperature": 0.2
    }
)

st.set_page_config(page_title="GenAI User Story Generator")

st.title("🧠 GenAI-Powered User Story Generator")
st.write("Paste your raw requirement below and generate structured Agile user stories.")

requirement_text = st.text_area("Enter Raw Requirement", height=200)

if st.button("Generate User Stories"):

    if requirement_text.strip() == "":
        st.warning("Please enter requirement text.")
    else:

        with st.spinner("Generating high-quality user stories..."):

            prompt = f"""
You are a senior Agile Business Analyst.

Convert the requirement below into high-quality user stories.

Requirement:
{requirement_text}

Instructions:
- Must follow format: As a [user], I want [goal], so that [benefit].
- Keep stories atomic.
- Provide measurable acceptance criteria.
- Identify missing or ambiguous information.
- Ask clarification questions.
- Include edge cases.
- Do NOT return JSON.
- Format output cleanly with headings and bullet points.
"""

            response = model.generate_content(prompt)

            st.subheader("📋 Generated User Stories")
            st.markdown(response.text)
