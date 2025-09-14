# P5 User Persona Generator 

# ==================================================================================

# Importing Libraries
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Annotated
import operator
from dotenv import load_dotenv

# For structured output
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

# For web interface
import streamlit as st

load_dotenv()

# ==================================================================================

# Model Initilisation
llm = HuggingFaceEndpoint( 
    endpoint_url= "openai/gpt-oss-20b",
    task="text-generation"
    )

model = ChatHuggingFace(llm= llm)

# ==================================================================================

# Structured output schema using Pydantic
class Users(BaseModel):
    users :List[str] = Field(description='List of prodect users')

parser = PydanticOutputParser(pydantic_object=Users)
instructions = parser.get_format_instructions()

prompt = PromptTemplate(
    template='From the givem input text extract the users profile. Examples : Doctor, Engineer, Driver, farmer, and etc\n Input: {profiles}\n\n Instructions: {instructions}',
    input_variables=['profiles'],
    partial_variables={'instructions': instructions}
)

structured_model = prompt | model | parser

# ==================================================================================

# Defining State
class personaState(TypedDict):
    product_details: str
    market_details : str
    aditional_details : str
    users : str
    user_list : List[str]
    user_count: int
    counter :  int = 0
    user_persona : Annotated[List[str], operator.add]
# ==================================================================================

# Function to get user profile list
def get_profiles(state: personaState):
    users = structured_model.invoke({'profiles': state['users']})
    user_count = len(users.users)
    return {'user_list': users.users, 'user_count': user_count}

# ==================================================================================

def get_persona(state: personaState):
    counter = state.get('counter',0)
    user = state['user_list'][counter]
    template = '''
**1. Header / Basic Info**

* Persona Name (a fictional name, e.g. “Tech-Savvy Tara”)
* Title / Role (e.g. “Teacher”, “Freelancer”, “IT Manager”)
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

**7. “A Day in the Life” or Scenario / Use-Case**

* A short narrative: what a typical day looks like, where the product fits in, when and why they would use it
* Could include what steps they would take to achieve something, showing touchpoints with your product

**8. Quote / Voice**

* A quote that captures their attitude or frustration, taken (ideally) from an interview or survey (“I hate waiting for the page to load…” etc.)

**9. Personality & Psychographics**

* Traits (e.g. “analytical”, “social”, “organized”, “risk-averse”, etc.)
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

    prompt= f'User has a product, whose details are : {state['product_details']}\n The market details where product is going are : {state['market_details']}\n Analysis the product details, market details and generate User persona for\n User: {user}\n\n {template}\n consider additional details provides by user: { state['aditional_details']}\n Response'
    
    result = model.invoke(prompt).content
    counter = state['counter'] + 1
    return {'user_persona':[result], 'counter': counter}

# ==================================================================================

# Defining Iterating Function
def interator(state: personaState):
    if state['counter'] == state['user_count']:
        return "END"
    else:
        return 'get_persona'
    
# ==================================================================================

# Graph Initilising
graph = StateGraph(personaState)

# Adding nodes
graph.add_node('get_profiles', get_profiles)
graph.add_node('get_persona', get_persona)

# Adding Edges
graph.add_edge(START, "get_profiles")
graph.add_edge('get_profiles', 'get_persona')
graph.add_conditional_edges('get_persona', interator,{'END': END, 'get_persona': 'get_persona'})

# Compiling graph
persona_graph = graph.compile()

# ==================================================================================

# strelit 

# Streamlit App Code

st.set_page_config(page_title="User Persona", page_icon="🧑", layout="wide")

st.title("User Persona Generator")
st.write("Generate detailed user personas for your product")

# Input fields
st.header("Product Information")
product_details = st.text_area("Product or service Details", placeholder="Describe your product...")

st.header("Market Information")
market_details = st.text_area("Market Details", placeholder="Describe your target market...")

st.header("User Information")
users = st.text_area("Users", placeholder="List the types of users (e.g., doctors, engineers, students)...")

st.header("Additional Details")
additional_details = st.text_area("Additional Details or instructions", placeholder="Any other instructions...")

# Generate button
if st.button("Generate User Personas"):
    if product_details and market_details and users:
        with st.spinner("Generating user personas..."):
            # Create state for the graph
            initial_state = {
                'product_details': product_details,
                'market_details': market_details,
                'aditional_details': additional_details,
                'users': users,
                'user_list': [],
                'user_count': 0,
                'counter': 0,
                'user_persona': []
            }
            
            # Run the graph
            result = persona_graph.invoke(initial_state)
            
            # Display results
            st.success("User personas generated successfully!")
            
            for i, persona in enumerate(result['user_persona']):
                st.header(f"Persona {i+1}")
                st.write(persona)
                st.divider()
    else:
        st.error("Please fill in all required fields (Product Details, Market Details, and Users)")

# sidebar with instructions
st.sidebar.title("Instructions")
st.sidebar.write("""
1. Enter your product details
2. Describe your target market
3. List the types of users
4. Add any additional details or instructions
5. Click 'Generate User Personas'
""")

# ==================================================================================

