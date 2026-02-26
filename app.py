# ------------------------------------------------
# DISPLAY STORY + FOLLOW-UP LOOP
# ------------------------------------------------
if st.session_state.generated_story:

    st.success("🎉 User Story Generated")
    st.markdown(st.session_state.generated_story)
    st.divider()

    # -----------------------------
    # AI FOLLOW-UP FLOW
    # -----------------------------
    if st.session_state.current_question:

        st.info(f"🤖 AI Follow-up Question:\n\n{st.session_state.current_question}")

        user_answer = st.text_area("Your Answer to AI Question:", height=120, key="ai_answer")

        if st.button("➤ Submit AI Answer"):

            if user_answer.strip() != "":

                with st.spinner("Thinking..."):

                    follow_prompt = f"""
User Story:
{st.session_state.generated_story}

Previous Question:
{st.session_state.current_question}

User Answer:
{user_answer}

1. Acknowledge briefly.
2. Ask ONE new intelligent clarification question.
Do NOT rewrite the story.
"""

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": follow_prompt}],
                        temperature=0.4,
                    )

                    output = response.choices[0].message.content

                    parts = output.strip().split("?")
                    acknowledgement = "?".join(parts[:-1])
                    next_question = parts[-1] + "?"

                    st.session_state.chat_history.append({
                        "type": "ai_followup",
                        "question": st.session_state.current_question,
                        "answer": user_answer,
                        "ai_ack": acknowledgement
                    })

                    st.session_state.current_question = next_question
                    st.rerun()

    st.divider()

    # -----------------------------
    # USER OWN QUESTION FLOW
    # -----------------------------
    st.subheader("💬 Ask Your Own Clarification")

    user_question = st.text_area("Your Question:", height=120, key="user_question_box")

    if st.button("➤ Ask Your Question"):

        if user_question.strip() != "":

            with st.spinner("Thinking..."):

                user_prompt = f"""
User Story:
{st.session_state.generated_story}

User Question:
{user_question}

Answer clearly.
Do NOT rewrite the story.
"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=0.4,
                )

                answer = response.choices[0].message.content

                st.session_state.chat_history.append({
                    "type": "user_question",
                    "question": user_question,
                    "answer": answer
                })

                st.rerun()

    st.divider()

    # -----------------------------
    # CHAT HISTORY DISPLAY
    # -----------------------------
    if st.session_state.chat_history:

        st.subheader("🧠 Discussion History")

        for chat in st.session_state.chat_history:

            if chat["type"] == "ai_followup":
                st.markdown(f"**🤖 AI Asked:** {chat['question']}")
                st.markdown(f"**You Answered:** {chat['answer']}")
                st.markdown(f"**AI Response:** {chat['ai_ack']}")
                st.divider()

            elif chat["type"] == "user_question":
                st.markdown(f"**🙋 You Asked:** {chat['question']}")
                st.markdown(f"**🤖 AI Answered:** {chat['answer']}")
                st.divider()

    # -----------------------------
    # DOWNLOAD
    # -----------------------------
    if st.button("✅ Download & Finish"):

        doc = Document()
        doc.add_heading("AI Generated User Story", level=1)
        doc.add_paragraph(st.session_state.generated_story)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇ Download File",
            data=buffer,
            file_name=f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
