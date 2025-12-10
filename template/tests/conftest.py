"""Pytest configuration for template validation tests."""

import shutil
import tempfile
from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options."""
    parser.addoption(
        "--full-matrix",
        action="store_true",
        default=False,
        help="Run full matrix tests (16 combinations)",
    )
    parser.addoption(
        "--keep-generated",
        action="store_true",
        default=False,
        help="Keep generated projects for inspection",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (full matrix)")
    config.addinivalue_line(
        "markers", "syntax_validation: marks tests that validate file syntax"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip slow tests unless --full-matrix is specified."""
    if config.getoption("--full-matrix"):
        return

    skip_slow = pytest.mark.skip(reason="Use --full-matrix to run full matrix tests")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def temp_dir(request: pytest.FixtureRequest) -> str:
    """Create a temporary directory for generated projects.

    If --keep-generated is specified, prints the directory path and does not clean up.
    """
    tmpdir = tempfile.mkdtemp(prefix="cookiecutter_test_")
    yield tmpdir

    if not request.config.getoption("--keep-generated"):
        shutil.rmtree(tmpdir, ignore_errors=True)
    else:
        print(f"\n  Generated project kept at: {tmpdir}")


@pytest.fixture
def template_dir() -> Path:
    """Return the path to the cookiecutter template directory."""
    # Tests are in template/tests/, template is in template/
    return Path(__file__).parent.parent


@pytest.fixture
def project_root() -> Path:
    """Return the path to the project root (where cookiecutter.json is)."""
    # Tests are in template/tests/, project root is template/
    return Path(__file__).parent.parent
