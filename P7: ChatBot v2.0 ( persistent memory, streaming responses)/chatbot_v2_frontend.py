import streamlit as st
from langchain_core.messages import HumanMessage 
from chatbot_v2_backend import chatbot

# Streamlit Web App Interface
st.title("AI Chatbot v2.0")
st.write("Chat with your AI assistant with persistent memory and streaming responses")


# Initializing session state for conversation history
if "conversation" not in st.session_state:
    st.session_state['conversation'] = []

for chat in st.session_state['conversation']:
    with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state['conversation'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)


    # Prepare state for the chatbot
    state = {
        "messages": [HumanMessage(content=user_input)]
    }

    # Configuration for streaming response
    config = {'configurable': {'thread_id': 'thread-1'}}

    # Get response from chatbot
    with st.chat_message("assistant"):
        response = st.write_stream(
            message.content for message , meta in chatbot.stream(
                state,
                config=config,
                stream_mode= 'messages'
            )
            )
        
        
    st.session_state['conversation'].append({"role": "assistant", "content":response})

    