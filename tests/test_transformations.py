"""Test correct reading and reduction of transformations"""
from pathlib import Path

import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal
from pytest import mark, param
from scipy.spatial.transform import Rotation

from nexus3d.coordinate_systems import angle_between
from nexus3d.matrix import rotate, translate
from nexus3d.nexus_transformations import transformation_matrices_from

# pylint: disable=redefined-outer-name


def example_file_paths():
    """Get the transformation example file path."""
    path = Path(__file__).parent

    return [
        str(path / "data" / "transformation_example.h5"),
        str(path / "data" / "transformation_example_array.h5"),
    ]


def get_all_matrices():
    """Get the transformation matrixes from the example file."""
    transformation_matrices = []
    for example_file_path in example_file_paths():
        transformation_matrices.append(
            param(
                transformation_matrices_from(example_file_path, False),
                id=example_file_path.rsplit("/", 1)[-1],
            )
        )
    return transformation_matrices


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


@mark.parametrize("tmatrices", get_all_matrices())
def test_correct_chain_resolution_from_nexus(tmatrices):
    """The transformation chain is resolved to the correct matrix from a nexus file"""

    def get_manipulator_trafo():
        m_rot_x = rotate(np.deg2rad(-90), np.array([1, 0, 0]))
        m_rot_z = rotate(np.deg2rad(-25), np.array([0, 0, 1]))
        m_trans_z = translate(-0.32 * np.array([0, 0, 1]))

        return m_rot_x @ m_rot_z @ m_trans_z

    def get_sample_trafo():
        trans_x = translate(2.65e-3 * np.array([1, 0, 0]))
        trans_y = translate(-4.321e-3 * np.array([0, 1, 0]))
        trans_z = translate(34.82e-3 * np.array([0, 0, 1]))
        rot_tht = rotate(np.deg2rad(401.18), np.array([0, 0, 1]))
        rot_phi = rotate(np.deg2rad(2.5), np.array([0, 1, 0]))
        rot_omg = rotate(np.deg2rad(131.7), np.array([1, 0, 0]))
        corrected_phi = rotate(np.deg2rad(90), np.array([0, 1, 0]))

        return (
            get_manipulator_trafo()
            @ trans_x
            @ trans_y
            @ trans_z
            @ rot_tht
            @ rot_phi
            @ rot_omg
            @ corrected_phi
        )

    def get_analyser_trafo():
        a_rot_y = rotate(np.deg2rad(-115), np.array([0, 1, 0]))
        a_trans_z = translate(4e-3 * np.array([0, 0, 1]))

        return a_rot_y @ a_trans_z

    assert_array_almost_equal(
        tmatrices["instrument/manipulator"], get_manipulator_trafo()
    )
    assert_array_almost_equal(tmatrices["sample"], get_sample_trafo())

    assert_array_almost_equal(
        tmatrices["instrument/electronanalyser"], get_analyser_trafo()
    )


@mark.parametrize(
    "tmatrices, example_file_path", zip(get_all_matrices(), example_file_paths())
)
def test_full_chain_extraction(tmatrices, example_file_path):
    """Test the full chain extraction from the example file."""
    tmatrices_chain = transformation_matrices_from(example_file_path, False, True)

    assert len(tmatrices_chain["sample"]) == 10
    assert len(tmatrices_chain["instrument/manipulator"]) == 3
    assert len(tmatrices_chain["instrument/electronanalyser"]) == 2

    for entry, matrix in tmatrices.items():
        last_matrix = tmatrices_chain[entry][next(reversed(tmatrices_chain[entry]))]
        assert_array_almost_equal(matrix, last_matrix)


@mark.parametrize("tmatrices", get_all_matrices())
def test_angle_between(tmatrices):
    """Test if the angle between the sample z-axis and beam axis is calculated correctly"""
    transformed_z = (
        np.linalg.inv(tmatrices["instrument/electronanalyser"]) @ np.array([0, 0, 1, 0])
    )[:-1]

    assert_almost_equal(
        angle_between(transformed_z, np.array([0, 0, -1])) / np.pi * 180,
        65,
    )
