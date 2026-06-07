from pathlib import Path
from typing import Any

from conftest import render_project


def test_minimal_project_renders(
    tmp_path: Path,
    default_answers: dict[str, Any],
) -> None:
    project = render_project(tmp_path / "minimal", default_answers)

    assert (project / "pyproject.toml").is_file()
    assert (project / "src/example_project/__init__.py").is_file()
    assert (project / "tests/test_package.py").is_file()
    assert (project / ".copier-answers.yml").is_file()
