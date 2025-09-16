# P4 Professional Writing Assistant
#     - Email, LinkedIn Messages, LinkedIn posts

# ==================================================================================

# Importing Libraries
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from dotenv import load_dotenv
import os

# For structured output
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

# For web interface
import streamlit as st

load_dotenv()

# ==================================================================================

# Function to initialize the LLM with API key
def initialize_llm(api_key: str):
    # Set the API key in environment variables
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key
    
    llm = HuggingFaceEndpoint( 
        endpoint_url="openai/gpt-oss-20b",
        task="text-generation",
        huggingfacehub_api_token=api_key
    )
    
    return ChatHuggingFace(llm=llm)

# Function to create structured output chains
def create_structured_chains(model):
    # Parsers for structured output
    parser1 = PydanticOutputParser(pydantic_object=taskschema)
    parser2 = PydanticOutputParser(pydantic_object=linkedIntaskschema)

    instruction1 = parser1.get_format_instructions()
    instruction2 = parser2.get_format_instructions()

    prompt1 = PromptTemplate(
        template="For given input by user identify whether the task need to perform on LinkedIn or Mail.\n Input : {user_input}\n Instructions:{instruction1}",
        input_variables=['user_input'],
        partial_variables={'instruction1': instruction1}
    )

    prompt2 = PromptTemplate(
        template="For given input by user identify whether it is about a linkedIn post or LinkedIn message \n Input : {user_input}\n Instructions:{instruction2}",
        input_variables=['user_input'],
        partial_variables={'instruction2': instruction2}
    )

    structured_model_chain1 = prompt1 | model | parser1
    structured_model_chain2 = prompt2 | model | parser2
    
    return structured_model_chain1, structured_model_chain2

# ==================================================================================

# Structured output schema using Pydantic
# 1. Task Platform
class taskschema(BaseModel):
    platform : Literal["Mail", "LinkedIn"] = Field(
        description='Where will task get execute? Mail or LinkedIn'
        )

# 2. LinkedIn Task 
class linkedIntaskschema(BaseModel):
    task : Literal["Post","Message"]= Field(
        description='What is the task user want to perform? a Message or Post'
        )

# ==================================================================================

# Defining State
class AssistantState(TypedDict):
    user_input : str
    platform : Literal["Mail", "LinkedIn"]
    email : str
    LinkedIn_task : Literal["Post","Message"]
    LinkedIn_content : str
    model: object  # Added to store the model instance
    chain1: object  # Added to store structured chain 1
    chain2: object  # Added to store structured chain 2

# ==================================================================================

# Defining Function for Task Platform Identification
def get_platform(State: AssistantState):
    platform = State['chain1'].invoke({"user_input":State['user_input']})
    return{'platform': platform.platform}

# ==================================================================================

# Defining Function for LinkedIn Task Identification
def get_task(State: AssistantState):
    task = State['chain2'].invoke({"user_input":State['user_input']})
    return{'LinkedIn_task': task.task}

# ==================================================================================

# Function for generating mail
def Generate_mail(State: AssistantState):
    prompt = f'User wanted write an Mail. Understand his\her purpose of mail and write a mail as he described below. Do not add any chart or table in mail\n User Input: { State["user_input"]}\n Mail Draft:\n'
    draft_mail = State['model'].invoke(prompt).content
    return {'email': draft_mail}

# ==================================================================================

# Function for generating LinkedIn post 
def Generate_post(State: AssistantState):
    prompt = f'User wanted write a linkedIn post. Understand his\her purpose and content requirement of post and write a LinkedIn professional post as he described below.\n User Input: { State["user_input"]}\n Post Draft:\n'
    draft_post = State['model'].invoke(prompt).content
    return {'LinkedIn_content': draft_post}

# ==================================================================================

# Function for generating LinkedIn Message
def Generate_message(State: AssistantState):
    prompt = f'User wanted write a personal message through his\her account. Understand his\her purpose for this message (to get connect or to HR or to sick help from mentor or something else) and write a professional\ semi-professional message on behalf of his\her as he\she described below.\n User Input: { State["user_input"]}\n Write a short message which effectively communicate all the point mentioned.\n Message Draft:\n'
    draft_message = State['model'].invoke(prompt).content
    return {'LinkedIn_content': draft_message}

