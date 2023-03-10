"""Cube mesh utility functions (e.g. creating cube arrays)"""
from typing import Optional
import numpy as np
from stl import mesh

from nexus3d.units import ureg


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


def get_mesh_from_stl(filename: str, unit: Optional[str] = None):
    """Reads a mesh as array of indices and vertices from a stl file.

    Args:
        filename (str): The stl filename
        unit (str): A pint interpretable unit which to interpret from the stl file.
    """
    stl_mesh = mesh.Mesh.from_file(filename)

    vertices, indices_lin = np.unique(
        stl_mesh.vectors.reshape([stl_mesh.vectors.size // 3, 3]),
        axis=0,
        return_inverse=True,
    )

    for dtype in ["uint8", "uint16", "uint32"]:
        if indices_lin.max() < np.iinfo(dtype).max:
            break

        if dtype == "uint32":
            raise ValueError(
                f"The stl model `{filename}` is too large to be converted into gltf."
            )

    indices = indices_lin.reshape([indices_lin.size // 3, 3]).astype(dtype)

    if unit is not None:
        scaling = ureg(f"1 {unit}").to("m").magnitude
        return indices, vertices * scaling
    return indices, vertices * scaling
