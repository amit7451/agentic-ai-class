from google import genai


class GeminiLLM:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def answer(self, question: str, context: str) -> str:
        prompt = f"""You are a helpful RAG assistant.

Answer the user's question using ONLY the supplied context.
If the context does not contain enough information, say that the
answer is not available in the provided document.

Do not invent facts.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text or "No answer was generated."
