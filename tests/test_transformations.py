"""Test correct reading and reduction of transformations"""
import os
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_almost_equal
from scipy.spatial.transform import Rotation
from nexus3d.coordinate_systems import angle_between

from nexus3d.matrix import rotate
from nexus3d.nexus_transformations import transformation_matrices_from


def test_correct_rotation_matrix():
    """Checks the nexus rotation matrix"""
    angles = np.linspace(0, 360, 36)
    rotvecs = np.random.rand(36, 3)

    for angle, rotvec in zip(angles, rotvecs):
        rot_matrix = np.pad(
            Rotation.from_rotvec(angle * rotvec / np.linalg.norm(rotvec)).as_matrix(),
            ((0, 1), (0, 1)),
        )
        rot_matrix[-1, -1] = 1
        nexus_matrix = rotate(angle, rotvec, np.array([0, 0, 0]))

        assert_array_almost_equal(nexus_matrix, rot_matrix)


def test_correct_chain_resolution_from_nexus():
    """The transformation chain is resolved to the correct matrix from a nexus file"""


def test_angle_between():
    """Test if the angle between the sample z-axis and beam axis is calculated correctly"""
    path = os.getenv("PYTEST_CURRENT_TEST").rsplit("/", 1)[0]
    tmatrices = transformation_matrices_from(
        f"{path}/data/transformation_example.h5", False
    )
    transformed_z = (tmatrices["sample"] @ np.array([0, 0, 1, 0]))[:-1]

    assert_almost_equal(
        angle_between(transformed_z, np.array([0, 0, 1])) / np.pi * 180, 92.5
    )
