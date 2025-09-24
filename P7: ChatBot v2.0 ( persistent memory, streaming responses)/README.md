# ChatBot v2.0 - Advanced AI Assistant 🤖

An advanced conversational AI chatbot built with LangGraph featuring persistent memory, streaming responses, and thread-based conversation management using InMemorySaver checkpointing.

## 🎯 Overview

This project demonstrates sophisticated LangGraph patterns with **persistent memory and streaming** that:

1. **Maintains conversation context** across sessions using InMemorySaver checkpointing
2. **Streams responses in real-time** for enhanced user experience
3. **Manages multiple conversation threads** with unique thread identifiers
4. **Provides modular architecture** with separated backend and frontend components
5. **Offers seamless chat experience** with professional UI and memory persistence

## ✨ Features

- **Persistent Memory**: True conversation continuity using LangGraph's InMemorySaver checkpointing
- **Streaming Responses**: Real-time message generation with `st.write_stream()` integration
- **Thread Management**: Multi-conversation handling with configurable thread IDs
- **Modular Architecture**: Clean separation of backend logic and frontend interface
- **Interactive UI**: Modern Streamlit interface with chat message history
- **Session Continuity**: Conversations persist beyond browser sessions
- **Memory Efficiency**: Optimized state management for long conversations
- **Professional Design**: Clean chat interface with proper message formatting

## 🔄 Upgrades from v1.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Memory | Session-based | InMemorySaver checkpointing |
| Responses | Standard | Streaming |
| Architecture | Monolithic | Modular (backend/frontend) |
| Persistence | Browser session only | True conversation continuity |
| Threading | Single session | Multi-thread support |


## 🗺️ LangGraph Workflow

```mermaid
graph LR
    A[START] --> B[Chat Node]
    B --> C[InMemorySaver Checkpoint]
    C --> D[Streaming Response]
    D --> E[END]
```

### Persistent Memory Architecture:

**Initialization Phase**: 
- Set up InMemorySaver checkpointer
- Configure thread-based conversation management
- Initialize streaming-enabled LLM endpoint

**Processing Phase**:
- Receive user input through Streamlit interface
- Convert to LangChain message format
- Process through LangGraph with checkpoint configuration
- Stream response in real-time to user

**Memory Persistence**: 
- Automatic conversation saving via InMemorySaver
- Thread-based conversation retrieval
- State persistence across sessions

### Workflow Details:

1. **Chat Node**:
   - Processes user messages through HuggingFace LLM
   - Maintains conversation context using checkpointing
   - Returns streaming responses for real-time display

2. **InMemorySaver Integration**:
   - Automatically saves conversation state
   - Enables conversation retrieval by thread ID
   - Provides true persistent memory across sessions

3. **Streaming Implementation**:
   - Real-time response generation using `streaming=True`
   - Streamlit integration with `st.write_stream()`
   - Progressive message display for better UX

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Hugging Face API access
- Internet connection for model access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/swarupd07/LangGraphProjects.git
   cd "LangGraphProjects/P7: ChatBot v2.0"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "HUGGINGFACEHUB_API_TOKEN=your_token_here" > .env
   ```

### Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run chatbot_v2_frontend.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Start chatting** with your AI assistant

4. **Enjoy persistent conversations** - your chat history is automatically saved!

## 📊 Usage Example

### Conversation Flow:

**User:** "Hello! Can you help me with Python programming?"

**Assistant:** "Hello! I'd be happy to help you with Python programming. Whether you're just starting out or working on specific projects, I can assist with concepts, code examples, debugging, best practices, and more. What particular aspect of Python would you like to explore today?"

**User:** "I want to learn about list comprehensions"

**Assistant:** "Great choice! List comprehensions are one of Python's most elegant features. They provide a concise way to create lists based on existing lists or other iterables.

**Basic Syntax:**
```python
[expression for item in iterable]
```

**Example:**
```python
# Traditional approach
squares = []
for x in range(10):
    squares.append(x**2)

