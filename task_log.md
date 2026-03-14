# DocuCompiler Project Tasks

- [x] **Phase 0: Ground Setup**
    - [x] Create `requirements.txt`
    - [x] Create `setup_env.py`
    - [x] Download NLTK/Spacy models

- [x] **Phase 1: Build the Source Reader**
    - [x] Implement PDF, DOCX, TXT extractors
    - [x] Create unified extractor interface

- [x] **Phase 2: Lexical Analysis Layer**
    - [x] Implement sentence tokenization and cleaning

- [x] **Phase 3: Structural Parsing Layer**
    - [x] Remove duplicates and noisy lines

- [x] **Phase 4: Semantic Graph Constructor**
    - [x] Implement MiniLM embeddings and PageRank scoring

- [x] **Phase 5: Build the S-IR (Semantic Intermediate Representation)**
    - [x] Define `SemanticIR` and SQLite persistence

- [x] **Phase 6: Semantic Optimization Engine**
    - [x] Implement DCE and redundancy removal

- [x] **Phase 7: Target Generator (Summary Emitter)**
    - [x] Implement paragraph and bullet summary generation

- [x] **Phase 8: Query Compiler (QA System)**
    - [x] Build FAISS index and T5-small QA pipeline

- [x] **Phase 9: Evaluation**
    - [x] Implement ROUGE and F1 metrics
    - [x] Orchestrate via `main.py`

- [x] **Phase 10: Research-Grade Polish**
    - [x] Implement ablation study and performance benchmarking

- [x] **Phase 11: Benchmark Suite Construction**
    - [x] Implement baseline models (TF-IDF Ranking, Plain TextRank)
    - [x] Implement abstractive baselines (T5, BART)
    - [x] Create evaluation dataset subset

- [x] **Phase 12: Efficiency Metrics & Scaling**
    - [x] Implement peak memory measurement
    - [x] Analyze scaling behavior (Time vs. Sentences)
    - [x] Calculate "Efficiency Score" (ROUGE-L / Inference Time)

- [x] **Phase 13: Evaluation Execution & Qualitative Analysis**
    - [x] Run comparative benchmarks
    - [x] Perform qualitative review of redundancy and coherence

- [x] **Phase 14: Final Research Synthesis**
    - [x] Compile all metrics and scaling graphs
    - [x] Finalize "DocuCompiler" contribution positioning
