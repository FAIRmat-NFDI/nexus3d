"""Interfacies for function communication"""
from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Union
import numpy as np
from numpy.typing import NDArray

TransformationMatrixDict = Mapping[
    str, Union[Dict[str, NDArray[np.float64]], NDArray[np.float64]]
]


@dataclass
class WriterInput:
    """Inputs for the writer classes"""

    output: str
    transformation_matrices: TransformationMatrixDict
    size: float
    show_beam: bool = False
    config_dict: Optional[Dict[str, Dict[str, str]]] = None
    shape: str = "cone"
