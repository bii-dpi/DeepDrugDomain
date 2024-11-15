# DeepDrugDomain

DeepDrugDomain is a comprehensive Python toolkit aimed at simplifying and accelerating the process of drug-target interaction (DTI) and drug-target affinity (DTA) prediction using deep learning. With a flexible preprocessing pipeline and modular design, DeepDrugDomain supports innovative research and development in computational drug discovery.



## Features

DeepDrugDomain is built with a suite of powerful features designed to empower researchers in the field of computational drug discovery. Below are some of the core capabilities that make DeepDrugDomain an indispensable tool:

### Extensive Preprocessing Capabilities
- **Comprehensive Preparation Tools**: Streamline your data preparation with our extensive suite of preprocessing tools.
- **Support for Diverse Data**: Cater to a wide array of data formats prevalent in drug discovery, ensuring compatibility and ease of integration.

### Modular Design for Flexibility
- **Customizable Components**: Adapt the toolkit to meet your research needs with highly customizable components.
- **Simplified Model Creation**: Our modular design principle makes model creation and experimentation a straightforward process, saving time and reducing complexity.

### Stateful Evaluation Metrics
- **Consistent Performance Tracking**: Integrated metrics provide a consistent framework for tracking the performance of models.
- **Reproducibility and Accuracy**: These metrics are integral in ensuring the reproducibility of results and the accuracy of predictions.

### Custom Activation Functions
- **Integration of Novel Functions**: Introduce and integrate custom activation functions with ease to enhance your models.
- **Boost to Model Adaptability**: This feature allows models to be more adaptable and effective in handling complex drug discovery tasks.

### Comprehensive Task Support
- **Support for Core Tasks**: DeepDrugDomain comes with built-in support for key tasks such as drug-target interaction (DTI) and drug-target affinity (DTA).
- **Tailored for Drug Discovery**: The toolkit is crafted to meet the unique challenges faced in drug discovery, providing tailored support that drives innovation and progress.

### Facilitation of Model Augmentation
- **Decorator Design**: Augment models seamlessly with new inputs, enhancing the toolkit's utility and application scope.
- **Accuracy Improvement**: With just a line of code, improve the accuracy of existing models, streamlining the refinement process.

### Benchmarking
- **Built-in Benchmarks**: Leverage the pre-implemented benchmark models to gauge performance and validate outcomes.
- **Customizability**: Tailor the architecture of implemented models to meet specific research requirements, offering unparalleled flexibility.

### Expandability
- **Continuous Development**: Designed with the future in mind, DeepDrugDomain encourages and facilitates continuous expansion and incorporation of new features.
- **Custom Instantiation**: Choose to instantiate components in their default configuration or customize them for a more tailored experience.

### Ease of Use
- **Simplified Drug Discovery**: Remove the complexity from drug discovery tasks. DeepDrugDomain comes with a comprehensive suite of tools for easy preprocessing of any generic data.
- **User-Friendly Model Training**: Whether you're defining new models or utilizing pre-implemented ones, the process is straightforward and user-friendly, requiring minimal setup.

By integrating these advanced features, DeepDrugDomain stands out as a toolkit that not only meets the current demands of drug discovery but also adapts to its future challenges and opportunities.

## Installation
For now you can use this environments for usage and development,
```bash
conda create --name deepdrugdomain python=3.11
conda activate deepdrugdomain
pip install dgl -f https://data.dgl.ai/wheels/repo.html
conda install -c conda-forge rdkit
pip install git+https://github.com/yazdanimehdi/deepdrugdomain.git
```

## Quick Start

