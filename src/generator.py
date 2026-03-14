from typing import List, Dict

class TargetGenerator:
    """Generates summaries from optimized sentences."""
    
    def generate(self, sentences: List[Dict[str, any]], mode: str = 'paragraph') -> str:
        """
        Generates a summary.
        Mode: 'paragraph' or 'bullet'.
        """
        if not sentences:
            return ""
            
        # Sort by original index for coherent flow
        sorted_sentences = sorted(sentences, key=lambda s: s['index'])
        texts = [s['text'] for s in sorted_sentences]
        
        if mode == 'bullet':
            return "\n".join([f"- {text}" for text in texts])
        else:
            return " ".join(texts)

if __name__ == "__main__":
    sents = [
        {"index": 0, "text": "First sentence."},
        {"index": 5, "text": "Later sentence."}
    ]
    gen = TargetGenerator()
    print("Paragraph:\n", gen.generate(sents, 'paragraph'))
    print("\nBullet:\n", gen.generate(sents, 'bullet'))
