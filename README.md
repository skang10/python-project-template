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

## Generated Project Structure

Here's `my-project` generated with every optional feature enabled (package name
`my_project`):

```
my-project/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml          # include_release
├── docs/                        # include_docs
│   ├── index.md
│   └── usage.md
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── cli.py               # include_cli
├── tests/
│   ├── test_cli.py              # include_cli
│   └── test_package.py
├── .copier-answers.yml
├── .dockerignore                # include_docker
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── Dockerfile                   # include_docker
├── LICENSE
├── mkdocs.yml                   # include_docs
├── pyproject.toml
├── README.md
└── uv.lock
```

Files marked with a comment only appear when the corresponding option is
enabled; declining an option omits its files entirely rather than leaving them
empty.

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
