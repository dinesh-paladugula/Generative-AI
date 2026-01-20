
# RAG Codebase - Notes

## Purpose
Build a **Retrieval-Augmented Generation (RAG)** pipeline that answers user questions using **external documents** by:
- Converting documents into embeddings
- Storing them in a vector database
- Retrieving relevant context
- Generating grounded answers using an LLM

## High-Level Architecture
```
Documents → Chunking → Embeddings → Vector DB (Chroma)
                                   ↓
User Question → Retrieval → Prompt + Context → LLM → Answer
```

## Folder Structure
```
docs/
db/chroma_db/
1_ingestion_pipeline.py
2_retrieval_pipeline.py
3_answer_generation.py
4_history_aware_generation.py
5_recursive_character_text_spliiter.py
6_semantic_chunking.py
7_agentic_chunking.py
9_retrieval_methods.py
10_multi_query_retrieval.py
11_reciprocal_rank_fusion.py
```

## Ingestion Pipeline
- Loads `.txt` files
- Chunks text
- Creates embeddings
- Stores in ChromaDB

## Retrieval Pipeline
- Loads ChromaDB
- Retrieves top-k relevant chunks

## Answer Generation
- Uses retrieved context
- Generates grounded answers

## History-Aware RAG
- Rewrites follow-up questions
- Maintains chat history

## Chunking Strategies
- Recursive
- Semantic
- Agentic

## Retrieval Enhancements
- Multi-query retrieval
- Reciprocal Rank Fusion

## Documents
- Google, Microsoft, Nvidia, SpaceX, Tesla
- PDF's

## Execution Order
1. Ingestion
2. Retrieval
3. Generation
4. Conversation
