"""
Module to run model for feature extraction.
"""

import torch
from transformers import pipeline, AutoModel


MODEL_NAME = "bert-large-uncased"
CACHED_DIRECTORY = "/Users/Omega/dev/sprint/Recommendation-Engine/src/cached_models/pretrained_bert"#"/app/cached_models/pretrained_bert"


if __name__ == "__main__":
    """
    Setup script to download the BERT model to memory in src/cached_models
    """
    model = AutoModel.from_pretrained(MODEL_NAME)
    model.save_pretrained(CACHED_DIRECTORY)
else:
    BERT_FEATURE_MODEL = pipeline("feature-extraction", model=CACHED_DIRECTORY)


def generate_sentence_embeddings(sentence: str) -> torch.Tensor:
    embeddings = BERT_FEATURE_MODEL(sentence)
    embeddings_list = [torch.tensor(embedding) for embedding in embeddings[0]]
    embeddings_tensor = torch.stack(embeddings_list)
    cls_index = 0
    cls_embedding = embeddings_tensor[cls_index]
    return cls_embedding
