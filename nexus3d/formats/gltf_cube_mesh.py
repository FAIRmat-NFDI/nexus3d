"""Functions for creating a gltf cube mesh file"""
from typing import Dict
import numpy as np
from numpy.typing import NDArray
import pygltflib


def get_cube_arrays(scale: float = 1):
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


def get_binary_blobs(vertices: NDArray[np.float32], indices: NDArray[np.uint8]):
    """Converts points and triangles arrays to binary blobs.

    Args:
        vertices (NDArray[np.float32]): The vertices array
        indices (NDArray[np.uint8]): The indices array

    Returns:
        (bytes, bytes): The vertices and indices binary blob
    """
    bin_vertices = vertices.flatten().tobytes()
    bin_indices = indices.tobytes()

    return bin_vertices, bin_indices


def write_gltf_file(
    filename: str,
    transformation_matrices: Dict[str, NDArray[np.float64]],
    scale: float = 0.1,
    show_beam: bool = True,
):
    """Writes a cube mesh from the transformation matrices to a gltf file.

    Args:
        filename (str): The filename to write to.
        transformation_matrices (Dict[str, NDArray[np.float64]]): The transformation matrix dict.
        scale (float, optional): The scale of the cubes. Defaults to 0.1.
        show_beam (bool, optional): Whether to show the beam in the gltf file. Defaults to True.
    """
    points, triangles = get_cube_arrays(scale / 2)
    points_binary_blob, triangles_binary_blob = get_binary_blobs(points, triangles)

    nodes = []
    for matrix in transformation_matrices.values():
        nodes.append(pygltflib.Node(mesh=0, matrix=list(matrix.T.flat)))

    nodes.append(pygltflib.Node(mesh=1))

    lines = np.array([[0, 0, 0], [0, 0, -1]], dtype="float32")
    indices = np.array([[0, 1]], dtype="uint8")
    lines_binary, indices_binary = get_binary_blobs(lines, indices)

    # mesh primitive modes
    # ◦ 0 POINTS
    # ◦ 1 LINES
    # ◦ 2 LINE_LOOP
    # ◦ 3 LINE_STRIP
    # ◦ 4 TRIANGLES
    # ◦ 5 TRIANGLE_STRIP ◦ 6 TRIANGLE_FAN


    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=nodes,
        meshes=[
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=1), indices=0
                    )
                ]
            ),
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=3), indices=2, mode=1,
                    )
                ]
            )
        ],
        accessors=[
            pygltflib.Accessor(
                bufferView=0,
                componentType=pygltflib.UNSIGNED_BYTE,
                count=triangles.size,
                type=pygltflib.SCALAR,
                max=[int(triangles.max())],
                min=[int(triangles.min())],
            ),
            pygltflib.Accessor(
                bufferView=1,
                componentType=pygltflib.FLOAT,
                count=len(points),
                type=pygltflib.VEC3,
                max=points.max(axis=0).tolist(),
                min=points.min(axis=0).tolist(),
            ),
            pygltflib.Accessor(
                bufferView=2,
                componentType=pygltflib.UNSIGNED_BYTE,
                count=indices.size,
                type=pygltflib.SCALAR,
                max=[int(indices.max())],
                min=[int(indices.min())],
            ),
            pygltflib.Accessor(
                bufferView=3,
                componentType=pygltflib.FLOAT,
                count=len(lines),
                type=pygltflib.VEC3,
                max=lines.max(axis=0).tolist(),
                min=lines.min(axis=0).tolist(),
            ),
        ],
        bufferViews=[
            pygltflib.BufferView(
                buffer=0,
                byteLength=len(triangles_binary_blob),
                target=pygltflib.ELEMENT_ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer=0,
                byteOffset=len(triangles_binary_blob),
                byteLength=len(points_binary_blob),
                target=pygltflib.ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer=0,
                byteOffset=len(triangles_binary_blob)+len(points_binary_blob),
                byteLength=len(indices_binary),
                target=pygltflib.ELEMENT_ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer=0,
                byteOffset=len(triangles_binary_blob)+len(points_binary_blob)+len(indices_binary),
                byteLength=len(lines_binary),
                target=pygltflib.ARRAY_BUFFER,
            ),
        ],
        buffers=[
            pygltflib.Buffer(
                byteLength=(
                    len(triangles_binary_blob)+len(points_binary_blob)
                    +len(indices_binary)+len(lines_binary)
                )
            ),
        ],
    )
    gltf.set_binary_blob(triangles_binary_blob + points_binary_blob + indices_binary + lines_binary)

    gltf.save(filename)
