from typing import List, Dict
import re

class StructuralParser:
    """Filters sentences based on structural rules."""

    def parse(self, sentences: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Filters sentences to remove duplicates and noise.
        """
        seen_texts = set()
        validated_sentences = []

        for sent in sentences:
            text = sent.get("text", "")
            
            # 1. Remove duplicates
            if text in seen_texts:
                continue
            seen_texts.add(text)
            
            # 2. Remove noisy lines
            # Check for high symbol density (e.g. tables)
            symbol_count = len(re.findall(r'[^\w\s]', text))
            if symbol_count / len(text) > 0.3:  # Heuristic: >30% symbols
                continue
            
            # 3. Basic length filtering (already done partially in lexical, but reinforcing)
            if len(text) < 10:  # Too short to be meaningful in structural context
                continue

            validated_sentences.append(sent)

        return validated_sentences

if __name__ == "__main__":
    # Test
    sentences = [
        {"text": "This is a valid sentence.", "index": 0},
        {"text": "This is a valid sentence.", "index": 1},  # Duplicate
        {"text": "-------", "index": 2}, # Noise
        {"text": "Table 1 | Data | Value", "index": 3}, # Noise
        {"text": "A good sentence.", "index": 4}
    ]
    parser = StructuralParser()
    results = parser.parse(sentences)
    for res in results:
        print(res)
