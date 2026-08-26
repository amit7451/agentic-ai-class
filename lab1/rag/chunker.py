def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size.")

    words = text.split()
    chunks = []
    start = 0
    step = chunk_size - overlap

    # Approximate character-based chunking using word boundaries.
    current = []
    current_len = 0
    i = 0

    while i < len(words):
        word = words[i]
        added = len(word) + (1 if current else 0)

        if current and current_len + added > chunk_size:
            chunks.append(" ".join(current))

            overlap_words = []
            overlap_len = 0
            for old_word in reversed(current):
                extra = len(old_word) + (1 if overlap_words else 0)
                if overlap_len + extra > overlap:
                    break
                overlap_words.insert(0, old_word)
                overlap_len += extra

            current = overlap_words
            current_len = len(" ".join(current))
            continue

        current.append(word)
        current_len += added
        i += 1

    if current:
        chunks.append(" ".join(current))

    return chunks


def chunk_documents(documents, chunk_size=1000, overlap=200):
    output = []

    for document in documents:
        parts = chunk_text(
            document["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for index, part in enumerate(parts):
            metadata = dict(document["metadata"])
            metadata["chunk"] = index
            output.append(
                {
                    "text": part,
                    "metadata": metadata,
                }
            )

    return output
