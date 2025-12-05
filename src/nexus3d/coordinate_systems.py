"""Create a coordinate system from NXtransformation groups"""

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
        transform_vec = partial(transform, matrix=transformation_matrix)  # type: ignore
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


# Get Euler angles from rotation matrix
# based on https://stackoverflow.com/questions/15022630/how-to-calculate-the-angle-from-rotation-matrix
def angles_from_matrix(tmatrix, quadrant=1):
    """
    Calculate Euler angles (chi (azimuth), beta (tilt), theta (polar)) from a rotation matrix.
    This produces the sample angles are defined in the ARPES coordinate system convention.
    https://arpes.readthedocs.io/en/latest/spectra.html#coordinate-conventions
    """

    if tmatrix[1][2] != 1 and tmatrix[1][2] != -1:
        beta1 = np.arcsin(-tmatrix[1][2])
        beta2 = np.pi - np.arcsin(-tmatrix[1][2])
        chi1 = np.arctan2(tmatrix[1][0] / np.cos(beta1), tmatrix[1][1] / np.cos(beta1))
        chi2 = np.arctan2(tmatrix[1][0] / np.cos(beta2), tmatrix[1][1] / np.cos(beta2))
        theta1 = np.arctan2(
            tmatrix[0][2] / np.cos(beta1), tmatrix[2][2] / np.cos(beta1)
        )
        theta2 = np.arctan2(
            tmatrix[0][2] / np.cos(beta2), tmatrix[2][2] / np.cos(beta2)
        )

        # IMPORTANT NOTE here, there is more than one solution but we choose the first for this case for simplicity !
        # You can insert your own domain logic here on how to handle both solutions appropriately (see the reference publication link for more info).
        if quadrant == 1:
            beta = beta1
            chi = chi1
            theta = theta1
        else:
            beta = beta2
            chi = chi2
            theta = theta2
    else:
        chi = 0  # anything (we default this to zero)
        if tmatrix[1][2] == -1:
            beta = np.pi / 2
            theta = chi + np.arctan2(tmatrix[0][1], tmatrix[0][0])
        else:
            beta = -np.pi / 2
            theta = -1 * chi + np.arctan2(tmatrix[0][1], tmatrix[0][0])

    # convert from radians to degrees
    chi = np.rad2deg(chi)
    beta = np.rad2deg(beta)
    theta = np.rad2deg(theta)

    return (chi, beta, theta)
