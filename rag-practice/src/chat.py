import os
from typing import List, Dict, Any

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

# ---------- Config ----------
CHROMA_DIR = os.environ.get("CHROMA_DIR", "storage/chroma")
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "docs")

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
TOP_K = 4

# Keep context bounded (chars) so prompts don't blow up
MAX_CONTEXT_CHARS = 12000

# Must match ingest embedding model
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBED_MODEL = SentenceTransformer(EMBED_MODEL_NAME)

# Groq client (reads GROQ_API_KEY from env if not passed)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
# ---------------------------


def embed_query(text: str) -> List[float]:
    return EMBED_MODEL.encode(
        [text],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0].tolist()


def build_context(docs: List[str], metas: List[Dict[str, Any]], max_chars: int) -> str:
    parts: List[str] = []
    total = 0
    for doc, meta in zip(docs, metas):
        block = f"[Source: {meta.get('source')} | Chunk: {meta.get('chunk')}]\n{doc}\n"
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    return "\n---\n".join(parts)


def main():
    # Load local Chroma
    chroma = chromadb.PersistentClient(path=CHROMA_DIR)
    col = chroma.get_collection(CHROMA_COLLECTION)

    print(f"Chroma: {CHROMA_DIR} | collection='{CHROMA_COLLECTION}' | vectors={col.count()}")
    print(f"Embed: {EMBED_MODEL_NAME} | Groq model: {GROQ_MODEL} | top_k={TOP_K}")
    print("Type 'exit' to quit.\n")

    while True:
        q = input("Question> ").strip()
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break

        q_emb = embed_query(q)

        res = col.query(
            query_embeddings=[q_emb],
            n_results=TOP_K,
            include=["documents", "metadatas", "distances"],
        )

        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dists = res["distances"][0]

        context = build_context(docs, metas, MAX_CONTEXT_CHARS)

        system_msg = (
            "You are a RAG assistant. Use ONLY the provided context. "
            "If the answer is not in the context, say: "
            "\"I don't know from the provided documents.\" "
            "Cite sources by file name."
        )

        user_msg = f"""CONTEXT:
{context}

QUESTION:
{q}

Return:
1) Answer
2) Sources (file names)
"""

        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )

        answer = completion.choices[0].message.content

        print("\n" + answer)
        print("\nRetrieved chunks:")
        for i, (m, d) in enumerate(zip(metas, dists), start=1):
            print(f"  {i}. {m.get('source')} | chunk={m.get('chunk')} | distance={d}")
        print()

if __name__ == "__main__":
    main()
