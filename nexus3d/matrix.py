"""Transformation matrices for nexus"""

from typing import Optional

import numpy as np
from numpy.linalg import norm
from numpy.typing import NDArray


def rotate(
    angle: float,
    axis: NDArray[np.float64],
    offset: Optional[NDArray[np.float64]] = None,
    left_handed: bool = False,
) -> NDArray[np.float64]:
    """Generates a 4D rotation matrix

    Returns:
        np.ndarray[(4, 4), float]: The 4D rotation matrix
    """
    if offset is None:
        offset = np.zeros(3)

    v_x, v_y, v_z = axis / norm(axis)
    cosa = np.cos(angle)
    cosa1 = 1 - cosa
    sina = np.sin(angle)

    if left_handed:
        return np.array(
            [
                [
                    cosa + v_x**2 * cosa1,
                    v_x * v_z * cosa1 + v_y * sina,
                    v_x * v_y * cosa1 - v_z * sina,
                    offset[0],
                ],
                [
                    v_z * v_x * cosa1 - v_y * sina,
                    cosa + v_z**2 * cosa1,
                    v_z * v_y * cosa1 + v_x * sina,
                    offset[2],
                ],
                [
                    v_y * v_x * cosa1 + v_z * sina,
                    v_y * v_z * cosa1 - v_x * sina,
                    cosa + v_y**2 * cosa1,
                    offset[1],
                ],
                [0, 0, 0, 1],
            ]
        )

    return np.array(
        [
            [
                cosa + v_x**2 * cosa1,
                v_x * v_y * cosa1 - v_z * sina,
                v_x * v_z * cosa1 + v_y * sina,
                offset[0],
            ],
            [
                v_y * v_x * cosa1 + v_z * sina,
                cosa + v_y**2 * cosa1,
                v_y * v_z * cosa1 - v_x * sina,
                offset[1],
            ],
            [
                v_z * v_x * cosa1 - v_y * sina,
                v_z * v_y * cosa1 + v_x * sina,
                cosa + v_z**2 * cosa1,
                offset[2],
            ],
            [0, 0, 0, 1],
        ]
    )


def rotate_z_onto_vec(
    vec: NDArray[np.float64], offset: Optional[NDArray[np.float64]] = None
) -> NDArray[np.float64]:
    """Generates a 4D rotation matrix to transform the z-axis
    from the reference frame onto the provided vector.

    Args:
        vec (NDArray[np.float64]): The vector to rotate onto.
        offset (Optional[NDArray[np.float64]], optional):
            An additional offset. Setting this to None ignores the offset. Defaults to None.

    Returns:
        np.ndarray[(4, 4), float]: The 4D rotation matrix
    """
    if offset is None:
        offset = np.zeros(3)

    return np.array(
        [
            [0, 0, vec[0], offset[0]],
            [0, 0, vec[1], offset[1]],
            [0, 0, vec[2], offset[2]],
            [0, 0, 0, 1],
        ]
    )


def translate(
    translation: NDArray[np.float64],
    offset: Optional[NDArray[np.float64]] = None,
    left_handed: bool = False,
) -> NDArray[np.float64]:
    """Generates a 4D translation matrix.

    Returns:
        np.ndarray[(4, 4), float]: The translation matrix.
    """
    trans = translation
    if offset is not None:
        trans += offset

    x, y, z = trans[0], trans[2], trans[1] if left_handed else trans
    return np.array(
        [
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1],
        ]
    )
