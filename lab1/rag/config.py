import os
from dataclasses import dataclass


@dataclass
class Settings:
    gemini_api_key: str
    llm_model: str
    embedding_model: str
    chroma_dir: str
    chunk_size: int
    chunk_overlap: int
    top_k: int

    @classmethod
    def from_env(cls):
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            embedding_model=os.getenv(
                "EMBEDDING_MODEL", "gemini-embedding-001"
            ),
            chroma_dir=os.getenv("CHROMA_DIR", "./chroma_db"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            top_k=int(os.getenv("TOP_K", "5")),
        )
