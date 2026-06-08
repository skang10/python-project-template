# Switch release automation to release-please

## Goal

Replace the current manual `git tag vX.Y.Z && git push` release flow with
[release-please](https://github.com/googleapis/release-please), which derives
version bumps and changelogs from Conventional Commit messages on `main` and
opens a "release PR" that, once merged, creates the tag and GitHub release
automatically.

This is a full replacement: the manual tagging instructions are removed from
the generated README, and `release-please` becomes the only release path.

## Files

All new/changed files live under `template/` and remain gated by the existing
`include_release` Copier option.

1. **Replace** `.github/workflows/[% if include_release %]release.yml[% endif %].jinja`
   with `.github/workflows/[% if include_release %]release-please.yml[% endif %].jinja`.
2. **Add** `[% if include_release %]release-please-config.json[% endif %].jinja`
   — manifest-mode config: `release-type: python`, single root package (`"."`).
3. **Add** `[% if include_release %].release-please-manifest.json[% endif %].jinja`
   — seeds the tracked version at `0.1.0`, matching the `version` field in
   `pyproject.toml.jinja`.
4. **Update** `README.md.jinja`'s `## Releases` section to describe the new
   PR-based flow and note the Conventional Commits requirement.

## Workflow design

Trigger: `push` to `main` (not tags — release-please manages tags itself).

Permissions: `contents: write`, `pull-requests: write`.

### Job 1: `release-please`

Runs `googleapis/release-please-action` (pinned to a specific commit SHA, per
this repo's existing convention for third-party actions). It:

- Scans commits since the last release for Conventional Commit prefixes
  (`feat:`, `fix:`, `chore:`, etc.).
- Maintains an open PR that bumps the version in `pyproject.toml` and updates
  `CHANGELOG.md` (created on first run).
- When that PR is merged, tags the merge commit and creates the GitHub
  release with generated notes.

Exposes `release_created` (bool) and `tag_name` outputs for the next job.

### Job 2: `build`

`needs: release-please`, gated on
`if: needs.release-please.outputs.release_created == 'true'`. Mirrors the
quality/build steps from the current `release.yml`:

- Checkout (the tagged commit), `astral-sh/setup-uv`, `uv sync --locked --all-groups`
- `ruff check`, `ruff format --check`, `mypy src`, `pytest`
- `uv build`, `uv run twine check dist/*`
- `gh release upload "${{ needs.release-please.outputs.tag_name }}" dist/*`
  to attach the wheel/sdist to the release release-please already created
  (replaces the old `gh release create ... dist/* --generate-notes`, since
  release-please now owns release creation and notes).

## README changes

Replace the "Create and push a version tag" instructions in `## Releases`
with:

- An explanation that merging commits to `main` with Conventional Commit
  messages drives an automatically maintained "Release PR"; merging that PR
  cuts the release.
- A short note on the Conventional Commits convention (`feat:` → minor,
  `fix:` → patch, `feat!:`/`BREAKING CHANGE:` → major) so users know how to
  influence version bumps.

## Out of scope

- No commit-lint enforcement (CI job or pre-commit hook) is added — the
  convention is documented only, keeping the template's tooling minimal.
- No changes to `ci.yml` or other workflows.
