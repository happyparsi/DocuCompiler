# MODELS & OTHERS DOCUMENTATION

This document covers all the Core Machine Learning models, Optimizers, and NLP logic files residing inside the `src/` directory.

## Core System Integration (Data Flow)
The text goes through a strict sequence of transformations:
`File` -> `extractor.py` (Raw Text) -> `lexical.py` (Sentences) -> `structural.py` (Filtered Sentences) -> `semantic.py` (Embeddings + PageRank Score) -> `ir.py` (Saved DB State) -> `optimizer.py` (Top Ranked Sentences) -> `generator.py` (Markdown Summary Output). 

Separately, `query.py` takes embeddings to perform RAG (Retrieval-Augmented Generation) using FAISS index retrieval and a T5 generation model equipped with beam search and markdown formatting.

### Key Enhancements
- **`query.py`**: Expanded retrieval context ($k=7$) and answer length (512 tokens) with `num_beams=4` for superior answer quality.
- **`generator.py`**: Rewritten to output beautifully structured markdown natively, adding headings and clean formatting out-of-the-box for React Markdown rendering.
