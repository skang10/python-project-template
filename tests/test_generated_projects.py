from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from conftest import render_project


def run(project: Path, *command: str) -> None:
    subprocess.run(command, cwd=project, check=True)


@pytest.mark.parametrize(
    ("name", "features"),
    [
        ("minimal", {}),
        (
            "full",
            {
                "include_cli": True,
                "include_docker": True,
                "include_docs": True,
                "include_release": True,
            },
        ),
    ],
)
def test_generated_project_quality_suite(
    tmp_path: Path,
    default_answers: dict[str, Any],
    name: str,
    features: dict[str, bool],
) -> None:
    project = render_project(
        tmp_path / name,
        {**default_answers, **features},
        run_tasks=True,
    )

    assert (project / "uv.lock").is_file()
    run(project, "uv", "sync", "--locked", "--all-groups")
    run(project, "uv", "run", "ruff", "check", ".")
    run(project, "uv", "run", "ruff", "format", "--check", ".")
    run(project, "uv", "run", "mypy", "src")
    run(project, "uv", "run", "pytest")
    run(project, "uv", "build")

    if features.get("include_docs"):
        run(project, "uv", "run", "mkdocs", "build", "--strict")


def test_full_project_dockerfile_builds_when_docker_is_available(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    if shutil.which("docker") is None:
        pytest.skip("Docker is not available")
    project = render_project(
        tmp_path / "docker",
        {
            **default_answers,
            "include_cli": True,
            "include_docker": True,
        },
        run_tasks=True,
    )

    run(project, "docker", "build", "-t", "example-project-template-test", ".")
