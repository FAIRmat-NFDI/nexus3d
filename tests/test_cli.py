"""Tests the CLI"""
import os

import pytest
from click.testing import CliRunner

from nexus3d.nexus_transformations import cli


@pytest.mark.filterwarnings("ignore: This file .* contains a binary blob")
def test_cli(tmp_path):
    """A test for the convert CLI."""
    path = os.getenv("PYTEST_CURRENT_TEST").rsplit("/", 1)[0]
    output_files = [
        tmp_path / f"experiment.{file_ending}" for file_ending in ["stl", "glb", "gltf"]
    ]

    for output_file in output_files:
        cli_input = [
            f"{path}/data/transformation_example.h5",
            "--output",
            str(output_file),
        ]
        runner = CliRunner()
        result = runner.invoke(cli, cli_input)

        assert result.exit_code == 0
