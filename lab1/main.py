import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from rag.config import Settings
from rag.model_selector import ModelSelector
from rag.embeddings import GeminiEmbedder
from rag.vector_store import ChromaVectorStore
from rag.pdf_loader import load_pdf
from rag.chunker import chunk_documents
from rag.llm import GeminiLLM
from rag.rag_pipeline import RAGPipeline


def choose_pdf() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]

    data_dir = Path("data")
    pdfs = sorted(data_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(
            "No PDF found. Put a PDF inside ./data or pass its path: "
            "python main.py data/file.pdf"
        )

    if len(pdfs) == 1:
        return str(pdfs[0])

    print("Available PDFs:")
    for i, pdf in enumerate(pdfs, 1):
        print(f"{i}. {pdf}")
    choice = int(input("Select PDF number: ")) - 1
    return str(pdfs[choice])


def main():
    load_dotenv()
    settings = Settings.from_env()

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Create a .env file.")

    print("Checking Gemini models...")
    selector = ModelSelector(settings.gemini_api_key)
    selected = selector.select(
        llm_model=settings.llm_model,
        embedding_model=settings.embedding_model,
    )

    print(f"LLM model: {selected.llm_model}")
    print(f"Embedding model: {selected.embedding_model}")

    pdf_path = choose_pdf()
    print(f"Loading: {pdf_path}")

    documents = load_pdf(pdf_path)
    chunks = chunk_documents(
        documents,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    print(f"Created {len(chunks)} chunks.")

    embedder = GeminiEmbedder(
        api_key=settings.gemini_api_key,
        model=selected.embedding_model,
    )

    store = ChromaVectorStore(
        persist_directory=settings.chroma_dir,
        collection_name="pdf_rag",
    )

    print("Creating embeddings and indexing...")
    store.add_documents(chunks, embedder)
    print("Indexing complete.")

    llm = GeminiLLM(
        api_key=settings.gemini_api_key,
        model=selected.llm_model,
    )

    rag = RAGPipeline(
        retriever=store,
        embedder=embedder,
        llm=llm,
        top_k=settings.top_k,
    )

    print("\nRAG is ready. Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        result = rag.ask(question)

        print("\nAssistant:")
        print(result["answer"])

        print("\nSources:")
        for source in result["sources"]:
            print(
                f"- page {source['page']} | distance={source['distance']:.4f}"
            )
        print()


if __name__ == "__main__":
    main()