```python
import deepdrugdomain as ddd

# setting device on GPU if available, else CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = ModelFactory.create("attentionsitedti")
preprocesses = ddd.data.PreprocessingList(model.default_preprocess(
    "SMILES", "pdb_id", "Label"))
dataset = ddd.data.DatasetFactory.create(
    "human", file_paths="data/human/", preprocesses=preprocesses)
datasets = dataset(split_method="random_split",
                    frac=[0.8, 0.1, 0.1], seed=seed, sample=0.1)


collate_fn = model.collate

data_loader_train = DataLoader(
    datasets[0], batch_size=64, shuffle=True, num_workers=0, pin_memory=True, drop_last=True, collate_fn=collate_fn)

data_loader_val = DataLoader(datasets[1], drop_last=False, batch_size=32,
                                num_workers=4, pin_memory=False, collate_fn=collate_fn)
data_loader_test = DataLoader(datasets[2], drop_last=False, batch_size=32,
                                num_workers=4, pin_memory=False, collate_fn=collate_fn)
criterion = torch.nn.BCELoss()
optimizer = OptimizerFactory.create(
    "adam", model.parameters(), lr=1e-3, weight_decay=0.0)
scheduler = None
device = torch.device("cpu")
model.to(device)
train_evaluator = ddd.metrics.Evaluator(["accuracy_score"], threshold=0.5)
test_evaluator = ddd.metrics.Evaluator(
    ["accuracy_score", "f1_score", "auc", "precision_score", "recall_score"], threshold=0.5)
epochs = 3000
accum_iter = 1
print(model.evaluate(data_loader_val, device,
        criterion, evaluator=test_evaluator))
for epoch in range(epochs):
    print(f"Epoch {epoch}:")
    model.train_one_epoch(data_loader_train, device, criterion,
                            optimizer, num_epochs=200, scheduler=scheduler, evaluator=train_evaluator, grad_accum_steps=accum_iter)
    print(model.evaluate(data_loader_val, device,
                            criterion, evaluator=test_evaluator))

print(model.evaluate(data_loader_test, device,
                        criterion, evaluator=test_evaluator))
                        
```
## Examples

The [example](./examples/) folder contains a collection of scripts and notebooks demonstrating various capabilities of DeepDrugDomain. Below is an overview of what each example covers:

### Training Different Models

- [attentionsitedti.ipynb](./examples/attentionsitedti.ipynb): Brief explanation of training AttentionSiteDTI with custom configurations and model tampering in this Jupyter Notebook.

### Other Functionalities

## Supported Preprocessings

The following table lists the preprocessing methods supported by the package, detailing the data conversion, settings options, and the models that use them:

### Ligand Preprocessing Methods

