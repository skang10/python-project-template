# Generated README Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand each generated project's README with a complete concise quick start for uv, pre-commit, project layout, and every selected optional feature.

**Architecture:** Keep all user-facing onboarding in `template/README.md.jinja`, using the template's existing Copier conditionals so disabled features leave no instructions. Extend `tests/test_template_contract.py` to assert both required content and feature-specific absence, then run the existing generated-project integration suite unchanged.

**Tech Stack:** Copier, Jinja, Markdown, pytest, uv

---

## File Map

- Modify `template/README.md.jinja`: Add baseline onboarding, repository layout,
  and expanded conditional quick starts.
- Modify `tests/test_template_contract.py`: Verify baseline commands and paths,
  enabled feature instructions, and disabled feature absence.
- Verify `tests/test_generated_projects.py`: Confirm README-only changes do not
  break generated-project linting, typing, tests, builds, docs, or Docker.

### Task 1: Add Baseline uv, Pre-Commit, and Layout Onboarding

**Files:**
- Modify: `tests/test_template_contract.py`
- Modify: `template/README.md.jinja`

- [ ] **Step 1: Expand the baseline README contract**

In `test_minimal_project_has_quality_workflows`, add these required strings to
the command tuple:

```python
        "uv run pre-commit run --all-files",
```

After the existing command loop, add:

```python
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
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```bash
uv run python -m pytest \
  tests/test_template_contract.py::test_minimal_project_has_quality_workflows -v
```

Expected: FAIL because the README does not contain the all-files pre-commit
command, installation URL, or project layout.

- [ ] **Step 3: Replace the baseline README sections**

Update the beginning of `template/README.md.jinja` through the Build section to:

```markdown
# [[ project_name ]]

[[ project_description ]]

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Setup

Install all dependency groups and configure the Git hooks:

```bash
uv sync --all-groups
uv run pre-commit install
uv run pre-commit run --all-files
```

## Project Layout

- `src/[[ package_name ]]/`: project source code
- `tests/`: automated tests
- `pyproject.toml`: project metadata, dependencies, and tool configuration
- `uv.lock`: resolved dependency lockfile

## Quality

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Build

Build source and wheel distributions into `dist/`:

```bash
uv build
```
```

Keep the existing conditional feature sections below this baseline for Task 2.

- [ ] **Step 4: Run baseline and static checks**

Run:

```bash
uv run python -m pytest \
  tests/test_template_contract.py::test_minimal_project_has_quality_workflows -v
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add template/README.md.jinja tests/test_template_contract.py
git commit -m "docs: expand generated project quick start"
```

### Task 2: Expand Conditional Feature Quick Starts

**Files:**
- Modify: `tests/test_template_contract.py`
- Modify: `template/README.md.jinja`

- [ ] **Step 1: Add failing CLI documentation assertions**

In `test_cli_feature_is_conditional`, assign both README values:

```python
    minimal_readme = (minimal / "README.md").read_text()
    cli_readme = (cli / "README.md").read_text()
```

Replace the existing README assertion and add absence checks:

```python
    assert "## CLI" not in minimal_readme
    assert "`src/example_project/cli.py`" not in minimal_readme
    assert "uv run example-project --help" in cli_readme
    assert "uv run example-project hello World" in cli_readme
    assert "`src/example_project/cli.py`" in cli_readme
    assert "`tests/test_cli.py`" in cli_readme
```

- [ ] **Step 2: Add failing documentation assertions**

In `test_docs_feature_is_conditional`, assign:

```python
    minimal_readme = (minimal / "README.md").read_text()
    docs_readme = (docs / "README.md").read_text()
```

Replace the current README assertion and add:

```python
    assert "## Documentation" not in minimal_readme
    assert "http://127.0.0.1:8000" not in minimal_readme
    assert "uv run mkdocs serve" in docs_readme
    assert "http://127.0.0.1:8000" in docs_readme
    assert "uv run mkdocs build --strict" in docs_readme
    assert "`site/`" in docs_readme
    assert "`docs/`" in docs_readme
    assert "`mkdocs.yml`" in docs_readme
