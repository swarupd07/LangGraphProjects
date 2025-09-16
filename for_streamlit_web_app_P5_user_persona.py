# P5 User Persona Generator 

# ==================================================================================

# Importing Libraries
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Annotated
import operator
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

# Function to create structured chain
def create_structured_chain(model):
    parser = PydanticOutputParser(pydantic_object=Users)
    instructions = parser.get_format_instructions()

    prompt = PromptTemplate(
        template='From the given input text extract the users profile. Examples : Doctor, Engineer, Driver, farmer, and etc\n Input: {profiles}\n\n Instructions: {instructions}',
        input_variables=['profiles'],
        partial_variables={'instructions': instructions}
    )

    return prompt | model | parser

# ==================================================================================

# Structured output schema using Pydantic
class Users(BaseModel):
    users: List[str] = Field(description='List of product users')

# ==================================================================================

# Defining State
class personaState(TypedDict):
    product_details: str
    market_details: str
    additional_details: str
    users: str
    user_list: List[str]
    user_count: int
    counter: int
    user_persona: Annotated[List[str], operator.add]
    model: object  # Added to store the model instance
    structured_chain: object  # Added to store structured chain

# ==================================================================================

# Function to get user profile list
def get_profiles(state: personaState):
    users = state['structured_chain'].invoke({'profiles': state['users']})
    user_count = len(users.users)
    return {'user_list': users.users, 'user_count': user_count}

# ==================================================================================

def get_persona(state: personaState):
    counter = state.get('counter', 0)
    user = state['user_list'][counter]
    template = '''
**1. Header / Basic Info**

* Persona Name (a fictional name, e.g. "Tech-Savvy Tara")
* Title / Role (e.g. "Teacher", "Freelancer", "IT Manager")
* Demographics

  * Age
  * Location / City / Country
  * Education level
  * Occupation / Industry
  * Other relevant demographic traits (income range, gender, etc.)

**2. Background / Context**

* A short biography or description: what their life / work is like, what contexts they use your product in.
* Experience with technology / skill level (beginner / intermediate / expert)
* Everyday environment: where and how they do tasks (mobile / desktop, on the move, office etc.)

**3. Goals & Motivations**

* What they want to achieve using your product or in general (both short-term and long-term goals)
* What motivates them: why they care about those goals; what drives their behavior

**4. Behaviors & Preferences**

* How they use similar products now
* Frequency of use / when / in which contexts
* Technology preferences (devices, platforms, level of customisation, etc.)
* Communication / learning style (do they like video tutorials, reading documentation, hands-on learning, etc.)

**5. Pain Points / Challenges**

* What frustrates them / what obstacles prevent them from achieving their goals
* What problems they regularly face, especially in context of your domain or solution

**6. Needs**

* What kind of product features or support would help them most
* What expectations they have from a solution

**7. "A Day in the Life" or Scenario / Use-Case**

* A short narrative: what a typical day looks like, where the product fits in, when and why they would use it
* Could include what steps they would take to achieve something, showing touchpoints with your product

**8. Quote / Voice**

* A quote that captures their attitude or frustration, taken (ideally) from an interview or survey ("I hate waiting for the page to load…" etc.)

**9. Personality & Psychographics**

* Traits (e.g. "analytical", "social", "organized", "risk-averse", etc.)
* Values / beliefs relevant to product usage
* Attitudes (towards technology, innovation, change, etc.)

**10. Technical / Environmental Constraints**

* Devices used (phone, laptop, etc.) and browser/OS if relevant
* Network constraints (slow internet, data limits)
* Accessibility needs (e.g. vision, hearing etc.)

**11. Preferred Channels & Influences**

* How they prefer to research / discover tools / get help (forums, social media, recommendations, docs, YouTube etc.)
* Which influencers, brands or platforms they trust

**12. Opportunities / Solution Ideas** *(optional but useful)*

* Key opportunities for design or product improvements based on their challenges and needs
* Possible features or interventions that might resonate well with this persona

**13. Measuring Success** *(optional)*

* What metrics or signals would show that your product is satisfying their needs (e.g. engagement, retention, task completion rate, satisfaction etc.)'''

    prompt = f'User has a product, whose details are : {state["product_details"]}\n The market details where product is going are : {state["market_details"]}\n Analyze the product details, market details and generate User persona for\n User: {user}\n\n {template}\n consider additional details provided by user: {state["additional_details"]}\n Response'
    
    result = state['model'].invoke(prompt).content
    counter = state['counter'] + 1
    return {'user_persona': [result], 'counter': counter}

