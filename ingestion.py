import re
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def extract_pages(file_bytes: bytes, filename: str) -> list[dict]:
    """Extract text from a PDF or Word document."""

    extension = Path(filename).suffix.lower()
    pages = []

    if extension == ".pdf":
        reader = PdfReader(BytesIO(file_bytes))

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                pages.append({
                    "text": text,
                    "page": page_number,
                })

    elif extension == ".docx":
        document = Document(BytesIO(file_bytes))

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

        if text.strip():
            pages.append({
                "text": text,
                "page": None,
            })

    else:
        raise ValueError(
            "Unsupported file type. Upload a PDF or DOCX file."
        )

    return pages


def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 40,
) -> list[str]:
    """Split text into overlapping word-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    words = re.findall(r"\S+", text)
    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if start + chunk_size >= len(words):
            break

    return chunks


def process_document(
    file_bytes: bytes,
    filename: str,
) -> list[dict]:
    """Extract document text and create source-aware chunks."""

    extracted_pages = extract_pages(file_bytes, filename)
    result = []
    chunk_index = 0

    for page_data in extracted_pages:
        chunks = chunk_text(page_data["text"])

        for chunk in chunks:
            result.append({
                "chunk_id": chunk_index,
                "source": filename,
                "page": page_data["page"],
                "text": chunk,
            })
            chunk_index += 1

    return result
