# General-Purpose Python Project Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Copier template that generates Python 3.12+ projects with a tested `uv`-managed quality baseline and optional Typer CLI, Docker, MkDocs Material, and GitHub release artifacts.

**Architecture:** The repository is a Python test project whose product is the `template/` tree. `copier.yml` owns prompts, validation, custom Jinja delimiters, conditional rendering, and the trusted `uv lock` post-generation task; pytest renders feature combinations into temporary directories and validates both file structure and executable project workflows.

**Tech Stack:** Python 3.12+, Copier, Jinja, uv, pytest, Ruff, mypy, Hatchling, Typer, MkDocs Material, GitHub Actions, Docker

---

## File Map

### Template Repository

- `pyproject.toml`: Development dependencies and Ruff, mypy, and pytest configuration for testing the template.
- `.python-version`: Pins Python 3.12 for template development.
- `.gitignore`: Ignores the template repository's virtual environment, caches, and generated test artifacts.
- `README.md`: Explains how to install Copier, generate a project, trust the lock task, test the template, and update generated projects.
- `copier.yml`: Defines questions, validation, Jinja delimiters, template root, answers file, and `uv lock` task.
- `tests/conftest.py`: Provides canonical answers and a helper that invokes Copier into a temporary directory.
- `tests/test_template_contract.py`: Tests question defaults, validation, rendering, answers metadata, and optional-file boundaries.
- `tests/test_generated_projects.py`: Runs quality, test, build, docs, and Docker-structure checks against rendered projects.
- `.github/workflows/ci.yml`: Runs the template repository's own static checks and generation matrix.

### Always-Rendered Project Files

- `template/pyproject.toml.jinja`: PEP 621 metadata, Hatchling build backend, baseline development dependencies, optional dependencies, scripts, and tool configuration.
- `template/.copier-answers.yml.jinja`: Retains Copier source/version and project answers for updates.
- `template/.python-version.jinja`: Pins Python 3.12.
- `template/.gitignore.jinja`: Ignores Python, uv, build, test, type-check, and documentation artifacts.
- `template/.pre-commit-config.yaml.jinja`: Runs Ruff linting and formatting.
- `template/LICENSE.jinja`: MIT license with generated author and year.
- `template/README.md.jinja`: Documents setup, quality commands, packaging, and selected optional features.
- `template/src/[[ package_name ]]/__init__.py.jinja`: Exposes `__version__` and `greet`.
- `template/tests/test_package.py.jinja`: Verifies package import, version, and greeting behavior.
- `template/.github/workflows/ci.yml.jinja`: Separate lint, format, type, test, and conditional docs jobs using locked dependencies.

### Optional Project Files

- `template/src/[[ package_name ]]/cli.py.jinja`: Typer application, rendered only for CLI projects.
- `template/tests/test_cli.py.jinja`: CLI behavior tests, rendered only for CLI projects.
- `template/Dockerfile.jinja`: Locked, non-root Python 3.12 image, rendered only for Docker projects.
- `template/.dockerignore.jinja`: Docker build exclusions, rendered only for Docker projects.
- `template/mkdocs.yml.jinja`: Strict MkDocs Material configuration, rendered only for documentation projects.
- `template/docs/index.md.jinja`: Documentation landing page, rendered only for documentation projects.
- `template/docs/usage.md.jinja`: Generated-project usage page, rendered only for documentation projects.
- `template/.github/workflows/release.yml.jinja`: Tag-triggered GitHub artifact release, rendered only for release projects.

## Implementation Decisions

