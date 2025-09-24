# ChatBot with Persistent Memory and Streaming Responses

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# =================================================================================================

llm = HuggingFaceEndpoint(
    endpoint_url="openai/gpt-oss-20b",
    task="text-generation",
    streaming=True 
    )

model = ChatHuggingFace(llm=llm)

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# =================================================================================================

def chat_node(state: ChatState):

    # take user query from state
    messages = state['messages']

    # send to llm
    response = model.invoke(messages)

    # response store state
    return {'messages': [response]}

# =================================================================================================

graph = StateGraph(ChatState)

# adding node   
graph.add_node('chat_node', chat_node)

# adding edges
graph.add_edge(START, 'chat_node')  
graph.add_edge('chat_node', END)

# Compiling graph
checkpointer = InMemorySaver()
chatbot = graph.compile(checkpointer=checkpointer)

# =================================================================================================

