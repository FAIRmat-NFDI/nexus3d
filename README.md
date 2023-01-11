# Scope

This is a project for reading out NX_TRANSFORMATION matrices from nexus files and
visualizing them by creating a stl which may be importet into 3D visualization software.

# Install

Just execute

```
pip install .
```

from the cloned git repository or add an optional `-e` to install it in development mode.

# Usage

Execute

```
nexus2stl nexus_file.nxs
```

on your nexus file to generate an output file `experiment.stl`.
The usage of the command is as follows:

```
Usage: nexus2stl [OPTIONS] FILE

  Create a stl from a nexus file via the command line

Options:
  --output TEXT  The filename to write to
  -f, --force    Force overwriting of output file
  --help         Show this message and exit.
```
