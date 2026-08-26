from dataclasses import dataclass
from google import genai


@dataclass
class SelectedModels:
    llm_model: str
    embedding_model: str


class ModelSelector:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def list_model_names(self):
        names = []
        for model in self.client.models.list():
            name = getattr(model, "name", None)
            if name:
                names.append(name.replace("models/", ""))
        return names

    @staticmethod
    def _matches(candidate: str, available: list[str]) -> str | None:
        candidate_clean = candidate.replace("models/", "")
        if candidate_clean in available:
            return candidate_clean

        # Some API responses expose aliases/versioned names.
        matches = [
            name for name in available
            if name == candidate_clean
            or name.startswith(candidate_clean + "-")
            or candidate_clean in name
        ]
        return matches[0] if matches else None

    def select(self, llm_model: str, embedding_model: str):
        available = self.list_model_names()

        if not available:
            raise RuntimeError("Gemini returned no available models.")

        selected_llm = self._matches(llm_model, available)
        if not selected_llm:
            # Prefer a Flash model if the requested model is unavailable.
            candidates = [
                x for x in available
                if "flash" in x.lower()
                and "embedding" not in x.lower()
            ]
            if not candidates:
                raise RuntimeError(
                    f"LLM model '{llm_model}' is unavailable. "
                    f"Available models: {available}"
                )
            selected_llm = candidates[0]

        selected_embedding = self._matches(embedding_model, available)
        if not selected_embedding:
            candidates = [
                x for x in available
                if "embedding" in x.lower()
            ]
            if not candidates:
                raise RuntimeError(
                    f"Embedding model '{embedding_model}' is unavailable. "
                    f"Available models: {available}"
                )
            selected_embedding = candidates[0]

        return SelectedModels(
            llm_model=selected_llm,
            embedding_model=selected_embedding,
        )
