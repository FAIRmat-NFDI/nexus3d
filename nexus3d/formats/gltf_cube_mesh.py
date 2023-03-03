"""Functions for creating a gltf cube mesh file"""
from sys import version_info
from typing import Dict, List, Mapping, Union
import numpy as np
from numpy.typing import NDArray
import pygltflib

from nexus3d.formats.cube_mesh import create_cube_arrays, get_mesh_from_stl
from nexus3d.formats.interfaces import WriterInput
from nexus3d.matrix import translate

TransformationMatrix = Union[Dict[str, NDArray[np.float64]], NDArray[np.float64]]
TransformationMatrixDict = Mapping[str, TransformationMatrix]


def get_binary_blobs(indices: NDArray[np.uint8], vertices: NDArray[np.float32]):
    """Converts points and triangles arrays to binary blobs.

    Args:
        vertices (NDArray[np.float32]): The vertices array
        indices (NDArray[np.uint8]): The indices array

    Returns:
        (bytes, bytes): The vertices and indices binary blob
    """
    vertices_bin = vertices.flatten().tobytes()
    indices_bin = indices.tobytes()

    return indices_bin, vertices_bin


def set_data(
    gltf: pygltflib.GLTF2,
    indices_list: List[NDArray[np.uint8]],
    vertices_list: List[NDArray[np.float32]],
):
    """Writes all binary data related structures into the gltf object.
    This includes accessors, bufferViews and buffers.
    The accessors indices are the same as in the respective indices and vertices list.
    The indices_list and vertices_list must have the same length.

    Args:
        gltf (pygltflib.GLTF2): The gltf object into which to write the data.
        indices_list (List[NDArray[np.uint8]]): List containing arrays of indices.
        vertices_list (List[NDArray[np.float32]]): List containting array of vertices.
    """

    if len(indices_list) != len(vertices_list):
        raise ValueError("Indices list and vertices list must have the same length.")

    gltf_type = {
        "int8": pygltflib.BYTE,
        "uint8": pygltflib.UNSIGNED_BYTE,
        "int16": pygltflib.SHORT,
        "uint16": pygltflib.UNSIGNED_SHORT,
        "uint32": pygltflib.UNSIGNED_INT,
        "float32": pygltflib.FLOAT,
    }

    binary_data = b""
    offset = 0
    gltf.accesors = []
    gltf.bufferViews = []

    for i, (indices, vertices) in enumerate(zip(indices_list, vertices_list)):
        indices_bin, vertices_bin = get_binary_blobs(indices, vertices)

        gltf.accessors.append(
            pygltflib.Accessor(
                bufferView=2 * i,
                componentType=gltf_type[str(indices.dtype)],
                count=indices.size,
                type=pygltflib.SCALAR,
                max=[int(indices.max())],
                min=[int(indices.min())],
            )
        )

        gltf.accessors.append(
            pygltflib.Accessor(
                bufferView=2 * i + 1,
                componentType=gltf_type[str(vertices.dtype)],
                count=len(vertices),
                type=pygltflib.VEC3,
                max=vertices.max(axis=0).tolist(),
                min=vertices.min(axis=0).tolist(),
            )
        )

        gltf.bufferViews.append(
            pygltflib.BufferView(
                buffer=0,
                byteOffset=offset,
                byteLength=len(indices_bin),
                target=pygltflib.ELEMENT_ARRAY_BUFFER,
            )
        )

        fill_offset = offset + len(indices_bin) % len(vertices_bin)
        fill_offset_bin = b"\x00" * fill_offset

        gltf.bufferViews.append(
            pygltflib.BufferView(
                buffer=0,
                byteOffset=offset + len(indices_bin) + fill_offset,
                byteLength=len(vertices_bin),
                target=pygltflib.ARRAY_BUFFER,
            )
        )

        offset += len(indices_bin) + len(vertices_bin) + fill_offset
        binary_data += indices_bin + fill_offset_bin + vertices_bin

    gltf.buffers = [pygltflib.Buffer(byteLength=offset)]
    gltf.set_binary_blob(binary_data)


