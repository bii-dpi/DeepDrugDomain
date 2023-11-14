from collections import defaultdict
from typing import Dict, Optional, List, Callable, Union
from rdkit import Chem
import torch
from deepdrugdomain.utils.exceptions import MissingRequiredParameterError
from ..factory import PreprocessorFactory
from ..base_preprocessor import BasePreprocessor
import numpy as np

AtomDictType = Dict[Union[str, tuple], int]
BondDictType = Dict[str, int]
FingerprintDictType = Dict[Union[int, tuple], int]


def create_atoms(mol, atom_dict):
    atoms = [a.GetSymbol() for a in mol.GetAtoms()]
    for a in mol.GetAromaticAtoms():
        i = a.GetIdx()
        atoms[i] = (atoms[i], 'aromatic')
    atoms = [atom_dict[a] for a in atoms]
    return np.array(atoms)


def create_ij_bond_dict(mol, bond_dict):
    ij_bond_dict = defaultdict(list)
    for b in mol.GetBonds():
        i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
        bond = bond_dict[str(b.GetBondType())]
        ij_bond_dict[i].append((j, bond))
        ij_bond_dict[j].append((i, bond))
    return ij_bond_dict


def extract_fingerprints(atoms, ij_bond_dict, radius, fingerprint_dict, edge_dict):
    if (len(atoms) == 1) or (radius == 0):
        fingerprints = [fingerprint_dict[a] for a in atoms]

    else:
        nodes = atoms
        ij_edge_dict = ij_bond_dict

        for _ in range(radius):
            fingerprints = []
            for i, j_edge in ij_edge_dict.items():
                neighbors = [(nodes[j], edge) for j, edge in j_edge]
                fingerprint = (nodes[i], tuple(sorted(neighbors)))
                fingerprints.append(fingerprint_dict[fingerprint])
            nodes = fingerprints

            _ij_edge_dict = defaultdict(lambda: [])
            for i, j_edge in ij_edge_dict.items():
                for j, edge in j_edge:
                    both_side = tuple(sorted((nodes[i], nodes[j])))
                    edge = edge_dict[(both_side, edge)]
                    _ij_edge_dict[i].append((j, edge))
            ij_edge_dict = _ij_edge_dict

    return np.array(fingerprints)


@PreprocessorFactory.register("smile_to_fingerprint")
class FingerprintFromSmilePreprocessor(BasePreprocessor):

    def __init__(self, method: str = 'rdkit',
                 radius: int = 2,
                 atom_dict: Optional[AtomDictType] = None,
                 bond_dict: Optional[BondDictType] = None,
                 fingerprint_dict: Optional[FingerprintDictType] = None,
                 edge_dict: Optional[Dict] = None,
                 consider_hydrogen: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.consider_hydrogen = consider_hydrogen
        self.method = method
        self.radius = radius
        self.atom_dict = atom_dict
        self.bond_dict = bond_dict
        self.fingerprint_dict = fingerprint_dict
        self.edge_dict = edge_dict

    def preprocess(self, smiles: str) -> Optional[torch.Tensor]:
        """
        Generate a molecular fingerprint based on a SMILES string.

        :param smiles: SMILES string of the molecule
        :param method: The fingerprinting method to use ('rdkit' or 'custom')
        :param radius: The radius for the fingerprint calculation (only for 'custom' method)
        :param consider_hydrogen: Flag to determine if hydrogen atoms should be considered
        :param custom_atom_dict: A dictionary mapping atom representation to integers (for 'custom' method)
        :param custom_bond_dict: A dictionary mapping bond types to integers (for 'custom' method)
        :param custom_fingerprint_dict: A dictionary for mapping fingerprints to indices (for 'custom' method)
        :return: A numpy array representing the fingerprint
        """
        # Convert SMILES to molecule
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None

        # Add hydrogens if the flag is set
        if self.consider_hydrogen:
            mol = Chem.AddHs(mol)

        # Use RDKit built-in method for fingerprinting
        if self.method == 'rdkit':
            fingerprints = Chem.RDKFingerprint(mol)

        elif self.method == 'ammvf':
            self.atom_dict = self.atom_dict if self.atom_dict is not None else defaultdict(
                lambda: len(self.atom_dict))
            self.bond_dict = self.bond_dict if self.bond_dict is not None else defaultdict(
                lambda: len(self.bond_dict))
            self.fingerprint_dict = self.fingerprint_dict if self.fingerprint_dict is not None else defaultdict(
                lambda: len(self.fingerprint_dict))
            self.edge_dict = self.edge_dict if self.edge_dict is not None else defaultdict(
                lambda: len(self.edge_dict))
            try:
                atoms = create_atoms(mol, self.atom_dict)
                ij_bond_dict = create_ij_bond_dict(mol, self.bond_dict)
                fingerprints = extract_fingerprints(
                    atoms, ij_bond_dict, self.radius, self.fingerprint_dict, self.edge_dict)

            except Exception as e:
                print(e)
                fingerprints = None

        else:
            raise ValueError(
                "Invalid method specified. Choose 'rdkit' or 'ammvf'.")

        fingerprints = torch.tensor(fingerprints, dtype=torch.long)
        return fingerprints