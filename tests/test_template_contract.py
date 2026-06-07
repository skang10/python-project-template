import subprocess
import tomllib
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

    pyproject = tomllib.loads((project / "pyproject.toml").read_text())
    assert pyproject["project"]["name"] == "example-project"
    assert pyproject["project"]["requires-python"] == ">=3.12"
    assert pyproject["build-system"]["build-backend"] == "hatchling.build"
    assert pyproject["dependency-groups"]["dev"]
    assert (project / ".python-version").read_text().strip() == "3.12"
    assert (project / "LICENSE").is_file()


def test_minimal_project_has_no_optional_dependencies(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    project = render_project(tmp_path / "minimal", default_answers)
    pyproject = tomllib.loads((project / "pyproject.toml").read_text())

    assert pyproject["project"]["dependencies"] == []
    assert "scripts" not in pyproject["project"]
    assert "docs" not in pyproject["dependency-groups"]


def test_minimal_project_has_quality_workflows(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    project = render_project(tmp_path / "minimal", default_answers)
    readme = (project / "README.md").read_text()
    workflow = (project / ".github/workflows/ci.yml").read_text()

    for command in (
        "uv sync --all-groups",
        "uv run pytest",
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run mypy src",
        "uv run pre-commit install",
        "uv build",
    ):
        assert command in readme
    assert (project / ".pre-commit-config.yaml").is_file()
    assert "lint:" in workflow
    assert "format:" in workflow
    assert "type-check:" in workflow
    assert "test:" in workflow
    assert "uv sync --locked --all-groups" in workflow
    assert "${{" in workflow
    assert "[[" not in workflow


def test_cli_feature_is_conditional(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    minimal = render_project(tmp_path / "minimal", default_answers)
    cli = render_project(
        tmp_path / "cli",
        {**default_answers, "include_cli": True},
    )

    assert not (minimal / "src/example_project/cli.py").exists()
    assert not (minimal / "tests/test_cli.py").exists()

    assert (cli / "src/example_project/cli.py").is_file()
    assert (cli / "tests/test_cli.py").is_file()
    pyproject = tomllib.loads((cli / "pyproject.toml").read_text())
    assert "typer>=0.15" in pyproject["project"]["dependencies"]
    assert pyproject["project"]["scripts"] == {
        "example-project": "example_project.cli:app"
    }
    assert "uv run example-project hello World" in (cli / "README.md").read_text()


def test_docs_feature_is_conditional(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    minimal = render_project(tmp_path / "minimal", default_answers)
    docs = render_project(
        tmp_path / "docs",
        {**default_answers, "include_docs": True},
    )

    assert not (minimal / "mkdocs.yml").exists()
    assert not (minimal / "docs").exists()
    assert (
        "docs"
        not in tomllib.loads((minimal / "pyproject.toml").read_text())[
            "dependency-groups"
        ]
    )

    assert (docs / "mkdocs.yml").is_file()
    assert (docs / "docs/index.md").is_file()
    assert (docs / "docs/usage.md").is_file()
    assert (
        "mkdocs-material>=9.6"
        in tomllib.loads((docs / "pyproject.toml").read_text())["dependency-groups"][
            "docs"
        ]
    )
    assert "uv run mkdocs serve" in (docs / "README.md").read_text()
    assert "docs:" in (docs / ".github/workflows/ci.yml").read_text()


def test_docker_feature_is_conditional(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    minimal = render_project(tmp_path / "minimal", default_answers)
    docker = render_project(
        tmp_path / "docker",
        {**default_answers, "include_docker": True},
    )
    docker_cli = render_project(
        tmp_path / "docker-cli",
        {**default_answers, "include_docker": True, "include_cli": True},
    )

    assert not (minimal / "Dockerfile").exists()
    assert not (minimal / ".dockerignore").exists()

    dockerfile = (docker / "Dockerfile").read_text()
    assert "FROM python:3.12-slim" in dockerfile
    assert "uv sync --locked --no-dev" in dockerfile
    assert "USER app" in dockerfile
    assert 'CMD ["python"]' in dockerfile
    assert (docker / ".dockerignore").is_file()

    assert 'CMD ["example-project"]' in (docker_cli / "Dockerfile").read_text()


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
