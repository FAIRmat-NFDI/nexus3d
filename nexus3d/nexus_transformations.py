"""Create a stl from NXtransformation groups"""

import json
import os
from collections import OrderedDict
from dataclasses import dataclass
from os import path
from sys import version_info
from typing import Any, Callable, Dict, Mapping, Union

import click
import h5py
import numpy as np
import xarray as xr
from numpy.typing import NDArray

from nexus3d.formats.gltf_writer import write_gltf_file
from nexus3d.formats.interfaces import WriterInput
from nexus3d.formats.stl_writer import write_stl_file
from nexus3d.matrix import rotate, translate
from nexus3d.units import ureg

TransformationMatrixDict = Mapping[
    str, Union[Dict[str, NDArray[np.float64]], NDArray[np.float64]]
]

TransformationMatrixXarray = Mapping[str, Union[Dict[str, xr.DataArray], xr.DataArray]]


@dataclass
class Config:
    left_handed: bool = False


cs_config = Config()


def transformation_matrices_xarray(
    fname: str, include_process: bool = False, store_intermediate: bool = False
) -> TransformationMatrixXarray:
    """
    Reads the transformation matrices from a file and generates a dict of xarray's.
    Every field is a coordinate axis in the xarray.

    Args:
        fname (str): The hdf5/NeXus file from which to read the transformation matrices.
        include_process (bool, optional):
            Whether all /process entries should be included. Defaults to False.
        store_intermediate (bool, optional):
            If True the complete chain with all intermediate matrices are stored.
            Defaults to False.

    Returns:
        TransformationMatrixXarray:
            The resulting xarray containing the transformation matrices with the
            field values as coordiante axis.
    """

    def store_in_chain(entry: str, matrix: xr.DataArray):
        if store_intermediate:
            matrix_chain[entry] = matrix

        return matrix

    def get_transformation_matrix(h5file: h5py.File, entry: str):
        required_attrs = ["depends_on", "vector", "transformation_type", "units"]
        attrs = h5file[entry].attrs

        for req_attr in required_attrs:
            if req_attr not in attrs:
                raise ValueError(f"`{req_attr}` attribute not found in {entry}")

        if "offset" in attrs and "offsets_units" not in attrs:
            raise ValueError(
                f"Found `offset` attribute in {entry} but no `offset_units` could be found."
            )
        offset = attrs.get("offset", np.zeros((3,)))
        offset_unit = ureg(attrs.get("offset_unit", ""))
        offset_si = (offset * offset_unit).to_base_units().magnitude

        vector = attrs["vector"]

        field = h5file[entry][()]
        if isinstance(field, np.ndarray) and field.ndim == 1:
            matrices = xr.DataArray(
                np.zeros((len(field), 4, 4)),
                dims=[entry, "m1", "m2"],
                coords={entry: field},
            )
        elif isinstance(
            field, (int, float, np.int32, np.int64, np.float32, np.float64)
        ):
            matrices = xr.DataArray(
                np.zeros((1, 4, 4)), dims=[entry, "m1", "m2"], coords={entry: [field]}
            )
        else:
            raise NotImplementedError(
                "Only 0D and 1D numeric fields are supported yet, "
                f"but {entry}: {field} is {type(field)}"
            )

        for i, point in enumerate(matrices):
            field = point[entry].values.flat[0]
            field_si = ureg(f"{field} {attrs['units']}").to_base_units().magnitude  # type: ignore

            if attrs["transformation_type"] == "translation":
                matrices[i] = translate(
                    field_si * vector, offset_si, left_handed=cs_config.left_handed
                )
            elif attrs["transformation_type"] == "rotation":
                matrices[i] = rotate(
                    field_si, vector, offset_si, left_handed=cs_config.left_handed
                )
            else:
                raise ValueError(
                    f"Unknown transformation type `{attrs['transformation_type']}`"
                )

        if attrs["depends_on"] == ".":
            return store_in_chain(entry, matrices)

        if "/" in attrs["depends_on"]:
            return store_in_chain(
                entry,
                xr.apply_ufunc(
                    np.matmul,
                    get_transformation_matrix(h5file, attrs["depends_on"]),
                    matrices,
                    input_core_dims=[["m1", "m2"], ["m1", "m2"]],
                    output_core_dims=[["m1", "m2"]],
                    vectorize=True,
                ),
            )

        return store_in_chain(
            entry,
            xr.apply_ufunc(
                np.matmul,
                get_transformation_matrix(
                    h5file, f"{entry.rsplit('/', 1)[0]}/{attrs['depends_on']}"
                ),
                matrices,
                input_core_dims=[["m1", "m2"], ["m1", "m2"]],
                output_core_dims=[["m1", "m2"]],
                vectorize=True,
            ),
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
            if store_intermediate:
                matrix_chain: Dict[str, xr.DataArray] = OrderedDict()

            if "/" in transformation_group and not transformation_group.startswith("/"):
                transformation_group = f"{name}/{transformation_group}"

            transformation_matrix = get_transformation_matrix(
                h5file, transformation_group
            )

            transformation_matrices[name] = (
                matrix_chain if store_intermediate else transformation_matrix
            )

    return transformation_matrices


def transformation_matrices_from(
    fname: str, include_process: bool, store_intermediate: bool = False
) -> TransformationMatrixDict:
    """
    Reads all NXtransformations from a nexus file
    and creates a transformation matrix from them.
    """
    tmatrices = transformation_matrices_xarray(
        fname, include_process, store_intermediate
    )

    transformation_matrices_flat: Dict[Any, Any] = {}
    for entry, value in tmatrices.items():
        if isinstance(value, dict):
            transformation_matrices_flat[entry] = {}
            for subentry in value:
                transformation_matrices_flat[entry][subentry] = (
                    value[subentry].values.flat[:16].reshape(4, 4)
                )
            continue
        transformation_matrices_flat[entry] = value.values.flat[:16].reshape(4, 4)

    return transformation_matrices_flat


def apply_blender_transform(
    transformations: TransformationMatrixDict,
) -> TransformationMatrixDict:
    """Applyes a transformation to align the CS in blender."""
    blender_rot = rotate(np.deg2rad(-90), np.array([1, 0, 0]))

    for key, val in transformations.items():
        if isinstance(val, dict):
            transformations[key] = apply_blender_transform(val)  # type: ignore
        else:
            transformations[key] = blender_rot @ val  # type: ignore

    return transformations


@click.command()
@click.argument("file")
@click.option(
    "-o",
    "--output",
    default="experiment.glb",
    help="The filename to write to.",
    show_default=True,
)
@click.option(
    "-c",
    "--config",
    default="",
    help="Config file to load stl drawings into the final output",
)
@click.option(
    "-s",
    "--size",
    default=0.1,
    type=float,
    help="The side length of a cube in meters.",
    show_default=True,
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
@click.option(
    "--store-intermediate",
    is_flag=True,
    default=False,
    type=bool,
    help=(
        "Store the intermediate matrices in gltf child nodes. "
        "Only applicable for gltf or glb files."
    ),
)
@click.option(
    "--shape",
    default="cone",
    type=click.Choice(["cone", "cube"]),
    help=(
        "The shape to write into the gltf file. Only applicable for gltf or glb files. "
    ),
    show_default=True,
)
@click.option(
    "--blender",
    is_flag=True,
    default=False,
    type=bool,
    help=(
        "Rotates the coordinate system by 90 degree around the x-axis. "
        "This maps the axes correctly to blender."
    ),
)
@click.option(
    "-l",
    "--left-handed",
    is_flag=True,
    default=False,
    type=bool,
    help=("Applies transformations left-handedly."),
)
def cli(  # pylint: disable=too-many-arguments
    file: str,
    config: str,
    output: str,
    force: bool,
    size: float,
    include_process: bool,
    store_intermediate: bool,
    blender: bool,
    left_handed: bool,
    shape: str,
):
    """
    Create a glb/gltf or stl from a nexus file via the command line.
    The actual file format is chosen from the
    file ending of the output file (default: experiment.glb).
    """

    if not path.exists(file):
        raise click.FileError(file, hint=f"File `{file}` does not exist.")

    if not path.isfile(file):
        raise click.FileError(file, hint=f"`{file}` is not a file.")

    if not h5py.is_hdf5(file):
        raise click.FileError(file, hint=f"`{file}` is not a valid HDF5 file.")

    if path.exists(output) and not force:
        raise click.FileError(
            output, hint=f"File `{output}` already exists. Use -f to overwrite."
        )

    file_format = os.path.splitext(output)[1]
    if file_format not in [".stl", ".gltf", ".glb"]:
        raise click.UsageError(
            message=f"Unsupported file format {file_format} in output file `{output}`"
        )

    if config and (not path.exists(config) or not path.isfile(config)):
        raise click.FileError(
            file, hint=f"Config file `{config}` does not exist or is not valid."
        )

    if config and os.path.splitext(config)[1] != ".json":
        raise click.FileError(file, hint=f"Config file `{config}` must be a json file.")

    if size <= 0:
        raise click.BadOptionUsage(
            "size", f"Not a valid size: {size}. Size needs to be > 0."
        )

    def format_not_implemented(cli_input: WriterInput):
        raise NotImplementedError(
            f"Cannot write to format {file_format} for output file {cli_input.output}"
        )

    config.left_handed = left_handed

    config_dict = {}
    if config:
        with open(config, "r", encoding="utf-8") as json_file:
            config_dict = json.load(json_file)

    format_map: Dict[str, Callable[[WriterInput], None]] = {
        ".stl": write_stl_file,
        ".gltf": write_gltf_file,
        ".glb": write_gltf_file,
    }

    transformation_matrices = transformation_matrices_from(
        file, include_process, store_intermediate
    )
    if blender:
        transformation_matrices = apply_blender_transform(transformation_matrices)

    format_map.get(file_format, format_not_implemented)(
        WriterInput(
            output=output,
            transformation_matrices=transformation_matrices,
            size=size,
            show_beam=True,
            beam_blender=blender,
            config_dict=config_dict,
            shape=shape,
        )
    )