- Set Copier's Jinja variables to `[[ ... ]]` and blocks to `[% ... %]`. This prevents collisions with GitHub Actions `${{ ... }}` expressions.
- Set `_subdirectory: template`, `_templates_suffix: .jinja`, and `_answers_file: .copier-answers.yml`.
- Use `_tasks: [["uv", "lock"]]`. Generation therefore requires `copier copy --trust`; tests invoke Copier with the same trust boundary.
- Use Copier conditional filenames such as `[% if include_cli %]cli.py[% endif %].jinja`; disabled features render no file.
- Use dependency groups: baseline tools in `dev`, documentation tools in `docs` only when documentation is selected.
- Use Hatchling as the generated package build backend because it supports `src/` layouts with minimal configuration.
- Use `uv sync --locked --all-groups` in CI. `--locked` checks that `pyproject.toml` still agrees with the committed lockfile.
- Pin third-party GitHub Actions to full commit SHAs and retain release comments beside each SHA.
- Test Dockerfile structure in normal CI. Build the image only when Docker is available.

### Task 1: Bootstrap the Template Repository Test Harness

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.gitignore`
- Create: `tests/conftest.py`
- Create: `tests/test_template_contract.py`

- [ ] **Step 1: Write the failing smoke test**

Create `tests/conftest.py`:

```python
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
        command.extend(["--data", f"{key}={str(value).lower() if isinstance(value, bool) else value}"])
    command.extend([str(TEMPLATE_ROOT), str(destination)])
    subprocess.run(command, check=True, cwd=TEMPLATE_ROOT)
    return destination
```

Create `tests/test_template_contract.py`:

```python
from pathlib import Path
from typing import Any

from conftest import render_project


def test_minimal_project_renders(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    project = render_project(tmp_path / "minimal", default_answers)

    assert (project / "pyproject.toml").is_file()
    assert (project / "src/example_project/__init__.py").is_file()
    assert (project / "tests/test_package.py").is_file()
    assert (project / ".copier-answers.yml").is_file()
```

- [ ] **Step 2: Add the template repository configuration**

Create `pyproject.toml`:

```toml
[project]
name = "python-project-template"
version = "0.1.0"
description = "A tested Copier template for general-purpose Python projects."
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "copier>=9,<10",
  "mypy>=1.15",
  "pytest>=8.3",
  "pyyaml>=6.0",
  "ruff>=0.11",
]

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["tests"]
```

Create `.python-version`:

```text
3.12
```

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.py[cod]
dist/
build/
```

- [ ] **Step 3: Run the smoke test and verify the intended failure**

Run:

```bash
uv sync
uv run pytest tests/test_template_contract.py::test_minimal_project_renders -v
```

Expected: FAIL because `copier.yml` does not exist.

- [ ] **Step 4: Run repository static checks**

Run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
```

Expected: PASS. If Ruff wraps the long `command.extend` line, run `uv run ruff format .` and rerun the checks.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock .python-version .gitignore tests
git commit -m "test: bootstrap template test harness"
```

### Task 2: Define Copier's Question and Rendering Contract

**Files:**
- Create: `copier.yml`
- Modify: `tests/test_template_contract.py`
- Create: `template/.copier-answers.yml.jinja`

- [ ] **Step 1: Add failing configuration tests**

Append to `tests/test_template_contract.py`:

```python
import subprocess

import yaml

from conftest import TEMPLATE_ROOT


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
        command.extend(["--data", f"{key}={str(value).lower() if isinstance(value, bool) else value}"])
    command.extend([str(TEMPLATE_ROOT), str(tmp_path / "invalid")])

    result = subprocess.run(command, cwd=TEMPLATE_ROOT, capture_output=True, text=True)

    assert result.returncode != 0
    assert "valid Python identifier" in result.stderr
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: FAIL because `copier.yml` and the template root do not exist.

- [ ] **Step 3: Implement Copier configuration**

Create `copier.yml`:

```yaml
_min_copier_version: "9.0.0"
_subdirectory: template
_templates_suffix: .jinja
_answers_file: .copier-answers.yml
_envops:
  block_start_string: "[%"
  block_end_string: "%]"
  variable_start_string: "[["
  variable_end_string: "]]"
  keep_trailing_newline: true
_tasks:
  - [uv, lock]

project_name:
  type: str
  help: Human-readable project name

