# General-Purpose Python Project Template Design

## Objective

Build a Copier template for creating modern, general-purpose Python projects
without repeatedly assembling packaging, quality, testing, CI, and optional
delivery tooling.

Generated projects must work independently after creation. Copier is required
to generate or update a project, but it is not a runtime or development
dependency of the generated project.

## Chosen Approach

Use one Copier template with conditional Jinja rendering. A single template
keeps the common Python setup consistent while feature flags include only the
files and dependencies selected by the user.

Separate project-type templates are out of scope because they would duplicate
the shared configuration. Post-generation add-on scripts are also out of scope
because they would make feature combinations and template updates harder to
test and maintain.

## Supported Environment

- Python 3.12 or newer
- `uv` for virtual environments, dependency resolution, locking, and command
  execution
- GitHub as the CI and release platform
- MIT as the default license
- A `src/` package layout

## Template Structure

The template repository will contain:

- `copier.yml` for questions, defaults, validation, and computed values
- `template/` for the generated project tree
- Template tests that render and validate representative feature combinations
- GitHub Actions for testing the template itself
- Documentation explaining generation, local development, and template updates

The generated project will contain a normalized distribution name and a valid
Python import package name. The package name will default from the project name
but remain editable during generation.

## Generation Questions

Copier will ask for:

- Project name
- Distribution name
- Import package name
- Short project description
- Author name
- Author email
- GitHub repository owner
- GitHub repository name
- Whether to include a Typer CLI
- Whether to include Docker support
- Whether to include a MkDocs Material documentation site
- Whether to include GitHub release automation

The template will validate package and repository identifiers before rendering.
Optional questions will use clear defaults, with optional features disabled by
default to keep a newly generated project small.

## Always-Included Baseline

Every generated project will include:

- A PEP 621 `pyproject.toml`
- A `src/<package_name>/` package
- A matching `tests/` test suite
- `README.md`, `.gitignore`, `.python-version`, and MIT `LICENSE`
- Ruff for linting and formatting
- mypy for static type checking
- pytest for tests
- pre-commit for local quality checks
- GitHub Actions for linting, formatting checks, type checks, and tests
- Build-system configuration so source and wheel distributions can be built
- A committed `uv.lock` generated after project creation

The generated starter package will contain a version value and a small,
testable public function so the initial test suite verifies real package
imports rather than an empty placeholder.

## Optional Features

### Typer CLI

When selected, the project will include:

- Typer as an application dependency
- A focused CLI module under the package
- A console-script entry point in `pyproject.toml`
- CLI tests using Typer's test runner
- README usage examples

When not selected, none of these dependencies, files, entry points, or examples
will be rendered.

### Docker

When selected, the project will include:

- A production-oriented `Dockerfile`
- A `.dockerignore`
- Documentation for building and running the image

The image will use Python 3.12 and `uv`, install from the lock file, run as a
non-root user, and default to running the package's CLI when the CLI feature is
enabled. Without the CLI feature, it will default to running Python and can be
overridden by the consumer.

### MkDocs Material

When selected, the project will include:

- MkDocs and Material for MkDocs in a documentation dependency group
- `mkdocs.yml`
- A small `docs/` site with an index and usage page
- Commands for serving and building documentation
- A CI check that builds the documentation with strict mode

Documentation deployment is not included. The feature verifies that the site
builds but leaves hosting decisions to each generated project.

### GitHub Release Artifacts

When selected, the project will include a GitHub Actions workflow triggered by
version tags. It will:

1. Run the quality and test suite.
2. Build source and wheel distributions.
3. Validate the distributions.
4. Create a GitHub Release and attach the built artifacts.

The workflow will not publish to PyPI and will not request PyPI credentials or
trusted-publishing permissions.

## Developer Workflows

The generated README will document direct, cross-platform `uv` commands:

```bash
uv sync --all-groups
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pre-commit install
uv build
```

Optional feature commands will appear only when relevant. A Makefile or
third-party task runner will not be required; direct `uv` commands keep the
workflow portable and reduce template dependencies.

## Continuous Integration

Generated-project CI will run on supported GitHub-hosted environments and use
Python 3.12. Separate jobs will expose failures for:

- Ruff linting
- Ruff formatting
- mypy
- pytest
- Documentation strict build, when selected

Dependency installation will use the committed `uv.lock` in frozen mode so CI
tests the resolved environment checked into the repository.

## Template Testing

Automated template tests will generate at least these combinations:

- Minimal project with no optional features
- Full project with every optional feature
- CLI-only project
- Docker and documentation project

Tests will verify:

- Copier completes successfully.
- Expected files and dependencies are present.
- Unselected files and dependencies are absent.
- `pyproject.toml` and other structured configuration are valid.
- No unrendered Jinja expressions remain.
- Package and distribution naming are rendered consistently.

The minimal and full variants will additionally run dependency synchronization,
Ruff, mypy, pytest, package builds, and any selected documentation checks.
Docker configuration will be structurally tested in normal CI; an image build
may be included where Docker is available.

## Template Update Support

The repository will retain Copier's answers file in generated projects so
consumers can run Copier's update workflow later. Template files will avoid
unnecessary generated timestamps or unstable content, reducing merge conflicts
when projects adopt newer template versions.

## Error Handling

- Copier validation will reject invalid import package names and malformed
  repository identifiers before files are generated.
- Template tests will fail on missing, unexpected, or partially rendered files.
- All local and CI commands will rely on non-zero process exit codes.
- CI quality checks will be separated so failures identify the responsible
  tool directly.
- Release automation will stop before creating a release if tests, builds, or
  distribution validation fail.

## Scope Boundaries

The first version will not include:

- Web-framework-specific scaffolding
- Database configuration
- Cloud deployment manifests
- PyPI publishing
- Documentation deployment
- Multiple dependency-manager choices
- Python versions older than 3.12
- A plugin system for post-generation features

These can be considered later only when a concrete generated project requires
them.

## Acceptance Criteria

The template is complete when:

1. A user can generate a valid project interactively with Copier.
2. Every documented feature combination renders without leftover template
   syntax.
3. The minimal and full generated projects pass their documented linting,
   formatting, typing, testing, and build commands.
4. Each optional feature is absent when disabled and operational when enabled.
5. Generated CI reflects the selected features.
6. Optional release automation creates GitHub release artifacts without any
   PyPI publishing configuration.
7. Copier update metadata is retained and documented.
