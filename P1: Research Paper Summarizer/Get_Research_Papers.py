from langgraph.graph import StateGraph, START, END
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from typing import TypedDict, Dict, List
from dotenv import load_dotenv
import requests
load_dotenv()

llm = HuggingFaceEndpoint(
    endpoint_url="openai/gpt-oss-20b",
    task="text-generation",
    )

Model = ChatHuggingFace(llm=llm)

# Defining State 
class PaperInfo(TypedDict):
    prompt: str
    topic: List[str]
    top_search: int
    title: List[str]
    abstract: List[str]
    url: List[str]
    citationCount: List[int]
    result: str
    
# Defining State 
# Function to get papers from Semantic Scholar API

def get_papers(Info :PaperInfo) -> PaperInfo:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    for i in range(Info['top_search']):
        params = {
            "query": Info['topic'][i],
            "fields": "title,url,abstract,citationCount",
            "limit": 1,
            "offset": 0
        }
        response = requests.get(url, params=params) 
        data = response.json()

        for paper in data.get("data", []):
         Info["abstract"].append( paper.get("abstract"))
         Info["title"].append(paper.get("title"))
         Info["url"].append(paper.get("url"))    
         Info["citationCount"].append(paper.get("citationCount"))

    return Info

# Finail answer Drafting function
def draft_answer(Info: PaperInfo) -> PaperInfo:
    prompt = f"Using the following papers, draft the summerization of each paper '{Info['topic']}'.\n\n"
    for i in range(len(Info['title'])):
        prompt += f"Title: {Info['title'][i]}\nAbstract: {Info['abstract'][i]}\nURL: {Info['url'][i]}\nCitations: {Info['citationCount'][i]}\n\n"
    prompt += "Summarize the key points from these papers in a concise manner.\n\n Title: \n Citations: \n Abstract Summery: \n URL: \n "
    
    response = Model.invoke(prompt)
    Info['result'] = response.content
    return Info

# Generating Paper Titles
def generate_titles(Info: PaperInfo) -> PaperInfo:
    prompt = Info['prompt']
    response = Model.invoke(prompt)
    titles = response.content.split('\n')
    Info['topic'] = [title.strip() for title in titles if title.strip()]
    return Info



# Graph Definition
graph = StateGraph(PaperInfo)

# adding notes
graph.add_node("generate_titles", generate_titles)
graph.add_node("get_papers", get_papers)
graph.add_node("draft_answer", draft_answer)

# adding edges
graph.add_edge(START, "generate_titles")
graph.add_edge("generate_titles", "get_papers")
graph.add_edge("get_papers", "draft_answer")
graph.add_edge("draft_answer", END)

# Completing the graph
research_paper_graph = graph.compile()

# Creating Stremlit App
import streamlit as st

st.title("Get Research Papers and Summarize")
input = st.text_input("Enter the research topic:")
top_search = st.number_input("Number of top papers to fetch:", min_value=1, max_value=10, value=3)
prompt = f"User gave us {input} as a topic. We need to find relevant research papers for this topics. Understand the topic and  give me top {top_search} research paper's title. Make sure the titles are relevant to the topic. all topic should give a sequencial learning to unser. for example , if topic is : 'Linear Regression' and top_search is 3 then 1st paper sholud be the 1st foundational paper 2nd should be with further seqential papers which improved it further and same with 3rd. Give me only the titles in the response and each title should be in new line."
if st.button("Get Papers"):
    if prompt:
        initial_info: PaperInfo = {
            "prompt": prompt,
            "topic": [],
            "top_search": top_search,
            "title": [],
            "abstract": [],
            "url": [],
            "citationCount": [],
            "result": ""
        }
        result = research_paper_graph.invoke(initial_info)
        st.subheader("Summarized Result:")
        st.write(result['result'])
    else:
        st.error("Please enter a research topic.")