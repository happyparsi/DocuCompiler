from src.query import QueryCompiler
import numpy as np
from sentence_transformers import SentenceTransformer

def test_qa():
    qc = QueryCompiler()
    
    # Mock some sentences from a paper
    sentences = [
        {"text": "Self-supervised learning (SSL) has emerged as a powerful paradigm for representation learning without manual labels."},
        {"text": "In this paper, we propose a novel Siamese network architecture for SSL that avoids collapse."},
        {"text": "Future work will focus on extending this architecture to video and multimodal data."},
        {"text": "Extensive experiments on ImageNet demonstrate the effectiveness of our approach."},
        {"text": "References: [1] D. Smith et al., 2020, pp. 233-240."},
        {"text": "We evaluate the representation quality using linear probing and k-NN classifiers."}
    ]
    
    # Generate embeddings
    print("Generating embeddings...")
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    texts = [s['text'] for s in sentences]
    embeddings = encoder.encode(texts)
    
    qc.build_index(sentences, embeddings)
    
    query = "what is the future scope of this?"
    print("Querying...")
    
    # Try different generation approaches
    context_sentences = qc.retrieve(query, 7)
    context = " ".join(context_sentences)
    
    prompt = (
        f"Answer the question based on the context below. Provide a detailed answer.\n\n"
        f"Context: {context}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )
    
    inputs = qc.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    
    print("Original params:")
    outputs1 = qc.model.generate(inputs.input_ids, max_length=512, num_beams=5, early_stopping=True, no_repeat_ngram_size=3, length_penalty=2.0, temperature=0.7, do_sample=True)
    print(qc.tokenizer.decode(outputs1[0], skip_special_tokens=True))
    
    print("\nNew params (beam search, no sample):")
    outputs2 = qc.model.generate(inputs.input_ids, max_length=512, num_beams=4, early_stopping=True, length_penalty=1.0)
    print(qc.tokenizer.decode(outputs2[0], skip_special_tokens=True))
    
    print("\nGreedy params:")
    outputs3 = qc.model.generate(inputs.input_ids, max_length=512)
    print(qc.tokenizer.decode(outputs3[0], skip_special_tokens=True))

if __name__ == '__main__':
    test_qa()
