
import json
import os
import pandas as pd
import torch
from torch.utils.data import Dataset

from .data_struct import PreprocessingObject
from ..preprocessing import PreprocessorFactory, BasePreprocessor
from typing import List, Any, Optional, Dict, Union, Tuple
from .dataset_utils import ensure_list, get_processed_data


class DrugProteinDataset(Dataset):
    """
    Dataset to load and preprocessing drug-protein interaction data.

    Attributes:
    - data (pd.DataFrame): Raw data containing drug and protein information.
    - drug_preprocess_type (List[str]): Types of preprocessing to apply to drug data.
    - drug_attributes (List[str]): Attributes/columns from the dataframe to apply preprocessing.
    - online_preprocessing_drug (List[bool]): Whether to preprocessing drug data online.
    - protein_preprocess_type (List[str]): Types of preprocessing to apply to protein data.
    - protein_attributes (List[str]): Attributes/columns from the dataframe to apply preprocessing.
    - online_preprocessing_protein (List[bool]): Whether to preprocessing protein data online.
    - shard_directory (str, optional): Directory for saving/loading shard files.
    - memory_proportion (float): Proportion of system memory to use when determining sharding.
    - threads (int): Number of threads to use for parallel processing.

    Methods:
    - _initialize_preprocesses: Initialize and prepare preprocessors.
    - _should_shard: Determine if data should be sharded based on size and system memory.
    - _determine_shard_size: Determine the size of each shard based on data size and system memory.
    - _preprocessing_done: Check if preprocessing has already been done for the dataset.
    - _load_mapping: Load the mapping dictionary from the shard directory.
    """

    def __init__(self,
                 data: pd.DataFrame,
                 preprocesses: PreprocessingObject,
                 save_directory: Optional[str] = None,
                 threads: int = 4) -> None:
        """
           Initialize the DrugProteinDataset.

           Parameters:
           - data (pd.DataFrame): Raw dataset containing drug and protein information.
           - drug_preprocess_type (Union[List[str], str]): Types of preprocessing to apply to drug data.
           - drug_attributes (Union[List[str], str]): Attributes/columns from the dataframe to apply preprocessing on for drugs.
           - online_preprocessing_drug (Union[List[bool], bool]): Flags indicating if preprocessing of drug data should occur online.
           - protein_preprocess_type (Union[List[str], str]): Types of preprocessing to apply to protein data.
           - protein_attributes (Union[List[str], str]): Attributes/columns from the dataframe to apply preprocessing on for proteins.
           - online_preprocessing_protein (Union[List[bool], bool]): Flags indicating if preprocessing of protein data should occur online.
           - shard_directory (Optional[str]): Path to the directory where shard files are saved/loaded. Default is None.
           - memory_proportion (float): Proportion of system memory to use when determining sharding. Default is 0.6.
           - threads (int): Number of threads to use for parallel processing. Default is 4.
        """

        self.data = data
        self.preprocesses = preprocesses
        self.save_directory = save_directory
        self.threads = threads

        self.mapping = self._initialize_preprocesses()

        self._clean_data()

    def _initialize_preprocesses(self) -> List[Tuple[Any, Dict[Any, Any]]]:
        mapping = []

        for attribute, preprocess, in_memory, online in self.preprocesses:
            if attribute is None:
                mapping.append((None, None))
                continue

            data = self.data[attribute].unique().tolist()
            if online:
                if preprocess is not None:
                    data = preprocess.data_preparations(data)
                mapping.append((attribute, None))
                continue

            if self._preprocessing_done(preprocess.__class__.__name__, attribute):
                if not in_memory:
                    mapping_data = self._load_mapping(preprocess, attribute)
                else:
                    path = preprocess.get_saved_path(
                        self.save_directory, attribute)
                    mapping_data = preprocess.load_preprocessed_to_memory(path)
                    _ = self._load_mapping(preprocess, attribute)
            else:
                info_dict = preprocess.process_and_get_info(
                    data, self.save_directory, in_memory, self.threads, attribute)
                mapping_data = info_dict['mapping_info'] if not in_memory else info_dict['processed_data']

            mapping.append((attribute, mapping_data))

        return mapping

    def _preprocessing_done(self, preprocess_type: str, attribute: str) -> bool:
        """
        Check if preprocessing has been done for the entire dataset.

        Returns:
        - bool: True if preprocessing files are found, False otherwise.
        """
        mapping_path = os.path.join(
            self.save_directory, f"{preprocess_type}_{attribute}_mapping_info.json")
        return os.path.exists(mapping_path)

    def _load_mapping(self, preprocess: BasePreprocessor, attribute: str) -> Dict[Any, Any]:
        """
        Load the mapping dictionary from the shard directory.

        Returns:
        - Dict: mapping dictionary of the relevant data
        """
        mapping_path = os.path.join(self.save_directory,
                                    f"{preprocess.__class__.__name__}_{attribute}_mapping_info.json")

        # Use Python's json module to load the mapping
        with open(mapping_path, 'r') as file:
            mapping = json.load(file)

        nones = []
        for item in mapping.keys():
            if mapping[item] is None:
                nones.append(item)

        preprocess.set_invalid_data(nones)

        return mapping

    def _clean_data(self) -> None:
        """
        Clean the data by removing rows where processed data is None for
        any of the preprocessed attributes.
        """
        # Combine attributes for easier iteration
        combined_attributes = zip(
            self.preprocesses.online,
            self.mapping,
            self.preprocesses.preprocessing_type
        )

        # This list comprehension iteratively processes each row and checks if any
        # of the processed data results in a 'None' value.
        # It returns a boolean list with 'True' at the positions where 'None' is found.

        for online, mapping, pre_process in combined_attributes:
            none_col_list = pre_process.collect_invalid_data(
                online, self.data[mapping[0]].unique())
            self.data = self.data[~self.data[mapping[0]].isin(none_col_list)]

    def __len__(self) -> int:
        """
        Return the number of samples in the dataset.

        Returns:
        - int: Number of data samples.
        """
        return len(self.data.index)

    def __getitem__(self, index: int) -> Any:
        """
        Retrieve an item from the dataset at the specified index.

        This method uses online or precomputed preprocessors for drugs and proteins
        to retrieve the preprocessed data samples. It further differentiates
        between data samples stored in memory and those that are sharded on disk.

        Parameters:
        - index (int): Index of the sample to retrieve.

        Returns:
        - List[Any]: A list of preprocessed data samples. The last item in the list is the label.
        """

        # Combine all preprocessing attributes into a single loop
        combined_attributes = zip(
            self.preprocesses.online,
            self.mapping,
            self.preprocesses.preprocessing_type,
            self.preprocesses.in_memory
        )

        data = []
        for online, mapping, pre_process, in_mem in combined_attributes:
            if mapping[0] is None:
                continue
            else:
                data.append(get_processed_data(online, mapping, pre_process,
                                               in_mem, self.data.iloc[index][mapping[0]]))

        return data
