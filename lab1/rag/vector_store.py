import uuid
import chromadb


class ChromaVectorStore:
    def __init__(self, persist_directory: str, collection_name: str):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, documents, embedder):
        texts = [doc["text"] for doc in documents]
        embeddings = embedder.embed_documents(texts)

        ids = [str(uuid.uuid4()) for _ in documents]
        metadatas = [doc["metadata"] for doc in documents]

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(self, query_vector, top_k=5):
        result = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        return [
            {
                "text": text,
                "metadata": metadata,
                "distance": distance,
            }
            for text, metadata, distance
            in zip(documents, metadatas, distances)
        ]
