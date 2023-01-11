"""Create a coordiante system from NXtransformation groups"""
from dataclasses import dataclass
from functools import partial
from typing import Dict
import numpy as np

from nexus2stl.nexus_transformations import transformation_matrices_from


@dataclass
class CoordinateSystem:
    """Represents a 3D coordinate system with its origin and axes."""

    origin: np.ndarray[(3,), float]
    x_axis: np.ndarray[(3,), float]
    y_axis: np.ndarray[(3,), float]
    z_axis: np.ndarray[(3,), float]


def coord_systems_from(fname: str) -> Dict[str, CoordinateSystem]:
    """Read all NXtransformations coordinate systems from the nexus file."""

    def transform(
        vector: np.ndarray[(4,), float], matrix: np.ndarray[(4, 4), float]
    ) -> np.ndarray[(3,), float]:
        return (matrix @ vector.T)[:-1]

    transformation_matrices = transformation_matrices_from(fname)

    coordinate_systems = {}

    for name, transformation_matrix in transformation_matrices.items():
        transform_vec = partial(transform, matrix=transformation_matrix)
        coordinate_systems[name] = CoordinateSystem(
            origin=transform_vec(np.array([0, 0, 0, 1])),
            x_axis=transform_vec(np.array([1, 0, 0, 0])),
            y_axis=transform_vec(np.array([0, 1, 0, 0])),
            z_axis=transform_vec(np.array([0, 0, 1, 0])),
        )

    return coordinate_systems
