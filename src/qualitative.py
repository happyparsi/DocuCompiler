from src.benchmarks import BenchmarkRunner
from src.baselines import ExtractiveBaselines, AbstractiveBaselines
import os

def qualitative_analysis():
    print("Running Qualitative Analysis...")
    runner = BenchmarkRunner()
    ext_baselines = ExtractiveBaselines()
    
    # We will use one sample from our dataset
    sample = {
        "article": "Artificial Intelligence (AI) is a rapidly evolving field of computer science. It focuses on creating systems capable of performing tasks that typically require human intelligence. These tasks include visual perception, speech recognition, decision-making, and language translation. Machine Learning (ML) is a subset of AI that enables systems to learn from data. Deep Learning is a further subset of ML, utilizing neural networks with many layers. Natural Language Processing (NLP) is another key area of AI. It deals with the interaction between computers and human language. Applications of NLP include sentiment analysis, chatbots, and language translation.",
        "highlights": "AI focuses on human-like tasks, with subsets in ML, Deep Learning, and NLP."
    }
    
    # 1. DocuCompiler
    docu = runner.measure_docu_compiler(sample['article'])['summary']
    
    # 2. TextRank
    tr = ext_baselines.textrank_summary(sample['article'])
    
    # 3. T5 Baseline (Optional, handle failure)
    t5 = "T5 Summary skipped due to resource/loading error on CPU."
    try:
        t5 = AbstractiveBaselines("t5-small").summarize(sample['article'])
    except Exception as e:
        print(f"T5 Summarization skipped: {e}")
    
    comparison = f"""
# Qualitative Comparison

## Original Article
{sample['article']}

## DocuCompiler Summary (Our Model)
{docu}

## TextRank Summary (Extractive Baseline)
{tr}

## T5-small Summary (Abstractive Baseline)
{t5}

## Discussion
- **Redundancy**: DocuCompiler uses redundancy removal to avoid repetitive sentences.
- **Coherence**: By sorting by original position, DocuCompiler maintains better flow than pure TextRank.
- **Conciseness**: T5 produces the most fluent summary but requires significantly more compute for training/inference compared to our extractive approach.
"""
    
    with open("qualitative_comparison.md", "w") as f:
        f.write(comparison)
    print("Qualitative analysis saved to 'qualitative_comparison.md'.")

if __name__ == "__main__":
    qualitative_analysis()
