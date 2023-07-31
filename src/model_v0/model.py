"""
Module to run model for feature extraction.
"""

import torch
from transformers import pipeline


CACHED_DIRECTORY = "/app/cached_models/pretrained_bert"
BERT_FEATURE_MODEL = pipeline("feature-extraction", model=CACHED_DIRECTORY)

def generate_sentence_embeddings(sentence: str) -> torch.Tensor:
    embeddings = BERT_FEATURE_MODEL(sentence)
    embeddings_list = [torch.tensor(embedding) for embedding in embeddings[0]]
    embeddings_tensor = torch.stack(embeddings_list)
    cls_index = 0
    cls_embedding = embeddings_tensor[cls_index]
    return cls_embedding
