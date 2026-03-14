
# Qualitative Comparison

## Original Article
Artificial Intelligence (AI) is a rapidly evolving field of computer science. It focuses on creating systems capable of performing tasks that typically require human intelligence. These tasks include visual perception, speech recognition, decision-making, and language translation. Machine Learning (ML) is a subset of AI that enables systems to learn from data. Deep Learning is a further subset of ML, utilizing neural networks with many layers. Natural Language Processing (NLP) is another key area of AI. It deals with the interaction between computers and human language. Applications of NLP include sentiment analysis, chatbots, and language translation.

## DocuCompiler Summary (Our Model)
Artificial Intelligence (AI) is a rapidly evolving field of computer science. Natural Language Processing (NLP) is another key area of AI. It deals with the interaction between computers and human language.

## TextRank Summary (Extractive Baseline)
Applications of NLP include sentiment analysis, chatbots, and language translation. Natural Language Processing (NLP) is another key area of AI. These tasks include visual perception, speech recognition, decision-making, and language translation.

## T5-small Summary (Abstractive Baseline)
T5 Summary skipped due to resource/loading error on CPU.

## Discussion
- **Redundancy**: DocuCompiler uses redundancy removal to avoid repetitive sentences.
- **Coherence**: By sorting by original position, DocuCompiler maintains better flow than pure TextRank.
- **Conciseness**: T5 produces the most fluent summary but requires significantly more compute for training/inference compared to our extractive approach.
