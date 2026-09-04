# Lab 2: RAG with LangChain, FAISS & OpenRouter

End-to-end local Retrieval-Augmented Generation (RAG) using LangChain, FAISS vector store, and OpenRouter.

## Requirements

- Python 3.10+
- OpenRouter API Key (get free from [openrouter.ai](https://openrouter.ai/))

## Setup

Activate the shared virtual environment created at the repository root (`agentic-ai-class/.venv`):

```bash
# From lab2 directory:
# Windows (CMD): ..\.venv\Scripts\activate
# Windows (PowerShell): ..\.venv\Scripts\Activate.ps1
# Linux/macOS: source ../.venv/bin/activate
```


## Configuration

Copy `.env.example` to `.env` and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_key_here
LLM_MODEL=nvidia/nemotron-3.5-lightning:free
EMBEDDING_MODEL=liquid/lfm-2.5-embedding-350m:free
```

## Running

### CLI Mode:
```bash
python main.py
```

### Notebooks:
You can also explore and run the interactive Jupyter Notebooks:
- `lab2.ipynb`
- `agent.ipynb`
