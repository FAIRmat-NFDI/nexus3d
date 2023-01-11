"""Transformation matrices for nexus"""
import numpy as np
from numpy.linalg import norm


def rotate(
    angle: float, axis: np.ndarray[(3,), float], offset: np.ndarray[(3,), float]
) -> np.ndarray[(4, 4), float]:
    """Generates a 4D rotation matrix

    Returns:
        np.ndarray[(4, 4), float]: The 4D rotation matrix
    """
    v_x, v_y, v_z = axis / norm(axis)
    cosa = np.cos(angle)
    cosa1 = 1 - cosa
    sina = np.sin(angle)

    rot_matrix = np.array(
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

    return rot_matrix


def translate(
    translation: np.ndarray[(3,), float], offset: np.ndarray[(3,), float]
) -> np.ndarray[(4, 4), float]:
    """Generation a 4D translation matrix.

    Returns:
        np.ndarray[(4, 4), float]: The translation matrix.
    """
    trans = translation + offset
    return np.array(
        [
            [1, 0, 0, trans[0]],
            [0, 1, 0, trans[1]],
            [0, 0, 1, trans[2]],
            [0, 0, 0, 1],
        ]
    )
