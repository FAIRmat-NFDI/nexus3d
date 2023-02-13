"""Functions for creating a cube mesh"""
import numpy as np
from stl import mesh

vertices = np.array(
    [
        [-1, -1, -1],
        [+1, -1, -1],
        [+1, +1, -1],
        [-1, +1, -1],
        [-1, -1, +1],
        [+1, -1, +1],
        [+1, +1, +1],
        [-1, +1, +1],
    ]
)

faces = np.array(
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
    ]
)


def create_cube_mesh(scale: float = 1.0):
    """Creates a cube mesh.

    Args:
        scale (float, optional): The scale of the cube mesh. Defaults to 1.0.

    Returns:
        stl.mesh: The cube mesh at the origin
    """
    scaled_vertices = vertices * scale

    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = scaled_vertices[face[j], :]

    return cube
