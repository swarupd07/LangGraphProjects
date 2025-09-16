# P2. You Tube Video Summarizer


# Importing necessary libraries
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Dict, List
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import streamlit as st
import os




# ===================================================================================

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

# ===================================================================================

# Defining State 

class VideoInfo(TypedDict):
    input_transcript: str
    video_url: str
    want_questions: bool
    want_answers: bool
    video_code: str
    transcript: str
    summary: str
    topic: List[str]
    questions: str
    qa : str
    Error: str
    model: object  # Added to store the model instance

# ===================================================================================

# Function to get code from YouTube video URL
def get_video_code(Info: VideoInfo) -> VideoInfo:
    if Info["input_transcript"]:
        return Info

    if "v=" in Info['video_url']:
        video_code = Info['video_url'].split("v=")[1].split("&")[0]
    
    elif "youtu.be/" in Info['video_url']:
        video_code = Info['video_url'].split("youtu.be/")[1].split("?")[0]
    else:
        Info['Error'] = "Invalid YouTube URL"
        return Info
    Info['video_code'] = video_code

    return Info

# ===================================================================================

# Function to get transcript from YouTube video code

def get_transcript(Info: VideoInfo) -> VideoInfo:
    if Info["input_transcript"]:
        Info['transcript'] = Info["input_transcript"]
        return Info
    try:
        # Validate video_code exists and is not empty
        if Info['video_code'] == '':
            Info['Error'] = "Invalid or missing video ID" 
            return Info
            
        video_id = Info['video_code'].strip()
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item['text'] for item in transcript_list])
        Info['transcript'] = transcript
        
    except Exception as e:
        Info['Error'] = f"Could not retrieve transcript: {str(e)}"
        
    return Info


# ===================================================================================

# Function to summarize the transcript

def summarize_transcript(Info: VideoInfo) -> VideoInfo:
    if Info["Error"]:
        return Info
    prompt = f"Topic wise summarize the following YouTube video transcript :\n\n{Info['transcript']}\n\n Topic Wise Summary:"
    response = Info['model'].invoke(prompt)
    Info['summary'] = response.content
    return Info

# ===================================================================================

# Function for extracting topics from the summary
def extract_topics(Info: VideoInfo) -> VideoInfo:
    if Info["Error"]:
        return Info
    prompt = f"Extract key topics from the following summary:\n\n{Info['summary']}\n\n Only give Key Topics where each topic is in next line:"
    response = Info['model'].invoke(prompt).content
    topics = response.split('\n')
    Info['topic'] = [topic.strip() for topic in topics if topic.strip()]
    
    return Info

# ===================================================================================

# Function for generating questions based on the topics
def generate_questions(Info: VideoInfo) -> VideoInfo:
    if Info["Error"] or not Info['want_questions']:
        return Info
    prompt = f"Generate questions based on the following topics:\n\n{', '.join(Info['topic'])}\n\n Topic wise Questions:"
    response = Info['model'].invoke(prompt)
    Info['questions'] = response.content
    return Info

# ===================================================================================

# Function to generate answers for the questions generated
def generate_answers(Info: VideoInfo) -> VideoInfo:
    if Info["Error"] or not Info['want_answers'] or not Info['want_questions']:
        return Info
    prompt = f"Based on the following transcript, provide answers to the questions:\n\nTranscript: {Info['transcript']}\n\nQuestions: {Info['questions']}\n\n Provide detailed answers for each question. Example format:\n\n Question: \n Answer: \n\n Question: \n Answer: \n\n"
    response = Info['model'].invoke(prompt)
    Info['qa'] = response.content
    return Info

# ===================================================================================

# Defining the Graph
graph = StateGraph(VideoInfo)

# Adding node to the graph
graph.add_node("get_video_code", get_video_code)
graph.add_node("get_transcript", get_transcript)
graph.add_node("summarize_transcript", summarize_transcript)
graph.add_node("extract_topics", extract_topics)
graph.add_node("generate_questions", generate_questions)    
graph.add_node("generate_answers", generate_answers)

# Adding edges to the graph
graph.add_edge(START, "get_video_code")
graph.add_edge("get_video_code", "get_transcript")
graph.add_edge("get_transcript", "summarize_transcript")    
graph.add_edge("summarize_transcript", "extract_topics")
graph.add_edge("extract_topics", "generate_questions")
graph.add_edge("generate_questions", "generate_answers")
graph.add_edge("generate_answers", END)

# Compiling the graph
YTgraph = graph.compile()

# ===================================================================================

# Creating a streamlit web app

st.title("YouTube Video Summarizer and Q&A Generator")

# API Key input
api_key = st.text_input("Enter your Hugging Face API Key:", type="password", help="Get your API key from https://huggingface.co/settings/tokens")

input_transcript = st.text_area("Or Enter Transcript directly (Optional):", height=150, value="")
video_url = st.text_input("Enter YouTube Video URL:", value="")
want_questions = st.checkbox("Generate Questions", value=False)
want_answers = st.checkbox("Generate Answers", value=False)

if st.button("Result"):
    if not api_key:
        st.error("Please enter your Hugging Face API key.")
    elif not video_url and not input_transcript:
        st.error("Please enter a valid YouTube video URL or provide a transcript.")
    else:
        try:
            # Initialize the model with the provided API key
            model = initialize_llm(api_key)
            
            initial_info: VideoInfo = {
                "input_transcript": input_transcript,
                "video_url": video_url,
                "want_questions": want_questions,
                "want_answers": want_answers,
                "video_code": "",
                "transcript": "",
                "summary": "",
                "topic": [],
                "questions": "",
                "qa" : "",
                "Error": "",
                "model": model
            }
            
            with st.spinner("Processing..."):
                result = YTgraph.invoke(initial_info)
            
            if result["Error"]:
                st.error(f"Error: {result['Error']}")
            else:
                st.subheader("Video Summary")
                st.write(result["summary"])
                
                if want_answers:
                    st.subheader("Generated Q&A")
                    st.write(result["qa"])

                elif want_questions:
                    st.subheader("Generated Questions")
                    st.write(result["questions"])

                st.subheader("Thanks for using the app!")
                
        except Exception as e:

            st.error(f"Error initializing the model: {str(e)}. Please check your API key.")
