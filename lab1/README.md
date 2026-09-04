# Simple RAG — PDF + Gemini + ChromaDB

End-to-end local RAG project:
1. Accept a PDF.
2. Extract text.
3. Chunk text with overlap.
4. Generate Gemini embeddings.
5. Store vectors in ChromaDB.
6. Detect available Gemini models before selecting the requested/default model.
7. Retrieve relevant chunks for a question.
8. Send retrieved context + question to Gemini LLM.
9. Return an answer with source chunks.

## Requirements

- Python 3.10+
- Google Gemini API key

## Setup

Activate the shared virtual environment created at the repository root (`agentic-ai-class/.venv`):

```bash
# From lab1 directory:
# Windows (CMD): ..\.venv\Scripts\activate
# Windows (PowerShell): ..\.venv\Scripts\Activate.ps1
# Linux/macOS: source ../.venv/bin/activate
```


Create `.env`:

```env
GEMINI_API_KEY=your_key_here
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001
CHROMA_DIR=./chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
```

## Run

Put a PDF in `data/`, then:

```bash
python main.py
```

The CLI will index the PDF and let you ask questions.

You can also specify a PDF directly:

```bash
python main.py data/my_document.pdf
```

## Architecture

PDF -> text extraction -> chunking -> Gemini embeddings -> ChromaDB

Question -> Gemini embedding -> ChromaDB similarity search -> retrieved context -> Gemini LLM -> answer

The model selector first calls the Gemini API to list available models and checks whether the configured LLM and embedding models are available. It then uses the selected models.

## Notes

This intentionally keeps the implementation simple and readable. It uses the official `google-genai` SDK, PyMuPDF for PDFs, and ChromaDB for local vector storage.
