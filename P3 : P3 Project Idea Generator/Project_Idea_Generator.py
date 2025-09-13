# P3 : Project Idea Generator

# Importing necessary libraries
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Dict, List

# For structured output
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

# For web interface
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ==================================================================================

# Model Initialization
llm = HuggingFaceEndpoint(
    endpoint_url="openai/gpt-oss-20b",
    task="text-generation",
    )

model = ChatHuggingFace(llm=llm)

# ==================================================================================

# Structured output schema using Pydantic
class ProjectIdeaSchema(BaseModel):
    project_idea: List[str] = Field(description="List of project ideas based on the input details")
    project_description: List[str] = Field(description="List of project descriptions corresponding to each project idea")

parser = PydanticOutputParser(pydantic_object=ProjectIdeaSchema)
instructions = parser.get_format_instructions()

# Prompt template
prompt = PromptTemplate(
    input_variables=["project_domain", "skills", "complexity_level", "number_of_ideas"],
    template="""Generate {number_of_ideas} project ideas in the domain of {project_domain}, which are based on skills {skills} and are of {complexity_level}  level.
    {instructions}""",
    partial_variables={"instructions": instructions}
)

structured_output_chain = prompt | model | parser

# ==================================================================================

# Defining State

class ProjectInfo(TypedDict):
    # Input Variables
        # Set 1
    project_domain: str
    skills: str
    number_of_ideas: int
    complexity_level: str
        # Set 2
    input_idea: str

    # Output Variables
        # Set 1
    project_idea: List[str]
    project_description: List[str] 
    other_skills_to_learn: str
        # Set 2
    steps_to_implement: str
    skills_required: str

    # Actual Output
    output : str

# ==================================================================================

# Function to generate project ideas based on user input
def generate_project_ideas(Info: ProjectInfo) :
    if Info["input_idea"]:
        return {"project_idea": [], "project_description": []}

    response = structured_output_chain.invoke({
        "project_domain": Info['project_domain'],
        "skills": Info['skills'],
        "complexity_level": Info['complexity_level'],
        "number_of_ideas": Info['number_of_ideas']
    })

    return {"project_idea": response.project_idea, "project_description": response.project_description}

# ==================================================================================

# Function to provide other relevant skills to learn
def suggest_other_skills(Info: ProjectInfo):
    if Info["input_idea"]:
        return {"other_skills_to_learn": ""}

    prompt = f"Suggest other relevant skills which get used to build projects in the domain of {Info['project_domain']} based on skills {Info['skills']} and of {Info['complexity_level']} level. Only give me the 4-5 skills in next line without any explanation."
    response = model.invoke(prompt).content
    return {"other_skills_to_learn": response}

# ==================================================================================

# Function to provide steps to implement the project idea
def provide_steps_to_implement(Info: ProjectInfo):
    if not Info['input_idea']:
        return {"steps_to_implement": ""}
    
    prompt1 = f'User hase given us input: {Info["input_idea"]}, based on these input give me redefined, well structured project idea and all specifications which user has mentioned'

    refined_idea = model.invoke(prompt1).content

    prompt2 = f'give me step to follow to complete the following project\n Project: {refined_idea}\n\n give me only steps. Give each step in next line'

    result = model.invoke(prompt2).content

    return {"steps_to_implement": result}

# ==================================================================================

# Function to give required skills for project idea
def provide_skills_required(Info: ProjectInfo):
    if not Info['input_idea']:
        return {"skills_required": ""}

    prompt = f'For the given Project idea give me skills which are required to complete the project.\n Project Idea: {Info["input_idea"]}\n Skills:'
    result = model.invoke(prompt).content

    return {"skills_required": result}

# ==================================================================================

# Function for Final Output 
def final_output(Info: ProjectInfo) :
    if Info["input_idea"]:
        prompt = f' For given Project idea: {Info["input_idea"]}\n The Skills Required are: {Info["skills_required"]}\n and Step to follow for project completion are: {Info["steps_to_implement"]}\n\n Now give me well structured and user frinedly ouput as:\n An encoraging message based on the quality of project\n Project Title: \n\n Skills Required: \n\n Steps to follow: \n'
        output = model.invoke(prompt).content
        
        return {"output": output}
    
    prompt = f'For given input:\n Project domain:{Info["project_domain"]}\n Skills learned:{Info["skills"]}\n\n The generated project ideas are: {Info["project_idea"]} \n and for each these {Info["number_of_ideas"]} project idea, the descriptions are:{Info["project_description"]} \n\n Draft well structured response to user based on the above data, which also include additional skills to learn suggestion\n Additional skills: {Info["other_skills_to_learn"]}\n\n Response:\n Encouraging Message based on input data and complexity level{Info["complexity_level"]} ( Do not mention it is an Encouraging Message)\n Project and short description for all project idea\n Other skills to learn:'
    output = model.invoke(prompt).content

    return {"output": output}

