"""Tests the CLI"""
import os
from click.testing import CliRunner

from nexus3d.nexus_transformations import cli


def test_cli(tmp_path):
    """A test for the convert CLI."""
    path = os.getenv("PYTEST_CURRENT_TEST").rsplit("/", 1)[0]
    output_file = tmp_path / "experiment.stl"
    cli_input = [
        f"{path}/data/transformation_example.h5",
        "--output",
        str(output_file),
    ]
    runner = CliRunner()
    result = runner.invoke(cli, cli_input)

    assert result.exit_code == 0
