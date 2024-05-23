import streamlit as st
import openai
import pickle
import os

st.title("GPT Chatbot")

openai.api_key = st.secrets['OPENAI_API_KEY']

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

# Check if chat logs exist and load them:
if os.path.exists('chat_logs/chat_logs.pickle'):
    with open('chat_logs/chat_logs.pickle', 'rb') as handle:
        st.session_state.messages = pickle.load(handle)
elif "messages" not in st.session_state:
    st.session_state.messages = []

# Display history message
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# React to user input
if prompt := st.chat_input('What is up?'):
    # Display user message in chat message
    with st.chat_message('user'):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ""
        for res in openai.chat.completions.create(
                model=st.session_state['openai_model'],
                messages=[
                    {'role': m['role'], 'content': m['content']}
                    for m in st.session_state.messages
                ],
                stream=True
        ):
            if res.choices[0].delta.content is not None:
                full_response += res.choices[0].delta.content
            message_placeholder.markdown(full_response + "| ")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({'role': 'assistant', 'content': full_response})

    # Save the updated chat logs:
    with open('chat_logs/chat_logs.pickle', 'wb') as handle:
        pickle.dump(st.session_state.messages, handle, protocol=pickle.HIGHEST_PROTOCOL)

with st.sidebar:
    if clear_btn_clicked := st.button("Clear"):
        st.session_state.messages = []

        # Delete the chat logs when messages are cleared:
        if os.path.exists('chat_logs/chat_logs.pickle'):
            os.remove('chat_logs/chat_logs.pickle')

        st.rerun()