distribution_name:
  type: str
  help: Package distribution name
  default: "[[ project_name | lower | replace(' ', '-') | replace('_', '-') ]]"
  validator: >-
    [% if not (distribution_name | regex_search('^[a-z0-9]+([._-][a-z0-9]+)*$')) %]
    Enter a valid Python distribution name.
    [% endif %]

package_name:
  type: str
  help: Python import package name
  default: "[[ distribution_name | replace('-', '_') | replace('.', '_') ]]"
  validator: >-
    [% if not (package_name | regex_search('^[A-Za-z_][A-Za-z0-9_]*$')) %]
    Enter a valid Python identifier.
    [% endif %]

project_description:
  type: str
  default: "A Python project."

author_name:
  type: str

author_email:
  type: str
  validator: >-
    [% if not (author_email | regex_search('^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$')) %]
    Enter a valid email address.
    [% endif %]

github_owner:
  type: str
  validator: >-
    [% if not (github_owner | regex_search('^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$')) %]
    Enter a valid GitHub owner.
    [% endif %]

github_repository:
  type: str
  default: "[[ distribution_name ]]"
  validator: >-
    [% if not (github_repository | regex_search('^[A-Za-z0-9._-]+$')) %]
    Enter a valid GitHub repository name.
    [% endif %]

include_cli:
  type: bool
  default: false

include_docker:
  type: bool
  default: false

include_docs:
  type: bool
  default: false

include_release:
  type: bool
  default: false
```

Create `template/.copier-answers.yml.jinja`:

```yaml
_src_path: "[[ _copier_conf.src_path ]]"
_commit: "[[ _copier_conf.vcs_ref ]]"
project_name: "[[ project_name ]]"
distribution_name: "[[ distribution_name ]]"
package_name: "[[ package_name ]]"
project_description: "[[ project_description ]]"
author_name: "[[ author_name ]]"
author_email: "[[ author_email ]]"
github_owner: "[[ github_owner ]]"
github_repository: "[[ github_repository ]]"
include_cli: [[ include_cli | lower ]]
include_docker: [[ include_docker | lower ]]
include_docs: [[ include_docs | lower ]]
include_release: [[ include_release | lower ]]
```

- [ ] **Step 4: Run configuration tests**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: configuration and invalid-name tests PASS; smoke test still FAILS because baseline project files do not exist.

- [ ] **Step 5: Commit**

```bash
git add copier.yml template/.copier-answers.yml.jinja tests/test_template_contract.py
git commit -m "feat: define copier generation contract"
```

### Task 3: Render the Baseline Python Package

**Files:**
- Create: `template/pyproject.toml.jinja`
- Create: `template/.python-version.jinja`
- Create: `template/.gitignore.jinja`
- Create: `template/LICENSE.jinja`
- Create: `template/src/[[ package_name ]]/__init__.py.jinja`
- Create: `template/tests/test_package.py.jinja`
- Modify: `tests/test_template_contract.py`

- [ ] **Step 1: Expand the failing baseline assertions**

Add these imports and assertions to `test_minimal_project_renders`:

```python
import tomllib


    pyproject = tomllib.loads((project / "pyproject.toml").read_text())
    assert pyproject["project"]["name"] == "example-project"
    assert pyproject["project"]["requires-python"] == ">=3.12"
    assert pyproject["build-system"]["build-backend"] == "hatchling.build"
    assert pyproject["dependency-groups"]["dev"]
    assert (project / ".python-version").read_text().strip() == "3.12"
    assert (project / "LICENSE").is_file()
