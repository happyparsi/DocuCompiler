# DocuCompiler: Getting Started Guide

This guide provides the step-by-step commands to set up the environment, run benchmarks, generate research plots, and process your own documents for summarization and Q&A.

## 1. Environment Setup

First, open your terminal in VS Code (`` Ctrl+` ``) and run the following commands to create a virtual environment and install dependencies.

```powershell
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Download required spaCy model for lexical analysis
python -m spacy download en_core_web_sm
```

## 2. Display Results and Comparisons

To run the benchmarks and generate the research-grade plots for the paper, use these commands:

```powershell
# Run the benchmark comparison (results saved to benchmark_results.log)
python -m src.benchmarks

# Run the ablation study (impact of optimization)
python -m src.ablation

# Generate the research-grade plots (saved in the /plots folder)
python src/research_visualizer.py
```

## 3. Running the Project (Summarization & QA)

You can process any **Text (.txt)** or **PDF (.pdf)** document using the main entry point:

### Simple Summarization
```powershell
# Replace 'your_document.pdf' with your actual file path
python main.py --input "path/to/your_document.pdf"
```

### Summarization + Q&A
```powershell
# Get a summary and ask a specific question
python main.py --input "sample.txt" --query "What is the main conclusion of this document?"
```

### Advanced Options
- `--mode`: Change output format (`paragraph` or `bullet`)
- `--strategy`: Change optimization sensitivity (`aggressive`, `moderate`, `conservative`)

```powershell
python main.py --input "document.pdf" --mode bullet --strategy aggressive
```

## 4. Troubleshooting
- **Missing Models**: If you see errors about "MiniLM" or "T5", ensure you have an active internet connection for the first run so the models can download automatically.
- **Python Version**: This project is optimized for Python 3.10+.


pip install rouge-score
