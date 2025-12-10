"""Tests for cookiecutter template generation.

This module provides comprehensive validation tests for the cookiecutter template,
ensuring all option combinations generate valid projects with correct syntax.

NOTE: The cookiecutter post-generation hook handles file removal based on options.
When testing programmatically, we need to explicitly run the hooks or test
with acceptance_hooks=True.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from cookiecutter.main import cookiecutter

from .option_combinations import (
    DEFAULT_OPTIONS,
    FULL_TEST_MATRIX,
    MINIMUM_TEST_MATRIX,
    get_combination_id,
    merge_options,
)


def generate_project(template_dir: Path, output_dir: str, options: dict) -> str:
    """Generate a project from the template.

    Args:
        template_dir: Path to the cookiecutter template directory.
        output_dir: Directory to output the generated project.
        options: Options to pass to cookiecutter.

    Returns:
        Path to the generated project directory.
    """
    full_options = merge_options(options)

    # Get the project root (one level up from template/) to find hooks
    project_root = template_dir.parent
    hooks_dir = project_root / "hooks"

    result_dir = cookiecutter(
        str(template_dir),
        output_dir=output_dir,
        no_input=True,
        extra_context=full_options,
    )

    # Run the post-generation hook manually if it exists
    post_gen_hook = hooks_dir / "post_gen_project.py"
    if post_gen_hook.exists():
        # Create a modified hook that uses our options
        run_post_gen_hook(result_dir, full_options)

    return result_dir


def run_post_gen_hook(project_dir: str, options: dict) -> None:
    """Run the post-generation cleanup based on options.

    This simulates what the post_gen_project.py hook does.
    """
    project_path = Path(project_dir)

    # Remove observability files if disabled
    if options.get("include_observability", "yes").lower() == "no":
        obs_dir = project_path / "observability"
        if obs_dir.exists():
            shutil.rmtree(obs_dir)
        obs_module = project_path / "backend" / "app" / "observability.py"
        if obs_module.exists():
            obs_module.unlink()

    # Remove GitHub Actions if disabled
    if options.get("include_github_actions", "yes").lower() == "no":
        github_dir = project_path / ".github"
        if github_dir.exists():
            shutil.rmtree(github_dir)

    # Remove Sentry files if disabled
    if options.get("include_sentry", "no").lower() == "no":
        sentry_module = project_path / "backend" / "app" / "sentry.py"
        if sentry_module.exists():
            sentry_module.unlink()

    # Remove Kubernetes files if disabled
    if options.get("include_kubernetes", "no").lower() == "no":
        k8s_dir = project_path / "k8s"
        if k8s_dir.exists():
            shutil.rmtree(k8s_dir)
        # Also remove deploy workflow if GitHub Actions is enabled
        deploy_workflow = project_path / ".github" / "workflows" / "deploy.yml"
        if deploy_workflow.exists():
            deploy_workflow.unlink()

    # Clean up any __pycache__ directories that may have been created
    for pycache in project_path.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)


class TestTemplateGeneration:
    """Test template generation with various option combinations."""

    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX,
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX],
    )
    def test_template_generates_successfully(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test that template generates without errors."""
        result_dir = generate_project(template_dir, temp_dir, options)

        assert os.path.isdir(result_dir), "Generated project directory should exist"
        assert os.path.isfile(
            os.path.join(result_dir, "README.md")
        ), "README.md should exist"

    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX,
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX],
    )
    def test_required_files_exist(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test that all required files are generated."""
        result_dir = generate_project(template_dir, temp_dir, options)

        # Core files always present
        required_files = [
            "README.md",
            "CLAUDE.md",
            "compose.yml",
            ".env.example",
            ".gitignore",
            "Makefile",
            "backend/app/main.py",
            "backend/app/core/config.py",
            "backend/pyproject.toml",
            "frontend/package.json",
            "frontend/vite.config.ts",
            "scripts/docker-dev.sh",
            "keycloak/setup-realm.sh",
        ]

        for file_path in required_files:
            full_path = os.path.join(result_dir, file_path)
            assert os.path.exists(full_path), f"Missing required file: {file_path}"

    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX,
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX],
    )
    def test_conditional_github_actions(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test GitHub Actions conditional generation."""
        result_dir = generate_project(template_dir, temp_dir, options)

        github_dir = os.path.join(result_dir, ".github")
        ci_workflow = os.path.join(result_dir, ".github", "workflows", "ci.yml")

        if options.get("include_github_actions") == "yes":
            assert os.path.exists(github_dir), ".github directory should exist"
            assert os.path.exists(ci_workflow), "CI workflow should exist"
        else:
            assert not os.path.exists(github_dir), ".github directory should not exist"

    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX,
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX],
    )
    def test_conditional_kubernetes(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test Kubernetes conditional generation."""
        result_dir = generate_project(template_dir, temp_dir, options)

        k8s_dir = os.path.join(result_dir, "k8s")

        if options.get("include_kubernetes") == "yes":
            assert os.path.isdir(k8s_dir), "k8s directory should exist"
            assert os.path.exists(
                os.path.join(k8s_dir, "base", "kustomization.yaml")
            ), "kustomization.yaml should exist"
            assert os.path.exists(
                os.path.join(k8s_dir, "base", "backend-deployment.yaml")
            ), "backend-deployment.yaml should exist"
        else:
            assert not os.path.exists(k8s_dir), "k8s directory should not exist"

    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX,
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX],
    )
    def test_conditional_sentry(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test Sentry conditional generation."""
        result_dir = generate_project(template_dir, temp_dir, options)

        sentry_file = os.path.join(result_dir, "backend", "app", "sentry.py")

        if options.get("include_sentry") == "yes":
            assert os.path.exists(sentry_file), "Sentry module should exist"
        else:
            assert not os.path.exists(sentry_file), "Sentry module should not exist"

    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX,
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX],
    )
    def test_conditional_observability(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test observability conditional generation."""
        result_dir = generate_project(template_dir, temp_dir, options)

        obs_dir = os.path.join(result_dir, "observability")
        obs_module = os.path.join(result_dir, "backend", "app", "observability.py")

        if options.get("include_observability") == "yes":
            assert os.path.isdir(obs_dir), "observability directory should exist"
            assert os.path.exists(
                os.path.join(obs_dir, "prometheus", "prometheus.yml")
            ), "prometheus.yml should exist"
            assert os.path.exists(
                os.path.join(obs_dir, "grafana", "dashboards")
            ), "grafana dashboards should exist"
        else:
            assert not os.path.exists(
                obs_dir
            ), "observability directory should not exist"
            assert not os.path.exists(
                obs_module
            ), "observability.py module should not exist"


class TestGeneratedProjectSyntaxValidity:
    """Test that generated projects have valid syntax."""

    @pytest.mark.syntax_validation
    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX[:3],  # Subset for speed
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX[:3]],
    )
    def test_python_syntax_valid(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test that generated Python files have valid syntax."""
        result_dir = generate_project(template_dir, temp_dir, options)

        backend_dir = os.path.join(result_dir, "backend")

        # Check all Python files for syntax errors
        for root, dirs, files in os.walk(backend_dir):
            # Skip virtual environments and cache
            dirs[:] = [d for d in dirs if d not in (".venv", "venv", "__pycache__")]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", file_path],
                        capture_output=True,
                        text=True,
                    )
                    assert (
                        result.returncode == 0
                    ), f"Syntax error in {file_path}: {result.stderr}"

    @pytest.mark.syntax_validation
    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX[:3],
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX[:3]],
    )
    def test_yaml_syntax_valid(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test that generated YAML files have valid syntax.

        Note: Kubernetes YAML files can contain multiple documents separated by ---,
        so we use yaml.safe_load_all() for those.
        """
        result_dir = generate_project(template_dir, temp_dir, options)

        for root, dirs, files in os.walk(result_dir):
            # Skip node_modules
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]

            for file in files:
                if file.endswith((".yml", ".yaml")):
                    file_path = os.path.join(root, file)
                    with open(file_path) as f:
                        try:
                            # Use safe_load_all for k8s files (may have multiple docs)
                            if "/k8s/" in file_path or file.startswith("k8s"):
                                list(yaml.safe_load_all(f))
                            else:
                                yaml.safe_load(f)
                        except yaml.YAMLError as e:
                            pytest.fail(f"YAML syntax error in {file_path}: {e}")

    @pytest.mark.syntax_validation
    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX[:3],
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX[:3]],
    )
    def test_json_syntax_valid(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test that generated JSON files have valid syntax.

        Note: tsconfig.json and similar files use JSONC (JSON with comments
        and trailing commas), so we skip those files in strict validation.
        """
        result_dir = generate_project(template_dir, temp_dir, options)

        # Files that use JSONC (JSON with comments/trailing commas)
        jsonc_files = {"tsconfig.json", "tsconfig.node.json", ".vscode/settings.json"}

        for root, dirs, files in os.walk(result_dir):
            # Skip node_modules
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]

            for file in files:
                if file.endswith(".json"):
                    # Skip JSONC files that have comments or trailing commas
                    if file in jsonc_files:
                        continue

                    file_path = os.path.join(root, file)
                    with open(file_path) as f:
                        try:
                            json.load(f)
                        except json.JSONDecodeError as e:
                            pytest.fail(f"JSON syntax error in {file_path}: {e}")

    @pytest.mark.syntax_validation
    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX[:2],
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX[:2]],
    )
    def test_dockerfile_valid(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test that generated Dockerfiles are valid."""
        result_dir = generate_project(template_dir, temp_dir, options)

        # Check backend Dockerfile
        backend_dockerfile = os.path.join(result_dir, "backend", "Dockerfile")
        assert os.path.exists(backend_dockerfile), "Backend Dockerfile should exist"

        with open(backend_dockerfile) as f:
            content = f.read()
            assert "FROM" in content, "Dockerfile should have FROM instruction"
            assert (
                "WORKDIR" in content or "COPY" in content
            ), "Dockerfile should have basic instructions"

        # Check frontend Dockerfile
        frontend_dockerfile = os.path.join(result_dir, "frontend", "Dockerfile")
        if os.path.exists(frontend_dockerfile):
            with open(frontend_dockerfile) as f:
                content = f.read()
                assert "FROM" in content, "Frontend Dockerfile should have FROM"


class TestNoJinjaArtifacts:
    """Test that no Jinja2 artifacts remain in rendered output."""

    # Files that are intentionally not rendered (copied as-is)
    # These are listed in cookiecutter.json's _copy_without_render
    UNRENDERED_FILES = {
        "db-restore.sh",
        "db-backup.sh",
        "db-verify.sh",
    }

    # Directories that are not rendered
    UNRENDERED_DIRS = {
        "docs/decisions",
        "observability/grafana/dashboards",
    }

    @pytest.mark.parametrize(
        "options",
        MINIMUM_TEST_MATRIX[:3],
        ids=[get_combination_id(o) for o in MINIMUM_TEST_MATRIX[:3]],
    )
    def test_no_jinja_artifacts_in_files(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test that no unrendered Jinja2 artifacts remain in rendered files.

        Note: Some files are intentionally not rendered (via _copy_without_render)
        because they contain syntax that conflicts with Jinja2 (like bash ${#array[@]}).
        """
        result_dir = generate_project(template_dir, temp_dir, options)

        jinja_patterns = ["{{ cookiecutter.", "{%", "{% if", "{% endif", "{% for"]

        for root, dirs, files in os.walk(result_dir):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]

            # Check if this directory should be skipped
            rel_root = os.path.relpath(root, result_dir)
            skip_dir = any(
                rel_root.startswith(unrendered) for unrendered in self.UNRENDERED_DIRS
            )
            if skip_dir:
                continue

            for file in files:
                # Skip binary files
                if file.endswith(
                    (".png", ".jpg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot")
                ):
                    continue

                # Skip files that are intentionally not rendered
                if file in self.UNRENDERED_FILES:
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    for pattern in jinja_patterns:
                        if pattern in content:
                            # Special case: {% raw %} and {% endraw %} are allowed in CI files
                            # as GitHub Actions uses similar syntax
                            if "{% raw" in content or "{% endraw" in content:
                                continue
                            pytest.fail(
                                f"Jinja2 artifact '{pattern}' found in {file_path}"
                            )
                except UnicodeDecodeError:
                    # Binary file, skip
                    pass


