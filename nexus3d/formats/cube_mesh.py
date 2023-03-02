"""Cube mesh utility functions (e.g. creating cube arrays)"""
import numpy as np
from stl import mesh


def create_cube_arrays(scale: float = 1):
    """Get cube arrays for creating the cubes.

    Args:
        scale (float, optional): The scale of the cubes. Defaults to 1.

    Returns:
        (np.ndarray, np.ndarray): The points and triangles array of the cube.
    """
    vertices = np.array(
        [
            [-0.5, -1, -2],
            [+0.5, -1, -2],
            [+0.5, +1, -2],
            [-0.5, +1, -2],
            [-0.5, -1, +2],
            [+0.5, -1, +2],
            [+0.5, +1, +2],
            [-0.5, +1, +2],
        ],
        dtype="float32",
    )
    indices = np.array(
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

    return indices, vertices * scale


def get_mesh_from_stl(filename: str):
    """Reads a mesh as array of indices and vertices from a stl file.

    Args:
        filename (str): The stl filename
    """
    stl_mesh = mesh.Mesh.from_file(filename)

    vertices = np.unique(
        stl_mesh.vectors.reshape([stl_mesh.vectors.size // 3, 3]), axis=0
    )

    vertex_groups = stl_mesh.vectors.reshape([stl_mesh.vectors.size // 9, 3, 3])

    indices = np.zeros((len(vertex_groups), 3), dtype="uint8")
    for i, group in enumerate(vertex_groups):
        for j, vertex in enumerate(group):
            indices[i][j] = np.argwhere(np.all(vertices == vertex, axis=1))[0][0]

    return indices, vertices
