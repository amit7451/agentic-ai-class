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
└── lab2/                      # Lab 2: PDF + LangChain + FAISS + OpenRouter RAG
    ├── lab2.ipynb             # Interactive exploration notebook
    ├── agent.ipynb            # Agentic RAG notebook
    ├── main.py                # Interactive CLI interface
    ├── requirements.txt       # Lab 2 dependencies
    └── README.md              # Lab 2 documentation & setup
```

## Quick Start

### 1. Lab 1 (Gemini + ChromaDB)
```bash
cd lab1
python -m venv .venv
# Activate venv:
# Windows (CMD): .venv\Scripts\activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Add your GEMINI_API_KEY
python main.py
```

### 2. Lab 2 (LangChain + FAISS + OpenRouter)
```bash
cd lab2
python -m venv .venv
# Activate venv:
# Windows (CMD): .venv\Scripts\activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Add your OPENROUTER_API_KEY
python main.py
```
