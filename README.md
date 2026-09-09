# Agentic AI Class

Hands-on practical implementations for Agentic AI and Retrieval-Augmented Generation (RAG).

## Repository Structure

```
agentic-ai-class/
├── lab1/                      # Lab 1: PDF + Gemini SDK + ChromaDB RAG
│   ├── rag/                   # RAG components (chunker, embeddings, vector store, llm, selector)
│   ├── data/                  # Source documents (PDFs)
│   ├── main.py                # Interactive CLI interface
│   ├── requirements.txt       # Lab 1 dependencies
│   └── README.md              # Lab 1 documentation & setup
│
├── lab2/                      # Lab 2: PDF + LangChain + FAISS + OpenRouter RAG
│   ├── lab2.ipynb             # Interactive exploration notebook
│   ├── agent.ipynb            # Agentic RAG notebook
│   ├── main.py                # Interactive CLI interface
│   ├── requirements.txt       # Lab 2 dependencies
│   └── README.md              # Lab 2 documentation & setup
│
├── lab3/                      # Lab 3: Enterprise IT Helpdesk AI Assistant
│   ├── lab3.ipynb             # Interactive exploration notebook
│   ├── main.py                # Interactive CLI interface
│   ├── requirements.txt       # Lab 3 dependencies
│   └── README.md              # Lab 3 documentation & setup
│
├── lab4/                      # Lab 4: Autonomous Medical Voice AI Assistant
│   ├── lab4.ipynb             # Interactive exploration notebook
│   ├── main.py                # Interactive CLI & voice assistant
│   ├── streamlit_app/         # Web UI interface
│   ├── requirements.txt       # Lab 4 dependencies
│   └── README.md              # Lab 4 documentation & setup
│
└── lab5/                      # Lab 5: Model Context Protocol (MCP) Assistant
    ├── server.py              # College MCP Server (Streamable HTTP)
    ├── client.py              # MCP Client module & tool discovery
    ├── main.py                # Interactive CLI interface
    ├── lab5.ipynb             # Interactive exploration notebook
    ├── requirements.txt       # Lab 5 dependencies
    └── README.md              # Lab 5 documentation & setup
```

## Quick Start

### 1. Global Virtual Environment Setup

Set up the virtual environment once at the root of `agentic-ai-class`:

```bash
# Create shared virtual environment
python -m venv .venv

# Activate virtual environment:
# Windows (CMD): .venv\Scripts\activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

# Install dependencies for all labs
pip install -r requirements.txt
```

### 2. Running Any Lab

With the shared root `.venv` activated, navigate to any lab folder and configure `.env`:

- **Lab 1 (PDF + Gemini SDK + ChromaDB RAG):**
  ```bash
  cd lab1
  cp .env.example .env    # Add GEMINI_API_KEY
  python main.py
  ```

- **Lab 2 (PDF + LangChain + FAISS + OpenRouter):**
  ```bash
  cd lab2
  cp .env.example .env    # Add OPENROUTER_API_KEY
  python main.py
  ```

- **Lab 3 (Enterprise IT Helpdesk AI Assistant):**
  ```bash
  cd lab3
  cp .env.example .env    # Add OPENROUTER_API_KEY
  python main.py
  ```

- **Lab 4 (Autonomous Medical Voice AI Assistant):**
  ```bash
  cd lab4
  cp .env.example .env    # Add OPENROUTER_API_KEY
  python main.py
  ```

- **Lab 5 (Model Context Protocol Assistant):**
  ```bash
  cd lab5
  cp .env.example .env    # Add OPENROUTER_API_KEY
  # Terminal 1: Start MCP Server
  python server.py
  # Terminal 2: Run MCP Assistant
  python main.py
  ```