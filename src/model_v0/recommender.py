import pandas as pd
import torch


def cosine_similarity_recommendations(input_dataset: pd.DataFrame, input_embeddings: torch.Tensor) -> pd.DataFrame:
    cosine_similarities = input_dataset['embeddings'].apply(lambda emb: torch.nn.functional.cosine_similarity(input_embeddings, emb, dim=0))
    input_dataset['cosine_similarity'] = cosine_similarities
    recommendations = input_dataset.sort_values(by='cosine_similarity', ascending=False)
    highest_similarity_row = recommendations.iloc[0]
    technologies_to_recommend = highest_similarity_row['technologies']
    return technologies_to_recommend