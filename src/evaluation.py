from typing import List, Dict
try:
    from rouge_score import rouge_scorer
except ImportError:
    print("Warning: rouge-score not installed.")
    rouge_scorer = None

class Evaluator:
    """Evaluates summaries and QA performance."""
    
    def __init__(self):
        if rouge_scorer:
            self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        else:
            self.scorer = None

    def evaluate_summary(self, generated_summary: str, reference_summary: str) -> Dict[str, float]:
        """Computes ROUGE scores."""
        if not self.scorer:
            print("ROUGE scorer not available.")
            return {}
            
        scores = self.scorer.score(reference_summary, generated_summary)
        return {
            "rouge1": scores['rouge1'].fmeasure,
            "rouge2": scores['rouge2'].fmeasure,
            "rougeL": scores['rougeL'].fmeasure
        }

    def evaluate_qa(self, predicted_answer: str, ground_truth: str) -> Dict[str, float]:
        """Computes Exact Match and F1 for QA."""
        pred_tokens = predicted_answer.lower().split()
        truth_tokens = ground_truth.lower().split()
        
        common = set(pred_tokens) & set(truth_tokens)
        num_same = len(common)
        
        precision = num_same / len(pred_tokens) if len(pred_tokens) > 0 else 0
        recall = num_same / len(truth_tokens) if len(truth_tokens) > 0 else 0
        
        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
            
        exact_match = 1.0 if predicted_answer.strip().lower() == ground_truth.strip().lower() else 0.0
        
        return {
            "exact_match": exact_match,
            "f1": f1
        }

if __name__ == "__main__":
    evaluator = Evaluator()
    if evaluator.scorer:
        res = evaluator.evaluate_summary("This is a summary.", "This is a reference summary.")
        print("Summary Scores:", res)
        
    qa_res = evaluator.evaluate_qa("The sky is blue.", "The sky is blue.")
    print("QA Scores:", qa_res)
