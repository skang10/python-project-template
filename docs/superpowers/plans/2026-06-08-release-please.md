# Release-Please Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the manual `git tag` release flow in the generated project template with release-please, which automates version bumps, changelogs, and GitHub release creation from Conventional Commits.

**Architecture:** Two-job workflow triggered on push to `main` — `release-please` manages the release PR and tags via `googleapis/release-please-action`; a `build` job runs only when a release is actually created and attaches wheel/sdist artifacts. Two JSON config files (`release-please-config.json`, `.release-please-manifest.json`) provide the manifest-mode config release-please-action requires. All files remain gated by the existing `include_release` Copier option.

**Tech Stack:** `googleapis/release-please-action@v5.0.0` (SHA `45996ed1f6d02564a971a2fa1b5860e934307cf7`), existing `actions/checkout` and `astral-sh/setup-uv` pins from `ci.yml.jinja`, Copier jinja template syntax (`[% if %]`/`[[ ]]`).

---

## File Map

| Action | Path |
|--------|------|
| Delete | `template/.github/workflows/[% if include_release %]release.yml[% endif %].jinja` |
| Create | `template/.github/workflows/[% if include_release %]release-please.yml[% endif %].jinja` |
| Create | `template/[% if include_release %]release-please-config.json[% endif %].jinja` |
| Create | `template/[% if include_release %].release-please-manifest.json[% endif %].jinja` |
| Modify | `template/README.md.jinja` — `## Releases` section |
| Modify | `tests/test_template_contract.py` — `test_release_feature_creates_github_artifacts_only` |

---

### Task 1: Update the release feature test (TDD — write the failing test first)

**Files:**
- Modify: `tests/test_template_contract.py` (lines ~193–222, the `test_release_feature_creates_github_artifacts_only` function)

- [ ] **Step 1: Replace the test body**

Open `tests/test_template_contract.py` and replace `test_release_feature_creates_github_artifacts_only` with:

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
```

- [ ] **Step 2: Add `import json` at the top of the test file**

The test file imports at the top of `tests/test_template_contract.py` currently read:
```python
import subprocess
import tomllib
from pathlib import Path
from typing import Any
```

Add `import json` after `import subprocess`:
```python
import json
import subprocess
import tomllib
from pathlib import Path
from typing import Any
```

- [ ] **Step 3: Run the test to confirm it fails for the right reason**

```bash
uv run pytest tests/test_template_contract.py::test_release_feature_creates_github_artifacts_only -v
```

Expected: FAIL — `FileNotFoundError` or `AssertionError` when it can't find `release-please.yml` (because `release.yml` still exists and has no `release-please.yml`).

- [ ] **Step 4: Commit the failing test**

```bash
git checkout -b feat/release-please
git add tests/test_template_contract.py
git commit -m "test: update release feature assertions for release-please"
```

---

### Task 2: Create the release-please config files

**Files:**
- Create: `template/[% if include_release %]release-please-config.json[% endif %].jinja`
- Create: `template/[% if include_release %].release-please-manifest.json[% endif %].jinja`

- [ ] **Step 1: Create `release-please-config.json`**

Create `template/[% if include_release %]release-please-config.json[% endif %].jinja` with:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    ".": {
      "release-type": "python"
    }
  }
}
```

Note: no jinja variables needed — all values are static.

- [ ] **Step 2: Create `.release-please-manifest.json`**

Create `template/[% if include_release %].release-please-manifest.json[% endif %].jinja` with:

```json
{
  ".": "0.1.0"
}
```

This seeds the manifest at the same version as `pyproject.toml`. release-please will update both files when it cuts a release.

- [ ] **Step 3: Run the test to confirm config assertions now pass**

```bash
uv run pytest tests/test_template_contract.py::test_release_feature_creates_github_artifacts_only -v
```

Expected: still FAIL, but the `AssertionError` should now be past the config file checks — it should fail on something about the workflow (e.g., `release-please.yml` not existing yet).

- [ ] **Step 4: Commit**

```bash
git add "template/[% if include_release %]release-please-config.json[% endif %].jinja" \
        "template/[% if include_release %].release-please-manifest.json[% endif %].jinja"
git commit -m "feat: add release-please manifest config files to template"
```

---

### Task 3: Create the release-please workflow and delete the old one

**Files:**
- Delete: `template/.github/workflows/[% if include_release %]release.yml[% endif %].jinja`
- Create: `template/.github/workflows/[% if include_release %]release-please.yml[% endif %].jinja`