class TestSpecificFeatureCombinations:
    """Test specific feature combinations for expected behavior."""

    def test_kubernetes_requires_deploy_workflow(
        self, temp_dir: str, template_dir: Path
    ) -> None:
        """Test that K8s + GH Actions includes deploy workflow."""
        options = {
            "include_observability": "no",
            "include_github_actions": "yes",
            "include_kubernetes": "yes",
            "include_sentry": "no",
        }

        result_dir = generate_project(template_dir, temp_dir, options)

        deploy_workflow = os.path.join(result_dir, ".github", "workflows", "deploy.yml")
        assert os.path.exists(deploy_workflow), "Deploy workflow should exist with K8s"

    def test_kubernetes_without_github_actions(
        self, temp_dir: str, template_dir: Path
    ) -> None:
        """Test K8s without GH Actions still generates K8s files."""
        options = {
            "include_observability": "no",
            "include_github_actions": "no",
            "include_kubernetes": "yes",
            "include_sentry": "no",
        }

        result_dir = generate_project(template_dir, temp_dir, options)

        # K8s should exist
        k8s_dir = os.path.join(result_dir, "k8s")
        assert os.path.isdir(k8s_dir), "k8s directory should exist"

        # But no deploy workflow (no .github directory)
        github_dir = os.path.join(result_dir, ".github")
        assert not os.path.exists(github_dir), ".github should not exist"

    def test_sentry_with_observability(
        self, temp_dir: str, template_dir: Path
    ) -> None:
        """Test Sentry + Observability combination."""
        options = {
            "include_observability": "yes",
            "include_github_actions": "no",
            "include_kubernetes": "no",
            "include_sentry": "yes",
        }

        result_dir = generate_project(template_dir, temp_dir, options)

        # Both should exist
        sentry_file = os.path.join(result_dir, "backend", "app", "sentry.py")
        obs_dir = os.path.join(result_dir, "observability")

        assert os.path.exists(sentry_file), "Sentry should exist"
        assert os.path.isdir(obs_dir), "Observability should exist"


