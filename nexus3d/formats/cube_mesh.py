"""Cube mesh utility functions (e.g. creating cube arrays)"""
import numpy as np


def create_cube_arrays(scale: float = 1):
    """Get cube arrays for creating the cubes.

    Args:
        scale (float, optional): The scale of the cubes. Defaults to 1.

    Returns:
        (np.ndarray, np.ndarray): The points and triangles array of the cube.
    """
    points = np.array(
        [
            [-1, -1, -1],
            [+1, -1, -1],
            [+1, +1, -1],
            [-1, +1, -1],
            [-1, -1, +1],
            [+1, -1, +1],
            [+1, +1, +1],
            [-1, +1, +1],
        ],
        dtype="float32",
    )
    triangles = np.array(
        [
            [0, 3, 1],
            [1, 3, 2],
            [0, 4, 7],
            [0, 7, 3],
            [4, 5, 6],
            [4, 6, 7],
            [5, 1, 2],
            [5, 2, 6],
            [2, 3, 6],
            [3, 7, 6],
            [0, 1, 5],
            [0, 5, 4],
        ],
        dtype="uint8",
    )

    return points * scale, triangles