- [ ] **Step 1: Delete the old `release.yml` template**

```bash
git rm "template/.github/workflows/[% if include_release %]release.yml[% endif %].jinja"
```

- [ ] **Step 2: Create the new `release-please.yml` template**

Create `template/.github/workflows/[% if include_release %]release-please.yml[% endif %].jinja` with:

```yaml
name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}
    steps:
      - uses: googleapis/release-please-action@45996ed1f6d02564a971a2fa1b5860e934307cf7 # v5.0.0
        id: release
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json

  build:
    needs: release-please
    if: ${{ needs.release-please.outputs.release_created == 'true' }}
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
      - name: Upload release artifacts
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh release upload "${{ needs.release-please.outputs.tag_name }}" dist/*
```

Note: `${{` and `}}` are GitHub Actions expression syntax — Copier's jinja delimiters are `[[`/`]]` and `[%`/`%]`, so there is no conflict.

- [ ] **Step 3: Run the test — workflow assertions should now pass**

```bash
uv run pytest tests/test_template_contract.py::test_release_feature_creates_github_artifacts_only -v
```

Expected: FAIL, but now only the README assertions should remain (the test should pass all workflow checks and fail on `"git tag v0.1.0" not in release_readme` or `"Conventional Commit" in release_readme`).

- [ ] **Step 4: Commit**

```bash
git add "template/.github/workflows/[% if include_release %]release-please.yml[% endif %].jinja"
git commit -m "feat: replace tag-push release workflow with release-please"
```

---

### Task 4: Update the generated README's Releases section

**Files:**
- Modify: `template/README.md.jinja` — the `## Releases` section (currently lines 96–108)

- [ ] **Step 1: Replace the `## Releases` section**

The current `[% if include_release %]` block in `template/README.md.jinja` reads:

```jinja
[% if include_release %]
## Releases

Create and push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow runs the quality checks, builds source and wheel
distributions, and attaches them to GitHub Releases. It does not publish to PyPI.
[% endif %]
```

Replace with:

```jinja
[% if include_release %]
## Releases

This project uses [release-please](https://github.com/googleapis/release-please)
to automate releases. Commit to `main` using
[Conventional Commits](https://www.conventionalcommits.org/) and release-please
will maintain an open "Release PR" that tracks unreleased changes:

- `fix:` commits → patch version bump (e.g. `0.1.0` → `0.1.1`)
- `feat:` commits → minor version bump (e.g. `0.1.0` → `0.2.0`)
- `feat!:` or `BREAKING CHANGE:` footer → major version bump (e.g. `0.1.0` → `1.0.0`)

Merging the Release PR cuts the release: release-please tags the commit, creates
the GitHub release with a generated changelog, and the build job attaches the
source and wheel distributions. It does not publish to PyPI.
[% endif %]
```

- [ ] **Step 2: Run the full test suite**

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: all tests pass, including `test_release_feature_creates_github_artifacts_only`.

- [ ] **Step 3: Run the full suite to catch any regressions**

```bash
uv run pytest -v
```

Expected: all tests pass (skip `test_generated_project_quality_suite` if it's slow — it's an integration test that actually runs `uv build` etc. in a temp dir).

- [ ] **Step 4: Commit**

```bash
git add template/README.md.jinja
git commit -m "docs: update Releases section to describe release-please PR flow"
```

---

### Task 5: Final verification and push

- [ ] **Step 1: Run linting and type checks on the test suite**

```bash
uv run ruff check tests/
uv run ruff format --check tests/
uv run mypy tests
```

Expected: no errors. If `mypy` complains about `import json` being unused or `Any` type, check that `import json` was added in Task 1 Step 2.

- [ ] **Step 2: Run the full test suite one final time**

```bash
uv run pytest tests/test_template_contract.py -v
```

Expected: all 10+ tests pass, none skipped except possibly the Docker integration test.

- [ ] **Step 3: Push and open a PR**

```bash
git push -u origin feat/release-please
gh pr create \
  --title "feat: switch release automation to release-please" \
  --body "Replaces the manual git-tag release flow with release-please.

## Changes
- New \`release-please.yml\` workflow: triggered on push to \`main\`, runs release-please-action then conditionally builds and uploads dist artifacts
- \`release-please-config.json\` and \`.release-please-manifest.json\` seeded at 0.1.0
- \`README.md.jinja\` Releases section updated to describe the PR-based flow and Conventional Commits convention
- Test updated to assert new workflow structure

Does not publish to PyPI."
```