```

Add:

```python
def test_minimal_project_has_no_optional_dependencies(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    project = render_project(tmp_path / "minimal", default_answers)
    pyproject = tomllib.loads((project / "pyproject.toml").read_text())

    assert pyproject["project"]["dependencies"] == []
    assert "scripts" not in pyproject["project"]
    assert "docs" not in pyproject["dependency-groups"]
```

- [ ] **Step 2: Run tests to verify baseline assertions fail**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: FAIL because baseline files are missing.

- [ ] **Step 3: Create baseline package metadata**

Create `template/pyproject.toml.jinja`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "[[ distribution_name ]]"
version = "0.1.0"
description = "[[ project_description ]]"
readme = "README.md"
requires-python = ">=3.12"
license = { file = "LICENSE" }
authors = [
  { name = "[[ author_name ]]", email = "[[ author_email ]]" },
]
dependencies = [
[% if include_cli %]
  "typer>=0.15",
[% endif %]
]

[% if include_cli %]
[project.scripts]
[[ distribution_name ]] = "[[ package_name ]].cli:app"
[% endif %]

[project.urls]
Homepage = "https://github.com/[[ github_owner ]]/[[ github_repository ]]"
Repository = "https://github.com/[[ github_owner ]]/[[ github_repository ]]"
Issues = "https://github.com/[[ github_owner ]]/[[ github_repository ]]/issues"

[dependency-groups]
dev = [
  "mypy>=1.15",
  "pre-commit>=4.2",
  "pytest>=8.3",
  "ruff>=0.11",
]
[% if include_docs %]
docs = [
  "mkdocs>=1.6",
  "mkdocs-material>=9.6",
]
[% endif %]

[tool.hatch.build.targets.wheel]
packages = ["src/[[ package_name ]]"]

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

Create `template/.python-version.jinja`:

```text
3.12
```

Create `template/.gitignore.jinja`:

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
dist/
build/
site/
```

Create `template/LICENSE.jinja` using the standard MIT license text, with:

```text
Copyright (c) 2026 [[ author_name ]]
```

- [ ] **Step 4: Create baseline source and tests**

Create `template/src/[[ package_name ]]/__init__.py.jinja`:

```python
"""[[ project_description ]]"""

__version__ = "0.1.0"


def greet(name: str) -> str:
    """Return a greeting for *name*."""
    return f"Hello, {name}!"
```

Create `template/tests/test_package.py.jinja`:

```python
import [[ package_name ]]


def test_version() -> None:
    assert [[ package_name ]].__version__ == "0.1.0"


def test_greet() -> None:
    assert [[ package_name ]].greet("World") == "Hello, World!"
```

- [ ] **Step 5: Run the contract tests**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add template tests/test_template_contract.py
git commit -m "feat: render baseline python package"
```

### Task 4: Add Baseline Documentation, Pre-Commit, and CI

**Files:**
- Create: `template/README.md.jinja`
- Create: `template/.pre-commit-config.yaml.jinja`
- Create: `template/.github/workflows/ci.yml.jinja`
- Modify: `tests/test_template_contract.py`

- [ ] **Step 1: Write failing workflow and documentation assertions**

Append:

```python
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
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
uv run pytest tests/test_template_contract.py::test_minimal_project_has_quality_workflows -v
```

Expected: FAIL because the rendered files do not exist.

- [ ] **Step 3: Add generated README and pre-commit hooks**

Create `template/README.md.jinja` with:

```markdown
# [[ project_name ]]

[[ project_description ]]

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync --all-groups
uv run pre-commit install
```

## Quality

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Build

```bash
uv build
```
```

Create `template/.pre-commit-config.yaml.jinja`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.0
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 4: Add generated-project CI**

Create `template/.github/workflows/ci.yml.jinja` with four baseline jobs:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
          version: "0.11.19"
      - run: uv sync --locked --all-groups
      - run: uv run ruff check .

  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
          version: "0.11.19"
      - run: uv sync --locked --all-groups
      - run: uv run ruff format --check .

  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
          version: "0.11.19"
      - run: uv sync --locked --all-groups
      - run: uv run mypy src

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
          version: "0.11.19"
      - run: uv sync --locked --all-groups
      - run: uv run pytest
```

The pins above correspond to `actions/checkout` v6.0.3,
`astral-sh/setup-uv` v8.1.0, and uv 0.11.19 as verified on 2026-06-07. Keep
`${{ ... }}` expressions unchanged where cache keys or GitHub contexts are
added.

- [ ] **Step 5: Run contract and formatting tests**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
uv run ruff check .
uv run ruff format --check .
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add template tests/test_template_contract.py
git commit -m "feat: add generated project quality workflows"
```

### Task 5: Add the Optional Typer CLI

**Files:**
- Create: `template/src/[[ package_name ]]/[% if include_cli %]cli.py[% endif %].jinja`
- Create: `template/tests/[% if include_cli %]test_cli.py[% endif %].jinja`
- Modify: `template/README.md.jinja`
- Modify: `tests/test_template_contract.py`

- [ ] **Step 1: Write failing CLI boundary tests**

Append:

```python
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
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
uv run pytest tests/test_template_contract.py::test_cli_feature_is_conditional -v
```

Expected: FAIL because CLI files and README instructions are missing.

- [ ] **Step 3: Implement the CLI and its generated test**

Create `template/src/[[ package_name ]]/[% if include_cli %]cli.py[% endif %].jinja`:

```python
import typer

from [[ package_name ]] import greet

app = typer.Typer(no_args_is_help=True)


@app.command()
def hello(name: str = "World") -> None:
    """Print a greeting."""
    typer.echo(greet(name))


if __name__ == "__main__":
    app()
```

Create `template/tests/[% if include_cli %]test_cli.py[% endif %].jinja`:

```python
from typer.testing import CliRunner

from [[ package_name ]].cli import app


runner = CliRunner()


def test_hello() -> None:
    result = runner.invoke(app, ["hello", "Codex"])

    assert result.exit_code == 0
    assert result.stdout == "Hello, Codex!\n"
```

- [ ] **Step 4: Add conditional README usage**

Append to `template/README.md.jinja`:

```markdown
[% if include_cli %]
## CLI

```bash
uv run [[ distribution_name ]] hello World
```
[% endif %]
```

Use `uv run example-project hello World` in the expected test assertion, matching
Typer's explicit `hello` subcommand.

- [ ] **Step 5: Run CLI contract tests**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add template tests/test_template_contract.py
git commit -m "feat: add optional typer cli"
```

### Task 6: Add Optional MkDocs Documentation

**Files:**
- Create: `template/[% if include_docs %]mkdocs.yml[% endif %].jinja`
- Create: `template/[% if include_docs %]docs[% endif %]/index.md.jinja`
- Create: `template/[% if include_docs %]docs[% endif %]/usage.md.jinja`
- Modify: `template/README.md.jinja`
- Modify: `template/.github/workflows/ci.yml.jinja`
- Modify: `tests/test_template_contract.py`

- [ ] **Step 1: Write failing documentation boundary tests**

Append:

```python
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
    assert "docs" not in tomllib.loads(
        (minimal / "pyproject.toml").read_text()
    )["dependency-groups"]

    assert (docs / "mkdocs.yml").is_file()
    assert (docs / "docs/index.md").is_file()
    assert (docs / "docs/usage.md").is_file()
    assert "mkdocs-material>=9.6" in tomllib.loads(
        (docs / "pyproject.toml").read_text()
    )["dependency-groups"]["docs"]
    assert "uv run mkdocs serve" in (docs / "README.md").read_text()
    assert "docs:" in (docs / ".github/workflows/ci.yml").read_text()
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
uv run pytest tests/test_template_contract.py::test_docs_feature_is_conditional -v
```

Expected: FAIL because MkDocs files and conditional workflow job are missing.

- [ ] **Step 3: Add MkDocs configuration and pages**

Create `template/[% if include_docs %]mkdocs.yml[% endif %].jinja`:

```yaml
site_name: "[[ project_name ]]"
site_description: "[[ project_description ]]"
repo_url: "https://github.com/[[ github_owner ]]/[[ github_repository ]]"
theme:
  name: material
nav:
  - Home: index.md
  - Usage: usage.md
strict: true
```

Create `template/[% if include_docs %]docs[% endif %]/index.md.jinja`:

```markdown
# [[ project_name ]]

[[ project_description ]]
```

Create `template/[% if include_docs %]docs[% endif %]/usage.md.jinja`:

```markdown
# Usage

Install dependencies with `uv sync --all-groups`, then import
`[[ package_name ]]` from Python.
```

- [ ] **Step 4: Add docs commands and CI**

Append conditionally to `template/README.md.jinja`:

```markdown
[% if include_docs %]
## Documentation

```bash
uv run mkdocs serve
uv run mkdocs build --strict
```
[% endif %]
```

Append conditionally to `template/.github/workflows/ci.yml.jinja`:

```yaml
[% if include_docs %]
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
          version: "0.11.19"
      - run: uv sync --locked --all-groups
      - run: uv run mkdocs build --strict
[% endif %]
```

- [ ] **Step 5: Run contract tests**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add template tests/test_template_contract.py
git commit -m "feat: add optional mkdocs site"
```

### Task 7: Add Optional Docker Support

**Files:**
- Create: `template/[% if include_docker %]Dockerfile[% endif %].jinja`
- Create: `template/[% if include_docker %].dockerignore[% endif %].jinja`
- Modify: `template/README.md.jinja`
- Modify: `tests/test_template_contract.py`

- [ ] **Step 1: Write failing Docker boundary tests**

Append:

```python
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

    assert 'CMD ["example-project"]' in (
        docker_cli / "Dockerfile"
    ).read_text()
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
uv run pytest tests/test_template_contract.py::test_docker_feature_is_conditional -v
```

Expected: FAIL because Docker files are missing.

- [ ] **Step 3: Implement the production-oriented Dockerfile**

Create `template/[% if include_docker %]Dockerfile[% endif %].jinja`:

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

RUN useradd --create-home --uid 10001 app
WORKDIR /app

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src

RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
USER app
[% if include_cli %]
CMD ["[[ distribution_name ]]"]
[% else %]
CMD ["python"]
[% endif %]
```

Keep the Docker uv version aligned with the version pinned in generated and
template CI.

Create `template/[% if include_docker %].dockerignore[% endif %].jinja`:

```dockerignore
.git
.github
.venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
dist
build
site
tests
docs
```

- [ ] **Step 4: Add conditional Docker documentation**

Append to `template/README.md.jinja`:

```markdown
[% if include_docker %]
## Docker

```bash
docker build -t [[ distribution_name ]] .
docker run --rm [[ distribution_name ]]
```
[% endif %]
```

- [ ] **Step 5: Run contract tests**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add template tests/test_template_contract.py
git commit -m "feat: add optional docker image"
```

### Task 8: Add Optional GitHub Release Artifacts

**Files:**
- Create: `template/.github/workflows/[% if include_release %]release.yml[% endif %].jinja`
- Modify: `template/README.md.jinja`
- Modify: `tests/test_template_contract.py`

- [ ] **Step 1: Write failing release boundary and security tests**

Append:

```python
def test_release_feature_creates_github_artifacts_only(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    minimal = render_project(tmp_path / "minimal", default_answers)
    release = render_project(
        tmp_path / "release",
        {**default_answers, "include_release": True},
    )

    assert not (minimal / ".github/workflows/release.yml").exists()

    workflow = (release / ".github/workflows/release.yml").read_text()
    assert "tags:" in workflow
    assert "uv sync --locked --all-groups" in workflow
    assert "uv build" in workflow
    assert "uv run twine check dist/*" in workflow
    assert "gh release create" in workflow
    assert "contents: write" in workflow
    assert "uv publish" not in workflow
    assert "id-token: write" not in workflow
    assert "pypi" not in workflow.lower()
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
uv run pytest tests/test_template_contract.py::test_release_feature_creates_github_artifacts_only -v
```

Expected: FAIL because the release workflow is missing.

- [ ] **Step 3: Add distribution validation dependency**

Modify the generated `dev` dependency group in
`template/pyproject.toml.jinja`:

```toml
  "twine>=6.1",
```

- [ ] **Step 4: Implement release workflow**

Create
`template/.github/workflows/[% if include_release %]release.yml[% endif %].jinja`:

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
          version: "0.11.19"
      - run: uv sync --locked --all-groups
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy src
      - run: uv run pytest
      - run: uv build
      - run: uv run twine check dist/*
      - name: Create GitHub release
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh release create "${{ github.ref_name }}" dist/* --generate-notes
```

The GitHub `${{ ... }}` expressions must survive rendering because Copier uses
`[[ ... ]]`.

- [ ] **Step 5: Document tag-based releases**

Append conditionally to `template/README.md.jinja`:

```markdown
[% if include_release %]
## Releases

Push a `v*` tag to run checks, build source and wheel distributions, and attach
them to a GitHub Release. This workflow does not publish to PyPI.
[% endif %]
```

- [ ] **Step 6: Run contract tests**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add template tests/test_template_contract.py
git commit -m "feat: add optional github release artifacts"
```

### Task 9: Verify Generated Projects End to End

**Files:**
- Create: `tests/test_generated_projects.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Write executable generated-project tests**

Create `tests/test_generated_projects.py`:

```python
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
    "name,features",
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
```

- [ ] **Step 2: Run tests and observe generated-project failures**

Run:

```bash
uv run pytest tests/test_generated_projects.py -v -m "not docker"
```

Expected: At least one generated quality command fails, exposing formatting,
typing, packaging, dependency, or Jinja issues not covered by structural tests.

- [ ] **Step 3: Fix only the reported generated-project defects**

Apply minimal corrections in the corresponding `template/` files. Common
expected corrections:

- Format generated Python with Ruff-compatible blank lines.
- Ensure Hatchling includes `src/[[ package_name ]]`.
- Ensure conditional TOML arrays remain valid with features disabled.
- Ensure CLI command tests use the actual Typer command shape.
- Ensure MkDocs strict mode has no broken navigation entries.
- Ensure `uv.lock` is generated after all feature-dependent dependencies render.

Do not weaken or skip a quality command to make the test pass.

- [ ] **Step 4: Run the complete executable suite**

Run:

```bash
uv run pytest tests/test_generated_projects.py -v
```

Expected: minimal and full quality suites PASS; Docker test PASS or SKIP only
when the Docker executable is unavailable.

- [ ] **Step 5: Run all repository checks**

Run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
uv run pytest -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add template tests
git commit -m "test: verify generated projects end to end"
```

### Task 10: Document Template Usage and Updates

**Files:**
- Create: `README.md`
- Modify: `tests/test_template_contract.py`

- [ ] **Step 1: Write a failing template-documentation test**

Append:

```python
def test_template_readme_documents_generation_and_updates() -> None:
    readme = (TEMPLATE_ROOT / "README.md").read_text()

    assert "copier copy --trust" in readme
    assert "uv run pytest" in readme
    assert "copier update --trust" in readme
    assert "GitHub Releases" in readme
    assert "does not publish to PyPI" in readme
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
uv run pytest tests/test_template_contract.py::test_template_readme_documents_generation_and_updates -v
```

Expected: FAIL because the repository README does not exist.

- [ ] **Step 3: Write repository documentation**

Create `README.md` with these sections and exact commands:

```markdown
# Python Project Template

A Copier template for Python 3.12+ projects using uv, pytest, Ruff, mypy,
pre-commit, and GitHub Actions.

## Generate a project

```bash
uv tool install copier
copier copy --trust /path/to/python-project-template my-project
```

`--trust` permits the template's only post-generation task: `uv lock`.

## Optional features

- Typer CLI
- Docker
- MkDocs Material
- GitHub Releases containing source and wheel artifacts

Release automation does not publish to PyPI.

## Develop the template

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
uv run pytest
```

## Update a generated project

Commit local project changes first, then run:

```bash
copier update --trust
```
```

After publishing the template repository, add its concrete GitHub shorthand as
a second example.

- [ ] **Step 4: Run documentation and full tests**

Run:

```bash
uv run pytest tests/test_template_contract.py -v
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_template_contract.py
git commit -m "docs: explain template generation and updates"
```

### Task 11: Add CI for the Template Repository

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `tests/test_template_contract.py`

- [ ] **Step 1: Write a failing template-CI test**

Append:

```python
def test_template_repository_has_ci() -> None:
    workflow = (TEMPLATE_ROOT / ".github/workflows/ci.yml").read_text()

    assert "uv run ruff check ." in workflow
    assert "uv run ruff format --check ." in workflow
    assert "uv run mypy tests" in workflow
    assert "uv run pytest" in workflow
    assert "docker" in workflow.lower()
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
uv run pytest tests/test_template_contract.py::test_template_repository_has_ci -v
```

Expected: FAIL because template CI does not exist.

- [ ] **Step 3: Add template CI**

Create `.github/workflows/ci.yml`:

```yaml
name: Template CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
          version: "0.11.19"
      - run: uv sync --locked
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy tests

  generated-projects:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"
          version: "0.11.19"
      - run: uv sync --locked
      - run: uv run pytest -v
      - name: Confirm Docker availability
        run: docker version
```

Use the same verified action SHAs as generated CI.

- [ ] **Step 4: Run all checks**

Run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
uv run pytest -v
```

Expected: PASS, with Docker build test PASS locally when Docker is available or
SKIP otherwise.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/ci.yml tests/test_template_contract.py
git commit -m "ci: validate template and generated projects"
```

### Task 12: Final Acceptance Verification

**Files:**
- Modify only files required by failures found during verification.

- [ ] **Step 1: Confirm no placeholders or unrendered template syntax**

Run:

```bash
rg -n "TBD|TODO|implement later|fill in details|\\[\\[" \
  --glob '!docs/superpowers/**' \
  --glob '!template/**'
```

Expected: no implementation placeholders. Template source naturally contains
`[[ ... ]]`; generated-project tests are responsible for proving those markers
do not survive rendering.

- [ ] **Step 2: Run repository quality checks from a clean environment**

Run:

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
```

Expected: PASS.

- [ ] **Step 3: Run all structural and executable tests**

Run:

```bash
uv run pytest -v
```

Expected: PASS. Docker may SKIP only if the executable is unavailable.

- [ ] **Step 4: Manually generate all required combinations**

Run the Copier CLI with canonical answers for:

```text
minimal: no options
full: CLI + Docker + docs + release
cli-only: CLI
docker-docs: Docker + docs
```

For each output, run:

```bash
uv lock --check
rg -n "\\[\\[|\\[%|\\{\\{" . --glob '!uv.lock'
```

Expected: `uv lock --check` passes; no Copier markers remain. `${{ ... }}`
matches are allowed only in GitHub workflow files.

- [ ] **Step 5: Review the rendered full project**

Confirm:

- The answers file contains `_src_path` and `_commit`.
- The release workflow has `contents: write` but no `id-token: write`.
- No generated file contains `uv publish`, PyPI credentials, or trusted
  publishing setup.
- Disabled features leave no empty directories or dependencies.
- README commands exactly match the rendered feature set.

- [ ] **Step 6: Commit verification fixes if needed**

```bash
git add .
git commit -m "fix: satisfy template acceptance checks"
```

Skip this commit when verification required no changes.

## Completion Criteria

- `copier copy --trust` generates all four required combinations.
- Generated projects retain `.copier-answers.yml` and support `copier update`.
- Minimal and full projects pass Ruff, mypy, pytest, and `uv build`.
- The full project passes `mkdocs build --strict`.
- Docker files are absent when disabled and build successfully when Docker is
  available.
- Release automation creates GitHub artifacts and contains no PyPI publishing
  permissions or commands.
- Template repository quality checks and pytest suite pass in GitHub Actions.
