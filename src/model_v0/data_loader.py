import h5py
import pandas as pd
import torch

# Specify the file path of the HDF5 file
DATASET_FILE_PATH = "/app/cached_models/embeddings_dataset/devpost_data_with_embeddings.h5"
EMBEDDINGS_COLUMN_NAME = "embeddings"


def load_dataset_dataframe() -> pd.DataFrame:
    raw_dataset = _load_recommendations_dataframe(DATASET_FILE_PATH)
    embeddings_dataset = _convert_embeddings_format_dataframe(raw_dataset, EMBEDDINGS_COLUMN_NAME)
    return embeddings_dataset


def _load_recommendations_dataframe(hdf5_file_path: str) -> pd.DataFrame: 
    """
    Load data from an H5 file and return it as a Pandas DataFrame.
    """
    with h5py.File(hdf5_file_path, "r") as h5_file:
        data = {key: h5_file[key][:] for key in h5_file.keys() if key != 'embeddings'}
        df = pd.DataFrame(data)
        embeddings_list = [embeddings for embeddings in h5_file['embeddings']]
        df[EMBEDDINGS_COLUMN_NAME] = embeddings_list
    return df


def _convert_embeddings_format_dataframe(raw_df: pd.DataFrame, \
    embeddings_column_name: str) -> pd.DataFrame:
    """
    Convert a specific column in the DataFrame to PyTorch tensors.
    """
    embeddings_tensors = [torch.tensor(embeddings) for embeddings in raw_df[embeddings_column_name]]
    raw_df[embeddings_column_name] = embeddings_tensors
    return raw_df

