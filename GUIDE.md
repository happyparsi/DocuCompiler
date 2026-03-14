# DocuCompiler: User Guide & Execution Manual

Welcome to DocuCompiler. This guide provides all necessary steps to run, test, and evaluate the system.

## 1. Environment Setup

Ensure you have Python 3.10+ installed.

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Download Models & Data
Run the setup script to download required NLTK and spaCy models:
```bash
python setup_env.py
```

## 2. Running the Project

### Basic Usage (File Input)
To process a file and generate a summary:
```bash
python main.py --input path/to/your/file.pdf
```
Supported formats: `.pdf`, `.docx`, `.txt`.

### How to provide input
The `main.py` script accepts a `--input` argument followed by the absolute or relative path to your document.

### Where results are stored
- **Console Output**: The generated summary and QA answers are printed directly to the terminal.
- **S-IR Persistence**: The intermediate representation is stored in a SQLite database (e.g., `docucompiler.db` or similar defined in `src/ir.py`).

## 3. Running Research Benchmarks

The research evaluation suite provides comparative data against TextRank and TF-IDF.

### Quantitative Benchmarks
Measure ROUGE scores and latency:
```bash
python -m src.benchmarks
```

### Scaling Analysis
Measure how performance scales with document size:
```bash
python -m src.scaling
```

### Ablation Study
Measure the impact of optimization layers:
```bash
python -m src.ablation_v3
```

### Qualitative Comparison
Generate a side-by-side comparison markdown file:
```bash
python -m src.qualitative
```
This generates `qualitative_comparison.md` in the root directory.

## 4. Running Tests

To verify component integrity:

### Automated Unit Tests
```bash
pytest tests/
```

### Minimal Component Validation
A quick diagnostic script to check if AI models are loading correctly:
```bash
python test_evaluation_minimal.py
```

### Generating Performance Graphs
To generate research-grade plots (ROUGE, scaling, ablation):
```bash
python src/visualizer.py
```
This will create a `plots/` directory with:
- `rouge_comparison.png`
- `scaling_behavior.png`
- `ablation_study.png`
