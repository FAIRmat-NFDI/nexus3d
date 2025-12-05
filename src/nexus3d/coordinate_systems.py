"""Create a coordiante system from NXtransformation groups"""
from dataclasses import dataclass
from functools import partial
from typing import Dict

import numpy as np
from numpy.typing import NDArray

from nexus3d.nexus_transformations import transformation_matrices_from


@dataclass
class CoordinateSystem:
    """Represents a 3D coordinate system with its origin and axes."""

    origin: NDArray[np.float64]
    x_axis: NDArray[np.float64]
    y_axis: NDArray[np.float64]
    z_axis: NDArray[np.float64]


def coord_systems_from(
    fname: str, include_process: bool = False
) -> Dict[str, CoordinateSystem]:
    """Read all NXtransformations coordinate systems from the nexus file."""

    def transform(
        vector: NDArray[np.float64], matrix: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        return (matrix @ vector.T)[:-1]

    transformation_matrices = transformation_matrices_from(fname, include_process)

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


def unit_vector(vec: NDArray[np.float64]):
    """Calculates an unit vector"""
    return vec / np.linalg.norm(vec)


def angle_between(vec1: NDArray[np.float64], vec2: NDArray[np.float64]):
    """Calculate the angle between two vectors"""
    uvec1 = unit_vector(vec1)
    uvec2 = unit_vector(vec2)
    return np.arccos(np.clip(np.dot(uvec1, uvec2), -1, 1))
