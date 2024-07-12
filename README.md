![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nexus3d)
[![PyPI](https://img.shields.io/pypi/v/nexus3d)](https://pypi.org/project/nexus3d/)
[![Pytest](https://github.com/FAIRmat-NFDI/nexus3d/actions/workflows/pytest.yml/badge.svg)](https://github.com/FAIRmat-NFDI/nexus3d/actions/workflows/pytest.yml)

# Scope

This is a project for reading out NXtransformation matrices from nexus files and
visualizing them by creating a 3D representation file ([stl](<https://en.wikipedia.org/wiki/STL_(file_format)>) or [gltf/glb](https://en.wikipedia.org/wiki/GlTF) - we recommend using `glb`) which may be imported into 3D visualization software (e.g. blender). It is possible to load CAD drawings from stl files to visualize your experiment with it. For glb files you can easily visualize it in the web with three.js (see the [example](https://github.com/FAIRmat-NFDI/nexus3d/tree/main/examples/threejs))

# Install

The easiest way to install is with pip

```
pip install nexus3d
```

or

```
pip install git+https://github.com/domna/nexus3d.git
```

for the latest development install.

If you want to keep to source code or use a development install clone the repostitory

```
git clone https://github.com/domna/nexus3d.git
cd nexus3d
```

and install with

```
pip install .
```

from the cloned git repository or add an optional `-e` to install it in development mode.

# Usage

Execute

```
nexus3d nexus_file.nxs
```

on your nexus file to generate an output file `experiment.glb`.
The usage of the command is as follows:

```
Usage: nexus3d [OPTIONS] FILE

  Create a glb/gltf or stl from a nexus file via the command line. The actual
  file format is chosen from the file ending of the output file (default:
  experiment.glb).

Options:
  -o, --output TEXT     The filename to write to.  [default: experiment.glb]
  -c, --config TEXT     Config file to load stl drawings into the final output
  -s, --size FLOAT      The side length of a cube in meters.  [default: 0.1]
  -f, --force           Force overwriting of output file.
  --include-process     Include transformations inside /entry/process
  --store-intermediate  Store the intermediate matrices in gltf child nodes.
                        Only applicable for gltf or glb files.
  --shape [cone|cube]   The shape to write into the gltf file. Only applicable
                        for gltf or glb files.   [default: cone]
  --blender             Rotates the coordinate system by 90 degree around the
                        x-axis. This maps the axes correctly to blender.
  -l, --left-handed     Applies transformations left-handedly.
  --help                Show this message and exit.
```

The optional config file in json format can be used to load stl files for the different objects, it should be according to the following format:

```json
{
  "instrument/my_fancy_instrument": {
    "file": "my_fancy_instrument.stl",
    "x": 5,
    "y": 10,
    "z": 3
  },
  "sample": {
    "file": "sample_holder.stl",
    "z": 3,
    "rot_x": 90,
    "unit": "mm"
  },
  "instrument/detector": {
    "file": "my_detector.stl",
    "unit": "inch"
  }
}
```

The json keys have to be named after their respective group containing a NXtransformation without leading `/entry/`.
The `file` attribute points to the stl file to be loaded.
Additionally, three keys (`x`, `y`, `z`) for translation (in meters) and three keys (`rot_x`, `rot_y`, `rot_z`) for rotation (in degrees) may be provided to introduce an additional shift and rotation of the stl drawing relative to
the coordinate frame from the nexus file. This is to account for any drawing offsets relative to the point denoted in the
nexus transformations. The shifts are introduced in the coordinate frame of the entry.
The rotations are applied first and then the object is translated.
Rotation are applied first `x`, second `y` and last `z`.
The full chain is therefore
$$T  R_z  R_y  R_x  v$$
, applied to the vector `v` in the coordinate frame of the entry.
To account for different units in the stl files a unit field may be provided.
The unit needs to be [pint](https://pint.readthedocs.io) convertible to meter.
If the unit field is not given meter is taken as default unit.

# Using with blender

The exported glb or gltf files can be directly used with blender to have a proper visualization available.
However, please note that blender does a coordinate transform from glb/gltf files.
The mapping is:

| Blender | gltf/glb |
| :-----: | :------: |
|    x    |    x     |
|    y    |    -z    |
|    z    |    y     |

This is equivalent to a rotation around the x-axis by 90 degrees.
There is also the `--blender` flag which may be used to transform the coordinate system to be displayed correctly in blender.
However, in this case the coordinate system would be changed inside the gltf/glb file.

# Display in the web

An example for [three.js](https://threejs.org) based rendering is available in [`examples/threejs`](https://github.com/FAIRmat-NFDI/nexus3d/tree/main/examples/threejs). It is based on this [example](https://threejs.org/examples/?q=gltf#webgl_loader_gltf) from three.js. The example can be directly viewed in the github pages of this project: [fairmat-nfdi.github.io/nexus3d/](https://fairmat-nfdi.github.io/nexus3d/). To quickly view your model there exists the excellent [gltf viewer](https://gltf-viewer.donmccurdy.com), which also allows to adjust lighting and materials of your model.