# ==================================================================================

# Conditional function for task platform
def which_platform(State:AssistantState) -> Literal["Generate_mail","get_task"]:
    if State['platform'] =="Mail":
        return "Generate_mail"
    else:
        return "get_task"
    
# ==================================================================================

# Conditional function for task platform
def which_task(State:AssistantState) -> Literal["Generate_post","Generate_message"]:
    if State['LinkedIn_task'] =="Post":
        return "Generate_post"
    else:
        return "Generate_message"
    
# ==================================================================================

# Initialize graph
graph = StateGraph(AssistantState)

# Adding nodes
graph.add_node('get_platform',get_platform)
graph.add_node('Generate_mail',Generate_mail)
graph.add_node('get_task',get_task)
graph.add_node('Generate_post',Generate_post)
graph.add_node('Generate_message',Generate_message)

# Adding edges
graph.add_edge(START,'get_platform')
graph.add_conditional_edges('get_platform',which_platform)
graph.add_edge('Generate_mail',END)
graph.add_conditional_edges('get_task', which_task)
graph.add_edge('Generate_message',END)
graph.add_edge('Generate_post',END)

# Compiling Graph
Apnagraph = graph.compile()

# ==================================================================================

# Streamlit App Interface
st.set_page_config(page_title="Writing Assistant", page_icon="✍️", layout="wide")

st.title("📝 Professional Writing Assistant")
st.markdown("---")
st.subheader("Generate professional emails, LinkedIn posts, and LinkedIn messages")

# API Key input section
st.markdown("### 🔑 API Configuration")
api_key = st.text_input(
    "Enter your Hugging Face API Key:", 
    type="password", 
    help="Get your API key from https://huggingface.co/settings/tokens"
)

st.markdown("---")

# Main input area
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 📝 Enter your writing request:")
    user_input = st.text_area(
        "Describe what you want to write...",
        placeholder="Example: I want to write a professional email to HR about...",
        height=150,
    )
    
    generate_button = st.button("✨ Generate Content", type="primary", use_container_width=True)

with col2:
    st.markdown("### 🎯 Quick Tips:")
    st.info("""
    **Be specific about:**
    - Purpose of your writing
    - Target audience
    - Tone (formal/casual)
    - Key points to include
    """)

# Generate content when button is clicked
if generate_button:
    if not api_key:
        st.error("🔑 Please enter your Hugging Face API key first!")
    elif not user_input:
        st.warning("⚠️ Please enter your writing request first!")
    else:
        try:
            with st.spinner("🤖 Initializing model and generating content..."):
                # Initialize the model with the provided API key
                model = initialize_llm(api_key)
                
                # Create structured chains
                chain1, chain2 = create_structured_chains(model)
                
                # Create initial state
                initial_state = {
                    "user_input": user_input,
                    "platform": "",
                    "email": "",
                    "LinkedIn_task": "",
                    "LinkedIn_content": "",
                    "model": model,
                    "chain1": chain1,
                    "chain2": chain2
                }
                
                # Run the graph
                result = Apnagraph.invoke(initial_state)
                
                # Display results
                st.markdown("---")
                st.markdown("### 📄 Generated Content:")
                
                # Check which type of content was generated
                if result.get('email'):
                    st.markdown("#### 📧 Email Draft:")
                    st.markdown(result['email'])
                    
                elif result.get('LinkedIn_content'):
                    linkedin_task = result.get('LinkedIn_task')
                    if linkedin_task == 'Post':
                        st.markdown("#### 📱 LinkedIn Post:")
                        st.markdown(result['LinkedIn_content'])
                    else:
                        st.markdown("#### 💬 LinkedIn Message:")
                        st.markdown(result['LinkedIn_content'])
                
                # Success message
                st.success("✅ Content generated successfully! You can copy and use it now.")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.markdown("Please check your API key and try again with a different request.")

# Footer
st.markdown("---")
