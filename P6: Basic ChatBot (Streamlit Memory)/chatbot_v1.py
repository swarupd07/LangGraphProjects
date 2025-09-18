# Basic Chat Bot with memory

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
import streamlit as st

from dotenv import load_dotenv
load_dotenv()


# ====================================================================================

class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

llm = HuggingFaceEndpoint(
    endpoint_url="openai/gpt-oss-20b",
    task="text-generation",
    )

model = ChatHuggingFace(llm=llm)

# ====================================================================================

def chat_node(state: ChatState):

    # take user query from state
    messages = state['messages']

    # send to llm
    response = model.invoke(messages)

    # response store state
    return {'messages': [response]}

# ====================================================================================

graph = StateGraph(ChatState)
# adding node
graph.add_node('chat_node', chat_node)
# adding edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)
# Compiling graph
chatbot = graph.compile()

# ====================================================================================

# Streamlit Web App Interface

st.title("AI Chatbot v1.0")
st.write("Chat with your AI assistant")
    
# Initializing session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []
    st.session_state.messages = []
    
# Sidebar for conversation history management
with st.sidebar:
    st.subheader("Conversation History")
        
    if st.button("Clear Conversation"):
        st.session_state.conversation = []
        st.session_state.messages = []
        st.rerun()
        

# Displaying conversation history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.write(message["content"])
    
# Chat input

prompt = st.chat_input("Ask: ")
if prompt:
    # Add user message to conversation
    st.session_state.conversation.append({"role": "You", "content": prompt})
    with st.chat_message("You"):
        st.write(prompt)
        
    # Convert conversation to LangChain messages
    
    msg = st.session_state.conversation[-1]
    if msg["role"] == "You":
        st.session_state.messages.append(HumanMessage(content=msg["content"]))
    elif msg["role"] == "AI":
        st.session_state.messages.append(AIMessage(content=msg["content"]))
        
    # Get response from chatbot
    with st.chat_message("AI"):
        with st.spinner("Thinking..."):
                # Use your existing chatbot
                response = chatbot.invoke({"messages": st.session_state.messages})
                bot_message = response["messages"][-1].content
                    
                st.write(bot_message)
                    
                # Add bot response to conversation
                st.session_state.conversation.append({
                        "role": "assistant", 
                        "content": bot_message
                    })
    


