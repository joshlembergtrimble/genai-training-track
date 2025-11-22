import streamlit as st
import requests
import os

# API endpoint configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Call the agent API
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"query": prompt},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()["response"]
    except requests.exceptions.RequestException as e:
        result = f"Error connecting to agent: {str(e)}"
    
    # Add assistant message to history and display
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("assistant").write(result)
