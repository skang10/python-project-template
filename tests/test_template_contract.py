import subprocess
from pathlib import Path
from typing import Any

import yaml
from conftest import TEMPLATE_ROOT, render_project


def test_minimal_project_renders(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    project = render_project(tmp_path / "minimal", default_answers)

    assert (project / "pyproject.toml").is_file()
    assert (project / "src/example_project/__init__.py").is_file()
    assert (project / "tests/test_package.py").is_file()
    assert (project / ".copier-answers.yml").is_file()


def test_copier_configuration_has_expected_defaults() -> None:
    config = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text())

    assert config["_subdirectory"] == "template"
    assert config["_templates_suffix"] == ".jinja"
    assert config["_answers_file"] == ".copier-answers.yml"
    assert config["include_cli"]["default"] is False
    assert config["include_docker"]["default"] is False
    assert config["include_docs"]["default"] is False
    assert config["include_release"]["default"] is False
    assert config["_tasks"] == [["uv", "lock"]]


def test_invalid_package_name_is_rejected(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    answers = {**default_answers, "package_name": "not-valid"}
    command = [
        "uv",
        "run",
        "copier",
        "copy",
        "--trust",
        "--skip-tasks",
        "--defaults",
    ]
    for key, value in answers.items():
        rendered_value = str(value).lower() if isinstance(value, bool) else value
        command.extend(["--data", f"{key}={rendered_value}"])
    command.extend([str(TEMPLATE_ROOT), str(tmp_path / "invalid")])

    result = subprocess.run(
        command,
        cwd=TEMPLATE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "valid Python identifier" in result.stderr
