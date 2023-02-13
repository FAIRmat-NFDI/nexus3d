"""Create a stl from NXtransformation groups"""
from sys import version_info
from os import path
from typing import Dict
import numpy as np
from numpy.typing import NDArray
import h5py
from pint import UnitRegistry
from stl import mesh
import click

from nexus3d.matrix import rotate, translate
from nexus3d.cube_mesh import create_cube_mesh

ureg = UnitRegistry()


def transformation_matrices_from(
    fname: str, include_process: bool
) -> Dict[str, NDArray[np.float64]]:
    """Reads all NXtransformations from a nexus file
    and creates a transformation matrix from them."""

    def get_transformation_matrix(h5file: h5py.File, entry: str):
        required_attrs = ["depends_on", "vector", "transformation_type", "units"]
        attrs = h5file[entry].attrs

        for req_attr in required_attrs:
            if req_attr not in attrs:
                raise ValueError(f"`{req_attr}` attribute not found in {entry}")

        if attrs["depends_on"] == ".":
            return np.identity(4)

        if "offset" in attrs and "offsets_units" not in attrs:
            raise ValueError(
                f"Found `offset` attribute in {entry} but no `offset_units` could be found."
            )
        offset = attrs.get("offset", np.zeros((3,)))
        offset_unit = ureg(attrs.get("offset_unit", ""))
        offset_si = (offset * offset_unit).to_base_units().magnitude

        vector = attrs["vector"]

        field = h5file[entry][()]
        if not isinstance(field, float):
            raise NotImplementedError("Only float fields are supported yet.")
        field_si = ureg(f"{field} {attrs['units']}").to_base_units().magnitude  # type: ignore

        if attrs["transformation_type"] == "translation":
            matrix = translate(field_si * vector, offset_si)
        elif attrs["transformation_type"] == "rotation":
            matrix = rotate(field_si, vector, offset_si)
        else:
            raise ValueError(
                f"Unknown transformation type `{attrs['transformation_type']}`"
            )

        if "/" in attrs["depends_on"]:
            return matrix @ get_transformation_matrix(h5file, attrs["depends_on"])

        return matrix @ get_transformation_matrix(
            h5file, f"{entry.rsplit('/', 1)[0]}/{attrs['depends_on']}"
        )

    def get_transformation_group_names(name: str, dataset: h5py.Dataset):
        if not include_process and name.startswith("entry/process"):
            return

        if "depends_on" in name:
            transformation_groups[
                name.rsplit("/", 1)[0].split("/", 1)[-1]
                if version_info.minor < 9
                else name.removesuffix("/depends_on").removeprefix("entry/")
            ] = dataset[()].decode("utf-8")

    transformation_groups: Dict[str, h5py.Dataset] = {}
    transformation_matrices = {}
    with h5py.File(fname, "r") as h5file:
        h5file.visititems(get_transformation_group_names)

        for name, transformation_group in transformation_groups.items():
            transformation_matrix = get_transformation_matrix(
                h5file, transformation_group
            )

            transformation_matrices[name] = transformation_matrix

    return transformation_matrices


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


@click.command()
@click.argument("file")
@click.option(
    "-o",
    "--output",
    default="experiment.stl",
    help="The filename to write to (default: experiment.stl).",
)
@click.option(
    "-s",
    "--size",
    default=0.1,
    type=float,
    help="The side length of a cube in meters. (default: 0.1 m).",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    type=bool,
    help="Force overwriting of output file.",
)
@click.option(
    "--include-process",
    is_flag=True,
    default=False,
    type=bool,
    help="Include transformations inside /entry/process",
)
def cli(file: str, output: str, force: bool, size: float, include_process: bool):
    """Create a stl from a nexus file via the command line"""

    if not path.exists(file):
        raise click.FileError(file, hint="File does not exist.")

    if not path.isfile(file):
        raise click.FileError(file, hint="Is not a file.")

    if not h5py.is_hdf5(file):
        raise click.FileError(file, hint="Not a valid HDF5 file.")

    if path.exists(output) and not force:
        raise click.FileError(output, hint="File already exists. Use -f to overwrite.")

    if size <= 0:
        raise click.BadOptionUsage(
            "size", f"Not a valid size: {size}. Size needs to be > 0."
        )

    scene = cube_meshs_from(
        transformation_matrices_from(file, include_process), size / 2
    )
    scene.save(output)
