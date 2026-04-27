from typing import List, Dict
import re


class TargetGenerator:
    """
    Generates rich, markdown-formatted summaries from optimized sentences.
    Produces structured output with bold headings, proper spacing,
    and clean paragraph or bullet formatting — suitable for react-markdown rendering.
    """

    def generate(self, sentences: List[Dict[str, any]], mode: str = 'paragraph') -> str:
        if not sentences:
            return ""

        # Sort by original document position so the narrative makes sense
        sorted_sentences = sorted(sentences, key=lambda s: s['index'])
        texts = [s['text'] for s in sorted_sentences]

        if mode == 'bullet':
            return self._generate_bullet(texts)
        else:
            return self._generate_paragraph(texts)

    def _generate_bullet(self, texts: List[str]) -> str:
        """
        Generates a well-structured bullet-point summary with a bold heading.
        Groups bullets into chunks for readability.
        """
        if not texts:
            return ""

        lines = []
        lines.append("## 📋 Key Points\n")

        for text in texts:
            # Clean up sentence ending
            t = text.strip()
            if t and not t.endswith(('.', '!', '?')):
                t += '.'
            lines.append(f"- {t}")

        return "\n".join(lines)

    def _generate_paragraph(self, texts: List[str]) -> str:
        """
        Generates a rich paragraph summary with:
        - A bold ## heading
        - Content grouped into readable paragraphs (every ~3 sentences)
        - An italic closing note
        """
        if not texts:
            return ""

        # Group sentences into paragraphs (every 3 sentences)
        group_size = 3
        groups = [texts[i:i + group_size] for i in range(0, len(texts), group_size)]

        parts = []
        parts.append("## 📄 Document Summary\n")

        for idx, group in enumerate(groups):
            para = " ".join([t.strip() for t in group])
            # Ensure paragraph ends with punctuation
            if para and not para[-1] in '.!?':
                para += '.'
            parts.append(para)

        # Closing note
        parts.append(
            f"\n---\n*Summary generated from **{len(texts)} key sentences** "
            f"extracted from the document. Ask a follow-up question below to explore further.*"
        )

        return "\n\n".join(parts)


if __name__ == "__main__":
    sents = [
        {"index": 0, "text": "Machine learning is a subset of artificial intelligence."},
        {"index": 1, "text": "It enables systems to learn from data automatically."},
        {"index": 2, "text": "Supervised learning uses labeled training data."},
        {"index": 3, "text": "Unsupervised learning finds hidden patterns without labels."},
        {"index": 4, "text": "Neural networks are inspired by the human brain structure."},
    ]
    gen = TargetGenerator()
    print("=== PARAGRAPH ===")
    print(gen.generate(sents, 'paragraph'))
    print("\n=== BULLET ===")
    print(gen.generate(sents, 'bullet'))
