# DocuCompiler - Project Summary

## Overview
DocuCompiler is an end-to-end document processing and summarization tool. 
It ingests files (PDF, text, etc.) or pasted text, performs lexical, structural, and semantic analysis, then builds an optimized extractive summary via a multi-stage pipeline.

## Key components
- `app.py`: FastAPI service exposing REST endpoints for signup/login/auth and summarization.
- `src/extractor.py`: Source document reading logic.
- `src/lexical.py`: Tokenization and sentence-level NLP analysis.
- `src/structural.py`: Sentence validation and structure parsing.
- `src/semantic.py`: Semantic graph construction with sentence embeddings.
- `src/optimizer.py`: Sentence ranking and optimization strategy selection.
- `src/generator.py`: Final natural language summary generation.
- `src/query.py` (optional): Query-based answer extraction from summaries.

## API Endpoints
- `/api/signup`
- `/api/login`
- `/api/me`
- `/api/sessions`
- `/api/sessions/{session_id}`
- `/api/summarize`

## Environment
- Python dependencies in `requirements.txt`
- SQLite local DB `app.db` is initialized automatically by `app.py`.

## Current task performed
- Added summary text to `PROJECT_SUMMARY.md`.
- Committed summary into local git repository.

## Notes
- Includes seed user setup for `paras_rawal117`.
- Supports CORS and static site serving for front-end.
