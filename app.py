import streamlit as st

st.set_page_config(page_title="GenAI User Story Generator")
st.title("🧠 GenAI-Powered User Story Generator")
st.write("Paste your raw requirement below and generate structured Agile user stories (Demo Mode).")

# Text input from user
requirement_text = st.text_area("Enter Raw Requirement", height=200)

def mock_generate_user_stories(req_text):
    """
    This is a mock function to simulate GenAI output.
    Replace this with real model call when API key is available.
    """
    if not req_text.strip():
        return "Please enter a requirement text to generate stories."
    
    # Very simple mock logic
    stories = f"""
**User Story 1:**  
As a user, I want to reset my password using OTP, so that I can access my account if I forget my password.  
**Acceptance Criteria:**  
- OTP is sent immediately when requested  
- Works on both mobile and web  
- Edge case: Multiple OTP requests should not cause conflicts  

**Clarifications Needed:**  
- Maximum OTP expiry time?  
- Should we lock account after multiple failed OTP attempts?

**User Story 2:**  
As a system, I want to log OTP delivery failures, so that delayed or failed OTPs can be monitored.  
**Acceptance Criteria:**  
- Failures logged with timestamp  
- Alerts sent to support team if OTP delayed  
- Edge case: Network errors on mobile
"""
    return stories

# Button to generate stories
if st.button("Generate User Stories"):
    with st.spinner("Generating user stories..."):
        output = mock_generate_user_stories(requirement_text)
        st.subheader("📋 Generated User Stories")
        st.markdown(output)
