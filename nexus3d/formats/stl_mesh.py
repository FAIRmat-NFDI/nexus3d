"""Functions for creating a cube mesh"""
from typing import Dict
import numpy as np
from numpy.typing import NDArray
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


def cube_meshs_from(
    transformation_matrices: Dict[str, NDArray[np.float64]], scale: float = 0.1
) -> mesh.Mesh:
    """Creates a composed cube mesh for a dict of transformation matrices.

    Args:
        transformation_matrices (Dict[str, np.ndarray[): The transformation matrix dict.
        scale (float): The scale of the cubes. Defaults to 0.1.

    Returns:
        mesh: The composed mesh containing a cube for each transformation matrix.
    """
    # pylint: disable=redefined-outer-name
    scene = None
    for transformation_matrix in transformation_matrices.values():
        cube = create_cube_mesh(scale)
        cube.transform(transformation_matrix)

        if scene is None:
            scene = cube.data
            continue
        scene = np.concatenate((scene, cube.data))

    return mesh.Mesh(scene)


def write_file(
    filename: str,
    transformation_matrices: Dict[str, NDArray[np.float64]],
    scale: float = 0.1,
):
    """Writes a cube mesh from the transformation matrices to a stl file.

    Args:
        filename (str): _description_
        transformation_matrices (Dict[str, NDArray[np.float64]]): The transformation matrix dict.
        scale (float, optional): The scale of the cubes. Defaults to 0.1.
    """
    scene = cube_meshs_from(transformation_matrices, scale / 2)
    scene.save(filename)