def clean_name(name: str, entry_name: str):
    """Cleans the name of a matrix path.

    Args:
        name (str): The name of the transformation path
        entry_name (str): The name of the current entry
    """

    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix) :]
        return text

    if version_info.minor < 9:
        return remove_prefix(
            remove_prefix(remove_prefix(name, "/entry/"), entry_name),
            "/transformations/",
        ).replace("/transformations", "")

    return (
        name.removeprefix("/entry/")
        .removeprefix(entry_name)
        .removeprefix("/transformations/")
        .replace("/transformations", "")
    )


def write_gltf_file(cli_input: WriterInput):
    """Writes a cube mesh from the transformation matrices to a gltf file.

    Args:
        filename (str): The filename to write to.
        transformation_matrices (TransformationMatrixDict): The transformation matrix dict.
        scale (float, optional): The scale of the cubes. Defaults to 0.1.
        show_beam (bool, optional): Whether to show the beam in the gltf file. Defaults to True.
    """

    def add_stl_shift(name: str, matrix: TransformationMatrix) -> TransformationMatrix:
        if name not in cli_input.config_dict:
            return matrix

        translations = np.zeros(3)
        if name in cli_input.config_dict:
            for i, axis in enumerate(["x", "y", "z"]):
                translations[i] = cli_input.config_dict[name].get(axis, 0)

        if isinstance(matrix, dict):
            matrix["stl_shift"] = matrix[next(reversed(matrix))] @ translate(
                translations
            )
            return matrix

        return matrix @ translate(translations)

    def append_nodes(mesh_indices: Dict[str, int]):
        for name, matrix in cli_input.transformation_matrices.items():
            children = []
            if isinstance(matrix, dict):
                for j, (cname, cmat) in enumerate(
                    add_stl_shift(name, matrix).items()  # type: ignore
                ):
                    gltf.nodes.append(
                        pygltflib.Node(
                            mesh=mesh_indices[name],
                            matrix=list(cmat.T.flat),
                            name=f"{j}-{clean_name(cname, name)}",
                        )
                    )
                    children.append(len(gltf.nodes) - 1)

            gltf.nodes.append(pygltflib.Node(mesh=mesh_indices[name], name=name))

            if children:
                gltf.nodes[-1].children = children
            else:
                gltf.nodes[-1].matrix = list(
                    add_stl_shift(name, matrix).T.flat  # type: ignore
                )

            gltf.scenes[gltf.scene].nodes.append(len(gltf.nodes) - 1)

    def append_mesh(mode: int = 4):
        gltf.meshes.append(
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=2 * len(indices) - 1),
                        indices=2 * len(indices) - 2,
                        mode=mode,
                    )
                ]
            ),
        )

    def create_meshs():
        mesh_indices = {}
        cube_index = None
        for name in cli_input.transformation_matrices:
            if name in cli_input.config_dict and "file" in cli_input.config_dict[name]:
                stl_indices, stl_vertices = get_mesh_from_stl(
                    cli_input.config_dict[name]["file"]
                )

                indices.append(stl_indices)
                vertices.append(stl_vertices)
                mesh_indices[name] = len(vertices) - 1
                append_mesh()
                continue

            if cube_index is None:
                cube_indices, cube_vertices = create_cube_arrays(cli_input.size / 2)
                indices.append(cube_indices)
                vertices.append(cube_vertices)
                cube_index = len(vertices) - 1
                append_mesh()
            mesh_indices[name] = cube_index

        return mesh_indices

    if cli_input.config_dict is None:
        cli_input.config_dict = {}

    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[])],
    )

    indices = []
    vertices = []
    mesh_indices = create_meshs()

    append_nodes(mesh_indices)

    if cli_input.show_beam:
        vertices.append(np.array([[0, 0, 0], [0, 0, -1]], dtype="float32"))
        indices.append(np.array([[0, 1]], dtype="uint8"))
        gltf.nodes.append(pygltflib.Node(mesh=len(indices) - 1, name="beam"))

        gltf.scenes[gltf.scene].nodes.append(len(gltf.nodes) - 1)

        append_mesh(mode=1)

    set_data(gltf, indices, vertices)

    gltf.save(cli_input.output)
