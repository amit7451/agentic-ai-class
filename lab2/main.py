import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI


class OpenRouterEmbeddings(Embeddings):
    def __init__(self, client: OpenAI, model: str = "liquid/lfm-2.5-embedding-350m:free"):
        self.client = client
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding


def choose_pdf() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]

    current_dir = Path(".")
    pdfs = sorted(current_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError("No PDF file found in current directory.")

    if len(pdfs) == 1:
        return str(pdfs[0])

    print("Available PDFs:")
    for i, pdf in enumerate(pdfs, 1):
        print(f"{i}. {pdf.name}")
    choice = int(input("Select PDF number: ")) - 1
    return str(pdfs[choice])


def main():
    load_dotenv()
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Check your .env file.")

    llm_model = os.getenv("LLM_MODEL", "nvidia/nemotron-3.5-lightning:free")
    embedding_model = os.getenv("EMBEDDING_MODEL", "liquid/lfm-2.5-embedding-350m:free")

    print("Initializing OpenRouter...")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key
    )

    pdf_path = choose_pdf()
    print(f"Loading: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print(f"Generating embeddings using '{embedding_model}' and building FAISS index...")
    embeddings = OpenRouterEmbeddings(client=client, model=embedding_model)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("faiss_index")
    print("FAISS vector store indexed successfully.")

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
        model=llm_model
    )

    print(f"\nRAG is ready with model '{llm_model}'. Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except EOFError:
            break

        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        retrieved_docs = retriever.invoke(question)
        context = "\n\n".join(
            f"[Source page {doc.metadata.get('page', 'unknown')}]\n{doc.page_content}"
            for doc in retrieved_docs
        )

        prompt = f"""Answer the question using only the provided context.

Context:
{context}

Question:
{question}

If the answer is not present in the context, say:
"I could not find this information in the provided documents."
"""

        response = llm.invoke(prompt)

        print("\nAssistant:")
        print(response.content)

        print("\nSources:")
        for doc in retrieved_docs:
            print(f"- page {doc.metadata.get('page', 'unknown')} | {doc.metadata.get('source', '')}")
        print()


if __name__ == "__main__":
    main()
