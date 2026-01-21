from __future__ import annotations

import os
from pathlib import Path
from typing import List

import chromadb
from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

load_dotenv()

# ---------- Non-sensitive config ----------
DATA_DIR = Path("data/raw")

CHROMA_DIR = Path(os.environ.get("CHROMA_DIR", "storage/chroma"))
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "docs")
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Chunking 
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Local embeddings 
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBED_MODEL = SentenceTransformer(EMBED_MODEL_NAME)

# Batching (performance only)
EMB_BATCH = 64
# ----------------------------------------


def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def chunk_text(text: str) -> List[str]:
    text = " ".join(text.split())
    chunks: List[str] = []

    step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
    start = 0

    while start < len(text):
        end = min(len(text), start + CHUNK_SIZE)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start += step

    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    # normalize_embeddings=True improves cosine similarity retrieval
    return EMBED_MODEL.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()


def main():
    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit("Put PDFs into data/raw/ first.")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION)

    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict] = []

    for pdf in pdfs:
        text = read_pdf(pdf)
        if not text.strip():
            print(f"WARNING: No extractable text in {pdf.name} (scanned PDF needs OCR).")
            continue

        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            ids.append(f"{pdf.stem}-{i}")
            docs.append(chunk)
            metas.append({"source": pdf.name, "chunk": i})

    if not docs:
        raise SystemExit("No text extracted from PDFs. If they are scanned images, OCR is required.")

    # Embed in batches
    embeddings: list[list[float]] = []
    for i in range(0, len(docs), EMB_BATCH):
        embeddings.extend(embed_texts(docs[i : i + EMB_BATCH]))

    
    collection.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)

    print(
        f"Indexed {len(docs)} chunks from {len(pdfs)} PDFs into LOCAL Chroma\n"
        f"Collection : {CHROMA_COLLECTION}\n"
        f"Path       : {CHROMA_DIR}\n"
        f"Embedding  : {EMBED_MODEL_NAME}\n"
        f"Chunking   : size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}"
    )


if __name__ == "__main__":
    main()
