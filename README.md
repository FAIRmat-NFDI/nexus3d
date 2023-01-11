# Scope

This is a testing project for reading out NX_TRANSFORMATION matrices from nexus files and
visualizing them.
There are two code snippets for either [reading](https://github.com/dials/dials/blob/5bf004bf8f92e891d0008d27b747578f0d35e827/src/dials/util/nexus/nx_mx.py#L126) or [writing](https://github.com/dials/cctbx/blob/master/xfel/euxfel/agipd_cxigeom2nexus.py) NX_TRANSFORMATION groups.
There is also the [nexus-constructor](https://github.com/ess-dmsc/nexus-constructor) which is able to
construct nexus transformation groups but is not able to load and display transformation groups
from nexus files.

# Idea

The idea is to extract a plane into a dxf file with [ezdxf](https://github.com/mozman/ezdxf).
Then a CAD software can be used to check whether the transformations are correct,
i.e. checking angles with respect to each other.

# Progress

- [ ] Extract transformation groups from an example file (`MoTe2.mpes.nxs`).
- [ ] Draw it as points into the final dxf file
- [ ] Add a line for the beam in the experiment
- [ ] Try to load the file with FreeCAD and try to extract an angle

## Transformation matrices

[Here](https://www.brainvoyager.com/bv/doc/UsersGuide/CoordsAndTransforms/SpatialTransformationMatrices.html) is some literature on affine 4D transformation matrices.

TL;DR: A point is represented by (x, y, z, 1).T to account also for translations and
a vector is represented by (x, y, z, 0).T to strip it of its position.

With this 4x4 transformation matrixes are build as

```
[R, o]
[0, 1]
```

for rotation and

```
[I, t+o]
[0, 1]
```

for translation in nexus.
Where o is an offset vector, t is the translation vector and R is a rotation matrix.
Read more details [here](https://manual.nexusformat.org/classes/base_classes/NXtransformations.html#nxtransformations).
