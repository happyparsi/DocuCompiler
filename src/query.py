import numpy as np
from typing import List, Dict

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    import torch
except ImportError:
    print("Warning: QA dependencies (faiss, transformers, torch) not installed.")
    faiss = None


class QueryCompiler:
    """
    QA System using FAISS retrieval + T5 generation.
    Enhanced: larger context window (k=7), longer answers (max_length=512),
    beam search (num_beams=4), and structured markdown output.
    """

    def __init__(
        self,
        embedding_model_name: str = 'all-MiniLM-L6-v2',
        qa_model_name: str = 'google/flan-t5-base'
    ):
        if faiss is None:
            raise ImportError("faiss, transformers, or torch not installed.")

        print("Loading QA models...")
        self.encoder = SentenceTransformer(embedding_model_name)
        self.tokenizer = T5Tokenizer.from_pretrained(qa_model_name, legacy=False)
        self.model = T5ForConditionalGeneration.from_pretrained(qa_model_name)
        self.model.eval()

        self.index = None
        self.sentences = []

    def build_index(self, sentences: List[Dict[str, any]], embeddings: np.ndarray):
        """Builds FAISS index from sentences and embeddings."""
        self.sentences = sentences
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

    def retrieve(self, query: str, k: int = 7) -> List[str]:
        """Retrieves top-k relevant sentences for a query (expanded to 7 for richer context)."""
        if not self.index:
            raise ValueError("Index not built. Call build_index first.")

        query_vec = self.encoder.encode([query]).astype('float32')

        # Clamp k to available sentences
        actual_k = min(k, len(self.sentences))
        distances, indices = self.index.search(query_vec, actual_k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.sentences):
                results.append(self.sentences[idx]['text'])
        return results

    def answer(self, query: str, k: int = 7) -> str:
        """
        Generates a structured markdown answer using retrieved context.
        Uses beam search (num_beams=4) and longer max_length (512) for quality.
        """
        context_sentences = self.retrieve(query, k)
        context = " ".join(context_sentences)

        # Trim context to avoid exceeding T5's token limit (~512 tokens input)
        # Rough heuristic: 4 chars ≈ 1 token
        max_context_chars = 1500
        if len(context) > max_context_chars:
            context = context[:max_context_chars]

        # Structured prompt for Flan-T5
        input_text = (
            f"Answer the following question in as much detail as possible, using only the provided context.\n\n"
            f"Question: {query}\n\n"
            f"Context: {context}\n\n"
            f"Detailed Answer:"
        )

        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )

        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=512,          # Much longer answers than before
                num_beams=5,             # Increased beam search for better quality
                early_stopping=True,
                no_repeat_ngram_size=3,  # Avoid repetitive phrases
                length_penalty=2.0,      # Higher length penalty to strongly encourage longer, more detailed answers
                temperature=0.7,         # Add slight temperature for better text flow
                do_sample=True           # Enable sampling to use temperature
            )

        raw_answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Post-process: wrap in markdown formatting for rich display
        formatted = self._format_answer(raw_answer, query)
        return formatted

    def _format_answer(self, raw: str, query: str) -> str:
        """
        Wraps the raw T5 answer in clean markdown formatting.
        Adds heading, formats sentences, and ensures proper spacing.
        """
        if not raw or not raw.strip():
            return "_No answer could be generated for this question._"

        raw = raw.strip()

        # Capitalise first letter
        raw = raw[0].upper() + raw[1:] if len(raw) > 1 else raw

        # If answer has multiple sentences, split into a readable block
        sentences = [s.strip() for s in raw.replace('. ', '.\n').split('\n') if s.strip()]

        if len(sentences) <= 1:
            return raw

        # Build a nice markdown block
        body = "\n\n".join(sentences)
        return body


if __name__ == "__main__":
    pass