| **Method**             | **Converts From** | **Converts To**    | **Settings Options**                                                                                                           | **Used in Models**                            |
|------------------------|-------------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| **smiles_to_encoding** | SMILES            | Encoding Tensor    | one_hot: bool, embedding_dim: Optional[int], max_sequence_length: Optional[int], replacement_dict: Dict[str, str], token_regex: Optional[str], from_set: Optional[Dict[str, int]] | DrugVQA, AttentionDTA                         |
| **smile_to_graph**     | SMILES            | Graph              | node_featurizer: Callable, edge_featurizer: Optional[Callable], consider_hydrogen: bool, fragment: bool, hops: int            | AMMVF, AttentionSiteDTI, FragXsiteDTI, CSDTI  |
| **smile_to_fingerprint** | SMILES          | Fingerprint        | method: str, Refer to [Supported Fingerprinting Methods](#supported-fingerprinting-methods) table for detailed settings.                    | AMMVF                                         |

For detailed information on fingerprinting methods, please see the [Supported Fingerprinting Methods](#supported-fingerprinting-methods) section.

#### Supported Fingerprinting Methods

| **Method Name** | **Description**                                                                                   | **Settings Options**                                                                                                                       |
|-----------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **RDKit**       | Converts SMILES to RDKit fingerprints, capturing molecular structure information.                | radius: Optional[int], nBits: Optional[int]                                                                                                |
| **Morgan**      | Generates circular fingerprints, representing the environment of each atom in a molecule.        | radius: Optional[int], nBits: Optional[int]                                                                                                |
| **Daylight**    | Traditional method to encode molecular features, focusing on specific substructure patterns.      | nBits: Optional[int]                                                                                                                       |
| **ErG**         | Extended reduced graph-based approach, emphasizing molecular topology.                            | nBits: Optional[int], atom_dict: Optional[AtomDictType], bond_dict: Optional[BondDictType]                                                 |
| **RDKit2D**     | Two-dimensional variant of RDKit, detailing planar molecular structures.                          | nBits: Optional[int], atom_dict: Optional[AtomDictType], bond_dict: Optional[BondDictType]                                                 |
| **PubChem**     | Utilizes PubChem's approach to fingerprinting, highlighting unique chemical structures.          | nBits: Optional[int]                                                                                                                       |
| **AMMVF**       | Custom fingerprinting method specific to the AMMVF model.                                         | num_finger: Optional[int], fingerprint_dict: Optional[FingerprintDictType], edge_dict: Optional[Dict]                                      |
| **Custom**      | Allows for user-defined fingerprinting techniques, adaptable to specific research requirements.  | custom_fingerprint: Optional[Callable], consider_hydrogen: bool                                                                            |

### Protein Preprocessing Methods

| **Method**                        | **Converts From**   | **Converts To**         | **Settings Options**                                                                                            | **Used in Models**              |
|-----------------------------------|---------------------|-------------------------|-----------------------------------------------------------------------------------------------------------------|---------------------------------|
| **contact_map_from_pdb**          | PDB ID              | Contact Map             | pdb_path: str, method: str, distance_threshold: float, normalize_distance: bool                                 | DrugVQA                         |
| **sequence_to_fingerprint**       | Protein Sequence    | Fingerprint             | method: str, Refer to [Supported Protein Fingerprinting Methods](#supported-protein-fingerprinting-methods) for settings.   | DrugVQA-Sequence                |
| **kmers**                          | Protein Sequence    | Kmers Encoded Tensor    | ngram: int, word_dict: Optional[dict], max_length: Optional[int]                                               | AMMVF, CSDTI                    |
| **protein_pockets_to_dgl_graph**  | PDB ID              | Binding Pocket Graph    | pdb_path: str, protein_size_limit: int                                                                          | AttentionSiteDTI, FragXsiteDTI  |
| **word2vec**                       | Protein Sequence    | Word2Vec Tensor         | model_path: str, vec_size: int, k: int, update_vocab: Optional[bool]                                           | AMMVF                           |
| **sequence_to_one_hot**           | Protein Sequence    | Encoding Tensor         | amino_acids: str, max_sequence_length: Optional[int], one_hot: bool                                            | AttentionDTA                    |
| **sequence_to_motif**             | Protein Sequence    | Motif Tensor            | ngram: int, word_dict: Optional[dict], max_length: Optional[int], one_hot: bool, number_of_combinations: Optional[int] | WideDTA                         |

For detailed information on protein fingerprinting methods, please see the [Supported Protein Fingerprinting Methods](#supported-protein-fingerprinting-methods) section.

#### Supported Protein Fingerprinting Methods

| **Method Name** | **Description**                                                                                   | **Settings Options**                                                                                                                       |
|-----------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **Quasi**       | A protein fingerprinting method that captures quasi-sequence information.                         | []                                                                                                      |
| **AAC**         | Encodes protein sequences based on amino acid composition.                                        | []                                                                                                      |
| **PAAC**        | Generates pseudo amino acid composition fingerprints for proteins.                               | []                                                                                                      |
| **CT**          | A method focusing on the composition, transition, and distribution of amino acids in sequences.  | []                                                                                                      |
| **Custom**      | Allows for user-defined protein fingerprinting techniques, adaptable to specific research needs. | custom settings as required                                                                                                               |

### Label Preprocessing Methods

| Method                | Converts From | Converts To    | Settings Options |
|-----------------------|---------------|----------------|------------------|
| **interaction_to_binary** | Binary        | Binary Tensor  | []               |
| **ic50_to_binary**        | IC50          | Binary         | threshold: float |
| **Kd_to_binary**          | Kd            | Binary         | threshold: float |
| **value_to_log**          | Float         | Log            | []               |


### `PreprocessingObject`

#### `attribute`
The `attribute` parameter specifies the key or column name in the input dataset that contains the data to be preprocessed.
- **Example Usage**: `attribute="SMILES"` means the preprocessing will be applied to the data in the "SMILES" column of the dataset.

#### `from_dtype`
This parameter defines the data type or format of the input data before preprocessing.
- **Example Usage**: `from_dtype="smile"` indicates that the input data is in SMILES (Simplified Molecular Input Line Entry System) format, a textual representation of chemical structures.

#### `to_dtype`
The `to_dtype` parameter specifies the desired data type or format after preprocessing.
- **Example Usage**: `to_dtype="graph"` implies that the preprocessing will convert the input data (in this case, SMILES format) into a graph representation, which is often used in molecular modeling and cheminformatics.

#### `preprocessing_settings`
This parameter is a dictionary that contains specific settings or options for the preprocessing step. It allows for customization of the preprocessing process based on the requirements of the model or the nature of the dataset.
- **Example Usage**: 

##### `in_memory` Flag
The `in_memory` flag controls whether the preprocessed data is stored entirely in the system's memory (RAM).
- **`True`**: Setting `in_memory` to `True` loads and stores the entire dataset in memory. This speeds up data retrieval during training but requires significant memory resources. It's ideal for datasets that can fit comfortably in RAM.
- **`False`**: Setting `in_memory` to `False` means the data is not stored in memory but processed and loaded during training iterations. This approach is more memory-efficient, suitable for large datasets, but can lead to slower data access times.

#### `online` Flag
The `online` flag indicates whether preprocessing is performed in real-time (online) or preprocessed once and stored.
- **`True`**: With `online` set to `True`, preprocessing occurs in real-time during each data access. This is beneficial for datasets requiring dynamic transformations during training.
- **`False`**: Setting `online` to `False` pre-processes and stores the data in its final form. This method is efficient for computationally expensive preprocessing steps on static datasets.

#### Usage Example
In DeepDrugDomain, `PreprocessingObject` can be configured with these flags to optimize data handling:

```python
import deepdrugdomain as ddd
from dgllife.utils import CanonicalAtomFeaturizer

feat = CanonicalAtomFeaturizer() 
preprocess_drug = ddd.data.PreprocessingObject(attribute="SMILES", from_dtype="smile", to_dtype="graph", preprocessing_settings={
                                               "fragment": False, "node_featurizer": feat}, in_memory=True, online=False)
```


## Supported Datasets

DeepDrugDomain provides support for a variety of datasets, each tailored for specific use cases in drug discovery. The table below details the datasets available:

| Dataset Name      | Description                                                              | Use Case             |
|-------------------|--------------------------------------------------------------------------|----------------------|
| **Celegans**          | Consists of chemical-genetic interaction data in C. elegans organisms.  | DTI                  |
| **Human**             | Encompasses human protein-target interaction datasets.                   | DTI                  |
| **DrugBankDTI**       | A comprehensive drug-target interaction dataset from DrugBank.           | DTI                  |
| **Kiba**              | Combines kinase inhibitor bioactivity data across multiple sources.      | DTA, DTI             |
| **Davis**             | Focuses on kinase inhibitor target affinity profiles.                    | DTA, DTI             |
| **IBM_BindingDB**     | Derived from BindingDB, focuses on binding affinity of drug-like molecules. | DTA, DTI           |
| **BindingDB**         | Contains measured binding affinities for protein-ligand complexes.       | DTA, DTI             |
| **DrugTargetCommon**  | A curated set of drug-target interactions from various databases.        | DTA, DTI             |
| **All TDC Datasets**  | Includes all datasets from the Therapeutics Data Commons (TDC).          | All drug discovery tasks |


### Supported Split Methods

All datasets listed above support the following split methods:
- k_fold 
- random_split
- cold_split
- scaffold_split

### Usage Example
```python
import deepdrugdomain as ddd

# Define PreprocessorObject
preprocess = [...]
preprocesses = ddd.data.PreprocessingList(preprocess)
# Load dataset
dataset = ddd.data.DatasetFactory.create("human", file_paths="data/human/", preprocesses=preprocesses) 
datasets = dataset(split_method="random_split", frac=[0.8, 0.1, 0.1], seed=4)
```

## Supported Models and Datasets
**Disclaimer**: This implementation of DeepDrugDomain is not an official version and may contain inaccuracies or differences compared to the original models. While efforts have been made to ensure reliability, the models provided may not perform at the same level as officially published versions and should be used with this understanding.

The following table showcases the models supported by our package and the datasets each model is compatible with:

| Model          | Supported Datasets          |
| -------------- | --------------------------- |
| AttentionSiteDTI         | DTI, DTA          |
| FragXsiteDTI         | DTI, DTA   |
| DrugVQA         | DTI, DTA                    |
| CSDTI     | DTI, DTA                            |
| AMMVF | DTI, DTA   |
| AttentionDTA| DTI, DTA    |
| DeepDTA| DTI, DTA|
| WideDTA|DTI, DTA   |
| GraphDTA| DTI, DTA|
| DGraphDTA| DTI, DTA|

**Contribution**: We are actively looking to add new models to the package. Feel free to add any model to the package and shoot a pull request!

## Documentation
For now please read the docstring inside the module for more information.

## Contributing
We welcome contributions to DeepDrugDomain! Please check out our [Contribution Guidelines](CONTRIBUTING.md) for more details on how to contribute.

## Citation
### BibTeX

```bibtex
@misc{my2024ddd,
  author = {Mehdi Yazdani-Jahromi},
  title = {From Data to Discovery: The DeepDrugDomain Framework for Predicting Drug-Target Interactions and Affinity},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  doi = {10.5281/zenodo.13974011},
  howpublished = {\url{https://github.com/yazdanimehdi/DeepDrugDomain}}
}
```

### Latest DOI
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13974011.svg)](https://doi.org/10.5281/zenodo.13974011)

