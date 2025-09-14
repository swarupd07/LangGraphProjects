# LangGraph Mini Projects 🕸️
A collection of small-scale LangGraph projects demonstrating various patterns, workflows, and use cases for building stateful, multi-actor applications with LangChain.

## 📂 Projects Overview

| Project Name | Description | Key Concepts | Status |
|--------------|-------------|--------------|--------|
| `P1: Research Paper Summarizer` | Automated research paper discovery and summarization using Semantic Scholar API | API integration, sequential workflows | ✅ Complete |
| `P2: YouTube Video Summarizer` | Extract and summarize YouTube video content with optional Q&A generation | External APIs, conditional processing | ✅ Complete |
| `P3: Project Idea Generator` | Generate personalized project ideas or provide implementation guides for existing ideas | Parallel processing, structured output | ✅ Complete |
| `P4: Professional Writing Assistant` | Generate professional emails, LinkedIn posts, and LinkedIn messages with smart platform detection | Conditional routing, structured parsing | ✅ Complete |
| `P5: User Persona Generator` | Generate comprehensive user personas with 13-section framework using iterative processing | Iterative loops, state accumulation | ✅ Complete |

## 🔄 Project Workflows

### P1: Research Paper Summarizer
```mermaid
graph LR
    A[START] --> B[Generate Titles]
    B --> C[Get Papers]
    C --> D[Draft Answer]
    D --> E[END]
```

### P2: YouTube Video Summarizer
```mermaid
graph LR
    A[START] --> B[Get Video Code]
    B --> C[Get Transcript]
    C --> D[Summarize Transcript]
    D --> E[Extract Topics]
    E --> F[Generate Questions]
    F --> G[Generate Answers]
    G --> H[END]
```

### P3: Project Idea Generator
```mermaid
graph TD
    A[START] --> B[Generate Project Ideas]
    A --> C[Suggest Other Skills]
    A --> D[Provide Steps to Implement]
    A --> E[Provide Skills Required]
    B --> F[Final Output]
    C --> F
    D --> F
    E --> F
    F --> G[END]
```

### P4: Professional Writing Assistant
```mermaid
graph TD
    A[START] --> B[Get Platform]
    B --> C{Platform?}
    C -->|Mail| D[Generate Mail]
    C -->|LinkedIn| E[Get Task]
    E --> F{LinkedIn Task?}
    F -->|Post| G[Generate Post]
    F -->|Message| H[Generate Message]
    D --> I[END]
    G --> I
    H --> I
```

### P5: User Persona Generator
```mermaid
graph TD
    A[START] --> B[Get Profiles]
    B --> C[Get Persona]
    C --> D{All Users Done?}
    D -->|No| C
    D -->|Yes| E[END]
```

## 🛠️ Technologies Used

- **LangGraph** - Stateful workflow orchestration
- **LangChain** - LLM application framework  
- **Python 3.8+** - Programming language
- **HuggingFace API** - Primary LLM provider
- **Additional tools**: Varies by project (web scraping, file processing, etc.)

## 📝 License

This projects are licensed under the MIT License

## 🌟 Acknowledgments

- Thanks to the LangChain team for creating LangGraph
- Inspired by the open-source AI community

## 📞 Contact

- **GitHub**: https://github.com/swarupd07
- **LinkedIn**: https://www.linkedin.com/in/swarup-dhanavade-2065a4280/

---

## ⭐ Star this repository if you find it helpful!