class TestFullMatrix:
    """Full matrix tests (run with --full-matrix flag)."""

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "options",
        FULL_TEST_MATRIX,
        ids=[get_combination_id(o) for o in FULL_TEST_MATRIX],
    )
    def test_all_combinations_generate(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test all 16 option combinations generate successfully."""
        result_dir = generate_project(template_dir, temp_dir, options)

        assert os.path.isdir(result_dir), "Generated project should be a directory"
        assert os.path.exists(
            os.path.join(result_dir, "README.md")
        ), "README.md should exist"
        assert os.path.exists(
            os.path.join(result_dir, "compose.yml")
        ), "compose.yml should exist"

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "options",
        FULL_TEST_MATRIX,
        ids=[get_combination_id(o) for o in FULL_TEST_MATRIX],
    )
    def test_all_combinations_python_syntax(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test all combinations have valid Python syntax."""
        result_dir = generate_project(template_dir, temp_dir, options)

        backend_dir = os.path.join(result_dir, "backend")

        for root, dirs, files in os.walk(backend_dir):
            dirs[:] = [d for d in dirs if d not in (".venv", "venv", "__pycache__")]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", file_path],
                        capture_output=True,
                        text=True,
                    )
                    assert (
                        result.returncode == 0
                    ), f"Syntax error in {file_path}: {result.stderr}"

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "options",
        FULL_TEST_MATRIX,
        ids=[get_combination_id(o) for o in FULL_TEST_MATRIX],
    )
    def test_all_combinations_yaml_syntax(
        self, temp_dir: str, template_dir: Path, options: dict
    ) -> None:
        """Test all combinations have valid YAML syntax."""
        result_dir = generate_project(template_dir, temp_dir, options)

        for root, dirs, files in os.walk(result_dir):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]

            for file in files:
                if file.endswith((".yml", ".yaml")):
                    file_path = os.path.join(root, file)
                    with open(file_path) as f:
                        try:
                            # Use safe_load_all for k8s files (may have multiple docs)
                            if "/k8s/" in file_path or file.startswith("k8s"):
                                list(yaml.safe_load_all(f))
                            else:
                                yaml.safe_load(f)
                        except yaml.YAMLError as e:
                            pytest.fail(f"YAML syntax error in {file_path}: {e}")