```

- [ ] **Step 3: Add failing Docker assertions**

In `test_docker_feature_is_conditional`, render the README strings:

```python
    minimal_readme = (minimal / "README.md").read_text()
    docker_readme = (docker / "README.md").read_text()
    docker_cli_readme = (docker_cli / "README.md").read_text()
```

Add:

```python
    assert "## Docker" not in minimal_readme
    assert "docker build -t example-project ." in docker_readme
    assert "docker run --rm example-project" in docker_readme
    assert "docker run --rm example-project hello World" in docker_cli_readme
```

- [ ] **Step 4: Add failing release assertions**

In `test_release_feature_creates_github_artifacts_only`, assign:

```python
    minimal_readme = (minimal / "README.md").read_text()
    release_readme = (release / "README.md").read_text()
```

Add:

```python
    assert "## Releases" not in minimal_readme
    assert "git tag v0.1.0" in release_readme
    assert "git push origin v0.1.0" in release_readme
    assert "GitHub Releases" in release_readme
    assert "does not publish to PyPI" in release_readme
```

- [ ] **Step 5: Run feature contract tests and verify they fail**

Run:

```bash
uv run python -m pytest \
  tests/test_template_contract.py::test_cli_feature_is_conditional \
  tests/test_template_contract.py::test_docs_feature_is_conditional \
  tests/test_template_contract.py::test_docker_feature_is_conditional \
  tests/test_template_contract.py::test_release_feature_creates_github_artifacts_only \
  -v
```

Expected: FAIL on the newly required help, path, preview URL, static output,
container CLI, and tag commands.

- [ ] **Step 6: Expand the CLI section**

Replace the CLI conditional in `template/README.md.jinja` with:

```markdown
[% if include_cli %]
## CLI

The Typer application lives in `src/[[ package_name ]]/cli.py`, with tests in
`tests/test_cli.py`.

```bash
uv run [[ distribution_name ]] --help
uv run [[ distribution_name ]] hello World
```
[% endif %]
```

- [ ] **Step 7: Expand the documentation section**

Replace the documentation conditional with:

```markdown
[% if include_docs %]
## Documentation

Documentation source lives in `docs/` and site configuration lives in
`mkdocs.yml`.

Start the live preview:

```bash
uv run mkdocs serve
```

Open `http://127.0.0.1:8000`.

Build static HTML into `site/`:

```bash
uv run mkdocs build --strict
```
[% endif %]
```

- [ ] **Step 8: Expand the Docker section**

Replace the Docker conditional with:

```markdown
[% if include_docker %]
## Docker

Build and run the image:

```bash
docker build -t [[ distribution_name ]] .
docker run --rm [[ distribution_name ]]
```

[% if include_cli %]
Pass CLI commands and arguments after the image name:

```bash
docker run --rm [[ distribution_name ]] hello World
```
[% endif %]
[% endif %]
```

- [ ] **Step 9: Expand the release section**

Replace the release conditional with:

```markdown
[% if include_release %]
## Releases

Create and push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow runs the quality checks, builds source and wheel
distributions, and attaches them to GitHub Releases. It does not publish to
PyPI.
[% endif %]
```

- [ ] **Step 10: Run feature contract and static checks**

Run:

```bash
uv run python -m pytest \
  tests/test_template_contract.py::test_cli_feature_is_conditional \
  tests/test_template_contract.py::test_docs_feature_is_conditional \
  tests/test_template_contract.py::test_docker_feature_is_conditional \
  tests/test_template_contract.py::test_release_feature_creates_github_artifacts_only \
  -v
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
```

Expected: PASS.

- [ ] **Step 11: Run the full generated-project suite**

Run:

```bash
uv run python -m pytest -v
```

Expected: all contract and generated-project tests PASS, including Docker when
available.

- [ ] **Step 12: Commit**

```bash
git add template/README.md.jinja tests/test_template_contract.py
git commit -m "docs: document optional generated project features"
```

## Final Verification

Run:

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy tests
uv run python -m pytest -q
git status --short
```

Expected:

- Ruff, formatting, and mypy pass.
- All tests pass.
- `git status --short` is empty after commits.
