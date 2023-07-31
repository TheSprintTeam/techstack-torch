import torch
from transformers import pipeline

model = "bert-large-uncased"
bertNLP = pipeline("feature-extraction", model=model)

def generate_sentence_embeddings(sentence: str) -> torch.Tensor:
    embeddings = bertNLP(sentence)
    embeddings_list = [torch.tensor(embedding) for embedding in embeddings[0]]
    embeddings_tensor = torch.stack(embeddings_list)
    cls_index = 0
    cls_embedding = embeddings_tensor[cls_index]
    return cls_embedding