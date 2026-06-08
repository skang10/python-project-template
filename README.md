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

Copier then asks a series of questions one at a time. Each `🎤` line is a
prompt waiting for your input — type an answer and press Enter (Copier is
waiting on you, not stuck):

```
$ copier copy --trust python-project-template my-project
No git tags found in template; using HEAD as ref
🎤 Human-readable project name
   My Project
🎤 Package distribution name
   my-project
🎤 Python import package name
   my_project
🎤 project_description
   A demo project
🎤 author_name
   Jane Doe
🎤 author_email
   jane@example.com
🎤 github_owner
   janedoe
🎤 github_repository
   my-project
🎤 include_cli (bool)
   Yes
🎤 include_docker (bool)
   No
🎤 include_docs (bool)
   Yes
🎤 include_release (bool)
   No
```

Leaving **"Human-readable project name"** blank causes a validation error on
the next question, since `distribution_name` and `package_name` derive their
defaults from it.

To skip the prompts, answer non-interactively with `--data`:

```bash
copier copy --trust --data project_name="My Project" --data include_docker=false \
  /path/to/python-project-template my-project
```

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

To change an answer (e.g. enable Docker after the fact), pass `--data`:

```bash
copier update --trust --data include_docker=true
```
