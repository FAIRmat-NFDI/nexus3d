#!/bin/bash

python -m pycodestyle --ignore=E501,E701,E731,W503,E203 nexus3d
python -m pylint nexus3d
python -m mypy --ignore-missing-imports --follow-imports=silent --no-strict-optional nexus3d