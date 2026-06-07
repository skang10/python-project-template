from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

TEMPLATE_ROOT = Path(__file__).parents[1]


@pytest.fixture
def default_answers() -> dict[str, Any]:
    return {
        "project_name": "Example Project",
        "distribution_name": "example-project",
        "package_name": "example_project",
        "project_description": "An example generated project.",
        "author_name": "Example Author",
        "author_email": "author@example.com",
        "github_owner": "example",
        "github_repository": "example-project",
        "include_cli": False,
        "include_docker": False,
        "include_docs": False,
        "include_release": False,
    }


def render_project(
    destination: Path,
    answers: dict[str, Any],
    *,
    run_tasks: bool = False,
) -> Path:
    command = [
        "uv",
        "run",
        "copier",
        "copy",
        "--trust",
        "--defaults",
        "--quiet",
    ]
    if not run_tasks:
        command.append("--skip-tasks")
    for key, value in answers.items():
        rendered_value = str(value).lower() if isinstance(value, bool) else value
        command.extend(["--data", f"{key}={rendered_value}"])
    command.extend([str(TEMPLATE_ROOT), str(destination)])
    subprocess.run(command, check=True, cwd=TEMPLATE_ROOT)
    return destination
