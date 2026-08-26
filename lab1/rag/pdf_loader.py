from pathlib import Path
import pymupdf


def load_pdf(pdf_path: str):
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF does not exist: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    documents = []

    with pymupdf.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if text:
                documents.append(
                    {
                        "text": text,
                        "metadata": {
                            "source": str(path),
                            "page": page_number,
                        },
                    }
                )

    if not documents:
        raise ValueError("No extractable text found in the PDF.")

    return documents
