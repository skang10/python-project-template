# Python Project Template

A Copier template for Python 3.12+ projects using uv, pytest, Ruff, mypy,
pre-commit, and GitHub Actions.

## Generate A Project

Install Copier and generate a project from this repository:

```bash
uv tool install copier
copier copy --trust /path/to/python-project-template my-project
```

`--trust` permits the template's only post-generation task: `uv lock`.

Copier then asks a series of questions one at a time, e.g.:

```
🎤 Human-readable project name
```

This is your cue to type an answer and press Enter — Copier is waiting on
you, not stuck. Answer **"Human-readable project name"** with an actual name
(e.g. `My Project`); leaving it blank causes a validation error on the next
question, since `distribution_name` and `package_name` derive their defaults
from it.

## Optional Features

- Typer CLI
- Docker
- MkDocs Material
- GitHub Releases containing source and wheel artifacts

Release automation does not publish to PyPI.

## Develop The Template

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
uv run pytest
```

## Update A Generated Project

Commit local project changes first, then run:

```bash
copier update --trust
```
