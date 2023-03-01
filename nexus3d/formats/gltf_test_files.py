"""Creates test files for rotation and translation for reference."""
import numpy as np
from nexus3d.formats.gltf_cube_mesh import write_gltf_file
from nexus3d.matrix import rotate, translate


def create_rot_test_file(angle: float = 20, gltf: bool = False):
    """Creates a rotation test file containing rotation around all three coordinate axes."""
    rot_vecs = {
        f"rot_x_{angle}": np.array([1, 0, 0]),
        f"rot_y_{angle}": np.array([0, 1, 0]),
        f"rot_z_{angle}": np.array([0, 0, 1]),
    }

    rotation_matrices = {}
    for name, rot_vec in rot_vecs.items():
        rotation_matrices[name] = rotate(np.deg2rad(angle), rot_vec)

    write_gltf_file("rot.gltf" if gltf else "rot.glb", rotation_matrices, 0.1)


def create_trans_test_file(distance: float = 0.1, gltf: bool = False):
    """Creates a translation test file containing translations along all three coordinate axes."""
    trans_matrices = {
        f"trans_x_{distance}": translate(np.array([distance, 0, 0])),
        f"trans_y_{distance}": translate(np.array([0, distance, 0])),
        f"trans_z_{distance}": translate(np.array([0, 0, distance])),
    }

    write_gltf_file("trans.gltf" if gltf else "trans.glb", trans_matrices, 0.1)


def create_test_files(gltf: bool = False):
    """Creates a translation and a rotation test file."""
    create_trans_test_file(gltf=gltf)
    create_rot_test_file(gltf=gltf)
