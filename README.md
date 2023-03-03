# Scope

This is a project for reading out NX_TRANSFORMATION matrices from nexus files and
visualizing them by creating a 3D representation file (e.g. stl or gltf) which may be imported into 3D visualization software.

# Install

The easiest way to install is with pip

```
pip install git+https://github.com/domna/nexus3d.git
```

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
  -o, --output TEXT     The filename to write to (default: experiment.glb).
  -c, --config TEXT     Config file to load stl drawings into the final output
  -s, --size FLOAT      The side length of a cube in meters. (default: 0.1 m).
  -f, --force           Force overwriting of output file.
  --include-process     Include transformations inside /entry/process
  --store-intermediate  Store the intermediate matrices in gltf child nodes.
                        Only applicable for gltf or glb files.
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
    "rot_x": 90
  },
  "instrument/detector": {
    "file": "my_detector.stl"
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

# Display in the web

An example for [three.js](https://threejs.org) based rendering is available in `examples/threejs`. It is based on this [example](https://threejs.org/examples/?q=gltf#webgl_loader_gltf) from three.js. The example can be directly viewed in the github pages of this project: [https://domna.github.io/nexus3d/](https://domna.github.io/nexus3d/).
