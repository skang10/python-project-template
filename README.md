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
