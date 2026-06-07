# Generated README Onboarding Design

## Objective

Make every generated project's README sufficient for a developer to set up,
verify, build, and use the project without consulting the template repository.

Instructions should remain concise and command-oriented. Extended tutorials,
deployment guidance, and troubleshooting are outside this change.

## Baseline Quick Start

Every generated README will explain:

1. Install `uv`, linking to the official installation documentation.
2. Install all project dependency groups with `uv sync --all-groups`.
3. Install Git hooks with `uv run pre-commit install`.
4. Immediately validate the repository with
   `uv run pre-commit run --all-files`.

The README will retain direct commands for:

- pytest
- Ruff linting
- Ruff formatting checks
- mypy
- Building source and wheel distributions with `uv build`

## Project Layout

Every generated README will briefly identify:

- `src/<package_name>/` as the application or library source directory
- `tests/` as the test directory
- `pyproject.toml` as project metadata and tool configuration
- `uv.lock` as the resolved dependency lockfile

Optional paths will appear only when their feature is enabled.

## Conditional Feature Guidance

### Typer CLI

When enabled, the README will show:

- How to display CLI help
- How to run the generated `hello` command
- Where the CLI implementation and tests live

### MkDocs Material

When enabled, the README will show:

- `uv run mkdocs serve` for local preview
- The local preview URL, `http://127.0.0.1:8000`
- `uv run mkdocs build --strict` for static generation
- That generated HTML is written to `site/`
- Where documentation source files and configuration live

### Docker

When enabled, the README will show:

- How to build the image
- How to run the image
- When CLI is also enabled, how to pass the generated CLI command and arguments
  to the container

### GitHub Releases

When enabled, the README will show:

- How to create and push a version tag
- That the workflow validates and builds the project
- Where source and wheel artifacts appear in GitHub Releases
- That the workflow does not publish to PyPI

## Conditional Rendering

Disabled features will leave no feature-specific README headings, commands, or
file references. The minimal generated README will contain only the baseline
setup, project layout, quality, and build guidance.

## Testing

Template contract tests will render minimal and feature-enabled projects and
assert that:

- Baseline setup and pre-commit commands always appear.
- Project-layout guidance uses the generated package name.
- Each enabled feature includes its expected commands and paths.
- Disabled features leave no corresponding guidance.
- Existing generated-project quality and build tests continue to pass.

## Acceptance Criteria

1. A developer can set up a generated project using only its README.
2. Pre-commit installation and an immediate all-files run are documented.
3. The source, tests, configuration, and lockfile locations are explained.
4. Every enabled optional feature has a concise operational quick start.
5. Documentation preview URL and static HTML output location are explicit.
6. Disabled feature instructions are absent.
