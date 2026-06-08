import json
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

    answers = yaml.safe_load((project / ".copier-answers.yml").read_text())
    assert answers["_src_path"] == str(TEMPLATE_ROOT)
    assert answers["_commit"]

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
        "uv run pre-commit run --all-files",
        "uv build",
    ):
        assert command in readme
    for path_description in (
        "`src/example_project/`",
        "`tests/`",
        "`pyproject.toml`",
        "`uv.lock`",
    ):
        assert path_description in readme

    assert "https://docs.astral.sh/uv/getting-started/installation/" in readme
    assert "## CLI" not in readme
    assert "## Documentation" not in readme
    assert "## Docker" not in readme
    assert "## Releases" not in readme
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
    minimal_readme = (minimal / "README.md").read_text()
    cli_readme = (cli / "README.md").read_text()
    assert "typer>=0.15" in pyproject["project"]["dependencies"]
    assert pyproject["project"]["scripts"] == {
        "example-project": "example_project.cli:app"
    }
    assert "## CLI" not in minimal_readme
    assert "`src/example_project/cli.py`" not in minimal_readme
    assert "uv run example-project --help" in cli_readme
    assert "uv run example-project hello World" in cli_readme
    assert "`src/example_project/cli.py`" in cli_readme
    assert "`tests/test_cli.py`" in cli_readme


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
    minimal_readme = (minimal / "README.md").read_text()
    docs_readme = (docs / "README.md").read_text()
    assert (
        "mkdocs-material>=9.6"
        in tomllib.loads((docs / "pyproject.toml").read_text())["dependency-groups"][
            "docs"
        ]
    )
    assert "## Documentation" not in minimal_readme
    assert "http://127.0.0.1:8000" not in minimal_readme
    assert "uv run mkdocs serve" in docs_readme
    assert "http://127.0.0.1:8000" in docs_readme
    assert "uv run mkdocs build --strict" in docs_readme
    assert "`site/`" in docs_readme
    assert "`docs/`" in docs_readme
    assert "`mkdocs.yml`" in docs_readme
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

    minimal_readme = (minimal / "README.md").read_text()
    docker_readme = (docker / "README.md").read_text()
    docker_cli_readme = (docker_cli / "README.md").read_text()
    dockerfile = (docker / "Dockerfile").read_text()
    assert "FROM python:3.12-slim" in dockerfile
    assert "uv sync --locked --no-dev" in dockerfile
    assert "USER app" in dockerfile
    assert 'CMD ["python"]' in dockerfile
    assert (docker / ".dockerignore").is_file()

    assert 'CMD ["example-project"]' in (docker_cli / "Dockerfile").read_text()
    assert "## Docker" not in minimal_readme
    assert "docker build -t example-project ." in docker_readme
    assert "docker run --rm example-project" in docker_readme
    assert "docker run --rm example-project hello World" in docker_cli_readme


def test_release_feature_creates_github_artifacts_only(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    minimal = render_project(tmp_path / "minimal", default_answers)
    release = render_project(
        tmp_path / "release",
        {**default_answers, "include_release": True},
    )

    assert not (minimal / ".github/workflows/release-please.yml").exists()
    assert not (minimal / ".github/workflows/release.yml").exists()

    minimal_readme = (minimal / "README.md").read_text()
    release_readme = (release / "README.md").read_text()
    workflow = (release / ".github/workflows/release-please.yml").read_text()

    assert "googleapis/release-please-action" in workflow
    assert "release_created" in workflow
    assert "branches:" in workflow
    assert "uv sync --locked --all-groups" in workflow
    assert "uv build" in workflow
    assert "uv run twine check dist/*" in workflow
    assert "gh release upload" in workflow
    assert "contents: write" in workflow
    assert "pull-requests: write" in workflow
    assert "uv publish" not in workflow
    assert "id-token: write" not in workflow
    assert "pypi" not in workflow.lower()
    assert "gh release create" not in workflow
    assert "tags:" not in workflow

    assert (release / "release-please-config.json").is_file()
    assert (release / ".release-please-manifest.json").is_file()

    config = json.loads((release / "release-please-config.json").read_text())
    assert config["packages"]["."]["release-type"] == "python"

    manifest = json.loads((release / ".release-please-manifest.json").read_text())
    assert manifest["."] == "0.1.0"

    assert "## Releases" not in minimal_readme
    assert "## Releases" in release_readme
    assert "git tag v0.1.0" not in release_readme
    assert "Conventional Commit" in release_readme
    assert "GitHub Releases" in release_readme
    assert "does not publish to PyPI" in release_readme


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


def test_template_readme_documents_generation_and_updates() -> None:
    readme = (TEMPLATE_ROOT / "README.md").read_text()

    assert "copier copy --trust" in readme
    assert "uv run pytest" in readme
    assert "copier update --trust" in readme
    assert "GitHub Releases" in readme
    assert "does not publish to PyPI" in readme


def test_template_repository_has_ci() -> None:
    workflow = (TEMPLATE_ROOT / ".github/workflows/ci.yml").read_text()

    assert "uv run ruff check ." in workflow
    assert "uv run ruff format --check ." in workflow
    assert "uv run mypy tests" in workflow
    assert "uv run pytest" in workflow
    assert "docker" in workflow.lower()
