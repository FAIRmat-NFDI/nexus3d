"""Test correct reading and reduction of transformations"""
import os
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_almost_equal
from scipy.spatial.transform import Rotation
from nexus3d.coordinate_systems import angle_between

from nexus3d.matrix import rotate, translate
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

    def get_manipulator_trafo():
        m_rot_x = rotate(np.deg2rad(-90), np.array([1, 0, 0]))
        m_rot_z = rotate(np.deg2rad(-25), np.array([0, 0, 1]))
        m_trans_z = translate(-0.32 * np.array([0, 0, 1]))

        return m_trans_z @ m_rot_z @ m_rot_x

    def get_sample_trafo():
        trans_x = translate(2.65e-3 * np.array([1, 0, 0]))
        trans_y = translate(-4.321e-3 * np.array([0, 1, 0]))
        trans_z = translate(34.82e-3 * np.array([0, 0, 1]))
        rot_tht = rotate(np.deg2rad(401.18), np.array([0, 0, 1]))
        rot_phi = rotate(np.deg2rad(2.5), np.array([0, 1, 0]))
        rot_omg = rotate(np.deg2rad(131.7), np.array([1, 0, 0]))
        corrected_phi = rotate(np.deg2rad(90), np.array([0, 1, 0]))

        return (
            corrected_phi
            @ rot_omg
            @ rot_phi
            @ rot_tht
            @ trans_z
            @ trans_y
            @ trans_x
            @ get_manipulator_trafo()
        )

    def get_analyser_trafo():
        a_rot_y = rotate(np.deg2rad(-115), np.array([0, 1, 0]))
        a_trans_z = translate(4e-3 * np.array([0, 0, 1]))

        return a_trans_z @ a_rot_y

    path = os.getenv("PYTEST_CURRENT_TEST").rsplit("/", 1)[0]
    tmatrices = transformation_matrices_from(
        f"{path}/data/transformation_example.h5", False
    )

    assert_array_almost_equal(
        tmatrices["instrument/manipulator"], get_manipulator_trafo()
    )
    assert_array_almost_equal(tmatrices["sample"], get_sample_trafo())

    assert_array_almost_equal(
        tmatrices["instrument/electronanalyser"], get_analyser_trafo()
    )


def test_angle_between():
    """Test if the angle between the sample z-axis and beam axis is calculated correctly"""
    path = os.getenv("PYTEST_CURRENT_TEST").rsplit("/", 1)[0]
    tmatrices = transformation_matrices_from(
        f"{path}/data/transformation_example.h5", False
    )
    transformed_z = (
        np.linalg.inv(tmatrices["instrument/electronanalyser"]) @ np.array([0, 0, 1, 0])
    )[:-1]

    assert_almost_equal(
        angle_between(transformed_z, np.array([0, 0, -1])) / np.pi * 180,
        65,
    )
