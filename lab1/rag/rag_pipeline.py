class RAGPipeline:
    def __init__(self, retriever, embedder, llm, top_k=5):
        self.retriever = retriever
        self.embedder = embedder
        self.llm = llm
        self.top_k = top_k

    def ask(self, question: str):
        query_vector = self.embedder.embed_query(question)
        results = self.retriever.search(query_vector, self.top_k)

        context_parts = []
        for i, result in enumerate(results, start=1):
            metadata = result["metadata"]
            context_parts.append(
                f"[Source {i} | page {metadata.get('page')}]\n"
                f"{result['text']}"
            )

        context = "\n\n".join(context_parts)

        answer = self.llm.answer(question, context)

        return {
            "answer": answer,
            "sources": [
                {
                    "page": result["metadata"].get("page"),
                    "source": result["metadata"].get("source"),
                    "distance": result["distance"],
                }
                for result in results
            ],
        }