# ==================================================================================

# Defining Iterating Function
def iterator(state: personaState):
    if state['counter'] == state['user_count']:
        return "END"
    else:
        return 'get_persona'
    
# ==================================================================================

# Graph Initializing
graph = StateGraph(personaState)

# Adding nodes
graph.add_node('get_profiles', get_profiles)
graph.add_node('get_persona', get_persona)

# Adding Edges
graph.add_edge(START, "get_profiles")
graph.add_edge('get_profiles', 'get_persona')
graph.add_conditional_edges('get_persona', iterator, {'END': END, 'get_persona': 'get_persona'})

# Compiling graph
persona_graph = graph.compile()

# ==================================================================================

# Streamlit App Code

st.set_page_config(page_title="User Persona Generator", page_icon="🧑", layout="wide")

st.title("🧑‍💼 User Persona Generator")
st.markdown("---")
st.subheader("Generate detailed user personas for your product")

# API Key input section
st.markdown("### 🔑 API Configuration")
api_key = st.text_input(
    "Enter your Hugging Face API Key:", 
    type="password", 
    help="Get your API key from https://huggingface.co/settings/tokens"
)

st.markdown("---")

# Create two columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    # Input fields
    st.header("📦 Product Information")
    product_details = st.text_area(
        "Product or Service Details", 
        placeholder="Describe your product or service in detail...",
        height=100
    )

    st.header("🎯 Market Information")
    market_details = st.text_area(
        "Market Details", 
        placeholder="Describe your target market, industry, competition...",
        height=100
    )

    st.header("👥 User Information")
    users = st.text_area(
        "Target Users", 
        placeholder="List the types of users (e.g., doctors, engineers, students, teachers)...",
        height=80
    )

    st.header("➕ Additional Details")
    additional_details = st.text_area(
        "Additional Details or Instructions", 
        placeholder="Any other specific requirements or instructions...",
        height=80
    )

with col2:
    # Sidebar with instructions
    st.markdown("### 📋 Instructions")
    st.info("""
    **Steps to Generate Personas:**
    
    1. **Enter API Key** - Your HuggingFace token
    2. **Product Details** - Describe your product/service
    3. **Market Info** - Target market & industry context  
    4. **User Types** - List different user categories
    5. **Additional Info** - Any specific requirements
    6. **Generate** - Click to create detailed personas
    """)
    
    st.markdown("### 💡 Tips")
    st.success("""
    **For Better Results:**
    - Be specific about your product features
    - Include target demographics
    - Mention use cases and scenarios
    - Add industry-specific details
    """)

# Generate button
st.markdown("---")
generate_button = st.button(
    "🚀 Generate User Personas", 
    type="primary", 
    use_container_width=True
)

if generate_button:
    if not api_key:
        st.error("🔑 Please enter your Hugging Face API key first!")
    elif not product_details or not market_details or not users:
        st.error("⚠️ Please fill in all required fields (Product Details, Market Details, and Users)")
    else:
        try:
            with st.spinner("🤖 Initializing model and generating detailed user personas..."):
                # Initialize the model with the provided API key
                model = initialize_llm(api_key)
                
                # Create structured chain
                structured_chain = create_structured_chain(model)
                
                # Create state for the graph
                initial_state = {
                    'product_details': product_details,
                    'market_details': market_details,
                    'additional_details': additional_details,
                    'users': users,
                    'user_list': [],
                    'user_count': 0,
                    'counter': 0,
                    'user_persona': [],
                    'model': model,
                    'structured_chain': structured_chain
                }
                
                # Run the graph
                result = persona_graph.invoke(initial_state)
                
                # Display results
                st.success(f"✅ {len(result['user_persona'])} User personas generated successfully!")
                
                # Display each persona in an expandable section
                for i, persona in enumerate(result['user_persona']):
                    with st.expander(f"👤 Persona {i+1} - {result['user_list'][i]}", expanded=True):
                        st.markdown(persona)
                        st.markdown("---")
                
                # Option to download results
                personas_text = "\n\n" + "="*50 + "\n\n".join([
                    f"PERSONA {i+1}: {result['user_list'][i]}\n\n{persona}" 
                    for i, persona in enumerate(result['user_persona'])
                ])
                
                st.download_button(
                    label="📥 Download All Personas",
                    data=personas_text,
                    file_name="user_personas.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.markdown("Please check your API key and try again.")

# Footer
st.markdown("---")
