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
  -s, --size FLOAT      The side length of a cube in meters. (default: 0.1 m).
  -f, --force           Force overwriting of output file.
  --include-process     Include transformations inside /entry/process
  --store-intermediate  Store the intermediate matrices in gltf child nodes.
                        Only applicable for gltf or glb files.
  --help                Show this message and exit.
```