# ==================================================================================

# Intitilising graph
graph = StateGraph(ProjectInfo)

# Adding nodes
graph.add_node("generate_project_ideas", generate_project_ideas)
graph.add_node("suggest_other_skills",suggest_other_skills)
graph.add_node("provide_steps_to_implement",provide_steps_to_implement)
graph.add_node("provide_skills_required",provide_skills_required)
graph.add_node("final_output",final_output)

# Adding Edges
# Layer 1
graph.add_edge(START,"generate_project_ideas")
graph.add_edge(START,"suggest_other_skills")
graph.add_edge(START,"provide_steps_to_implement")
graph.add_edge(START,"provide_skills_required")

# Layer 2
graph.add_edge("generate_project_ideas","final_output")
graph.add_edge("suggest_other_skills","final_output")
graph.add_edge("provide_steps_to_implement","final_output")
graph.add_edge("provide_skills_required","final_output")

# Layer 3
graph.add_edge("final_output", END)

# Compiling Graph

PIG_graph = graph.compile()

# ==================================================================================

# Streamlit App for Project Idea Generator
# Page configuration
st.set_page_config(
    page_title="Project Idea Generator",
    page_icon="💡",
    layout="wide"
)

# Title and description
st.title("💡 Project Idea Generator")
st.markdown("Generate personalized project ideas or get implementation guidance for your existing ideas!")

# Sidebar for mode selection
st.sidebar.title("Choose Your Mode")
mode = st.sidebar.radio(
    "What would you like to do?",
    ["Generate New Project Ideas", "Get Help with Existing Idea"]
)

# Main content area
if mode == "Generate New Project Ideas":
    st.header("🚀 Generate New Project Ideas")
    st.session_state.result = None
    col1, col2 = st.columns(2)
    
    with col1:
        project_domain = st.text_input(
            "Project Domain",
            placeholder="e.g., Web Development, Data Science, Mobile Apps",
            help="Enter the field or domain you're interested in"
        )
        
        skills = st.text_area(
            "Your Current Skills",
            placeholder="e.g., Python, JavaScript, HTML/CSS, Machine Learning",
            help="List the skills you already have"
        )
    
    with col2:
        complexity_level = st.selectbox(
            "Complexity Level",
            ["Beginner", "Intermediate", "Advanced"]
        )
        
        number_of_ideas = st.slider(
            "Number of Ideas to Generate",
            min_value=1,
            max_value=10,
            value=3,
            help="How many project ideas would you like?"
        )
    
    # Generate button
    if st.button("🎯 Generate Project Ideas"):
        if project_domain and skills:
            with st.spinner("Generating your personalized project ideas..."):
                try:
                    # Prepare input for the graph
                    input_data = {
                        "project_domain": project_domain,
                        "skills": skills,
                        "complexity_level": complexity_level,
                        "number_of_ideas": number_of_ideas,
                        "input_idea": "",  # Empty for generation mode
                        "project_idea": [],
                        "project_description": [],
                        "other_skills_to_learn": "",
                        "steps_to_implement": "",
                        "skills_required": "",
                        "output": ""
                    }
                    
                    # Run the graph
                    result = PIG_graph.invoke(input_data)
                    st.session_state.result = result
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please fill in both Project Domain and Skills fields.")

else:  
    st.header("🔧 Get Implementation Help")
    
    input_idea = st.text_area(
        "Describe Your Project Idea",
        placeholder="e.g., I want to build a web application that helps users track their daily expenses with charts and analytics",
        height=150,
        help="Describe your project idea in detail"
    )
    
    # Analyze button
    if st.button("📋 Get Implementation Guide"):
        if input_idea.strip():
            with st.spinner("Analyzing your project and creating implementation guide..."):
                try:
                    # Prepare input for the graph
                    input_data = {
                        "project_domain": "",
                        "skills": "",
                        "complexity_level": "",
                        "number_of_ideas": 0,
                        "input_idea": input_idea,
                        "project_idea": [],
                        "project_description": [],
                        "other_skills_to_learn": "",
                        "steps_to_implement": "",
                        "skills_required": "",
                        "output": ""
                    }
                    
                    # Run the graph
                    result = PIG_graph.invoke(input_data)
                    st.session_state.result = result

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please describe your project idea.")

# Display results
if st.session_state.result:
    st.markdown("---")
    st.header("📋 Results")
    
    # Display the formatted output
    if st.session_state.result.get("output"):
        st.markdown(st.session_state.result["output"])
    
    # Clear results button
    if st.button("🔄 Generate New Ideas"):
        st.session_state.result = None
        st.rerun()