# List comprehension approach
squares = [x**2 for x in range(10)]
```

Would you like me to show you more advanced examples with conditions?"

**User:** "Yes, show me conditional list comprehensions"

**Assistant:** "Perfect! Here are conditional list comprehensions:

**With if condition (filtering):**
```python
# Only even squares
even_squares = [x**2 for x in range(10) if x % 2 == 0]
# Result: [0, 4, 16, 36, 64]
```

**With if-else (conditional expression):**
```python
# Mark odd/even numbers
labels = ['even' if x % 2 == 0 else 'odd' for x in range(5)]
# Result: ['even', 'odd', 'even', 'odd', 'even']
```

**Complex example:**
```python
# Process only positive numbers, square them if even, cube if odd
processed = [x**2 if x % 2 == 0 else x**3 for x in [-2, -1, 0, 1, 2, 3] if x >= 0]
# Result: [0, 1, 4, 27]
```

The conversation continues with full context retention..."

## 🔧 Technical Architecture

### Backend Implementation (`chatbot_v2_backend.py`)

```python
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages': [response]}

# Graph with checkpointing
checkpointer = InMemorySaver()
chatbot = graph.compile(checkpointer=checkpointer)
```

### Frontend Implementation (`chatbot_v2_frontend.py`)

```python
import streamlit as st
from langchain_core.messages import HumanMessage
from chatbot_v2_backend import chatbot

# Configuration for persistent memory
config = {'configurable': {'thread_id': 'thread-1'}}

# Streaming response
response = st.write_stream(
    message.content for message, meta in chatbot.stream(
        state, config=config, stream_mode='messages'
    )
)
```

### State Management with Persistence

```python
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    # Messages automatically accumulated via add_messages annotation
    # InMemorySaver handles persistence across sessions
```

### Streaming Configuration

```python
llm = HuggingFaceEndpoint(
    endpoint_url="openai/gpt-oss-20b",
    task="text-generation",
    streaming=True  # Enable streaming responses
)
```

## 📁 Project Structure

```
chatbot-v2/
├── chatbot_v2_backend.py         # Core LangGraph implementation
├── chatbot_v2_frontend.py        # Streamlit UI interface
├── requirements.txt              # Project dependencies
├── README.md                     # This file
└── .env.example                  # Environment variables template
 
```


## 🔄 Future Enhancements

- [ ] **Persistent Storage**: Database-backed conversation persistence
- [ ] **Multi-User Support**: User authentication and isolated conversations
- [ ] **Conversation Management**: Save, load, and organize conversations
- [ ] **File Upload**: Document analysis and discussion
- [ ] **Advanced Memory**: Semantic search through conversation history


## 🎓 Learning Outcomes

This project demonstrates:

### Advanced LangGraph Patterns
- **Checkpointing Systems**: InMemorySaver for persistent state
- **Streaming Integration**: Real-time response generation
- **Thread Management**: Conversation organization and retrieval

### State Management Techniques
- **Persistent Memory**: Beyond session-based storage
- **Message Accumulation**: Using annotated types for state building
- **Configuration Management**: Thread-based conversation handling

### Modern UI/UX Principles
- **Streaming Interfaces**: Real-time response display
- **Conversation History**: Proper chat interface design
- **Progressive Enhancement**: Smooth user experience patterns

### Production-Ready Features
- **Modular Design**: Scalable architecture patterns
- **Error Handling**: Robust failure management
- **Performance Optimization**: Efficient memory and streaming usage


## 📝 License

This project is part of the LangGraph Mini Projects collection and follows the same MIT License.

---

⭐ **Star the repository** if this chatbot enhanced your AI conversation experience!

🤖 **Built something amazing with it?** Share your implementations in discussions!

💡 **Want new features?** [Open an issue](https://github.com/swarupd07/LangGraphProjects/issues) with your suggestions!

🤝 **Contribute improvements** for better conversation management and user experience!
