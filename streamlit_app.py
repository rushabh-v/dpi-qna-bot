import streamlit as st
from openai import OpenAI
import time
import datetime

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def check_run_status(thread_id, run):
    while True:
        run_info = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_info.status == "completed":
            break
        time.sleep(0.1)

if __name__ == '__main__':
    st.title("India Stack (DPI) QnA")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Initialize thread for the session if it doesn't exist
    if "thread" not in st.session_state:
        st.session_state.thread = client.beta.threads.create()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send user message to OpenAI assistant
        message = client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=prompt
        )

        # Add current time context for the assistant
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="assistant",
            content=f"Time right now: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        )

        # Create a run with the assistant
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id="asst_bxA0B599UQ2vtuTyua2juDhH",
            instructions=""
        )

        # Check run status until completion
        check_run_status(st.session_state.thread.id, run)

        # Display assistant response
        with st.chat_message("assistant"):
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread.id
            )
            response_text = messages.data[0].content[0].text.value
            st.write(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
