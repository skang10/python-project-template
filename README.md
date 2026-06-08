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

Run the update from inside the *generated* project (not this template repo) — Copier
reads `.copier-answers.yml` there to find the template source and your prior answers.
Check that file if you want to see what answers will be reused.

Commit local project changes first, then run:

```bash
copier update --trust
```

To change an answer (e.g. enable Docker after the fact), pass `--data`:

```bash
copier update --trust --data include_docker=true
```
