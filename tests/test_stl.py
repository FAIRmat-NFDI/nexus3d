"""Tests for stl file functions"""
import numpy as np
from numpy.testing import assert_array_almost_equal
from nexus3d.formats.cube_mesh import create_cube_arrays, get_mesh_from_stl
from nexus3d.formats.interfaces import WriterInput
from nexus3d.formats.stl_cube_mesh import write_stl_file


def test_cube_mesh_reconstruction(tmp_path):
    """Test whether a cube mesh is correctly reconstructed from a stl file"""
    test_file = tmp_path / "cube.stl"
    write_stl_file(WriterInput(test_file, {"test": np.identity(4)}, 2.0, False, {}))

    indices, vertices = create_cube_arrays()
    indices_file, vertices_file = get_mesh_from_stl(test_file)

    for i, face in enumerate(indices):
        for j in range(3):
            assert_array_almost_equal(
                vertices[face[j], :], vertices_file[indices_file[i][j], :]
            )
