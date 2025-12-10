# P6-03: Validate Cookiecutter Option Combinations

## Task Identifier
**ID:** P6-03
**Phase:** 6 - Documentation and Validation
**Domain:** DevOps
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| All P1-P5 tasks | Implementation | Pending | All features must be implemented |
| P1-01 | include_github_actions | Must complete | New cookiecutter variable |
| P3-04 | include_sentry | Must complete | New cookiecutter variable |
| P4-06 | include_kubernetes | Must complete | New cookiecutter variable |

## Scope

### In Scope
- Create comprehensive test matrix for all cookiecutter option combinations
- Implement automated validation script for template generation
- Test that generated projects build and pass basic tests
- Validate Jinja2 conditionals render correctly
- Test edge cases (empty values, special characters)
- Create CI job for matrix testing
- Document validation procedures

### Out of Scope
- Full E2E testing of generated projects (covered by P6-04)
- Performance testing of template generation
- Testing non-default cookiecutter values (project name, ports, etc.)
- Testing deprecated option combinations

## Relevant Code Areas

### Files to Create
```
template/tests/
  test_template_generation.py              # Pytest-based validation tests
  conftest.py                              # Test fixtures
  option_combinations.py                   # Test matrix definition

.github/workflows/
  template-validation.yml                  # CI workflow for matrix testing

scripts/
  validate-template.sh                     # Manual validation script
```

### Files to Analyze
```
template/cookiecutter.json                 # Option definitions
template/hooks/post_gen_project.py         # Post-generation hooks
template/{{cookiecutter.project_slug}}/    # All template files with conditionals
```

## Implementation Details

### 1. Option Combinations Matrix

Define all meaningful option combinations to test:

```python
# template/tests/option_combinations.py

"""Cookiecutter option combinations for validation testing."""

# Boolean options that create conditional content
CONDITIONAL_OPTIONS = {
    "include_observability": ["yes", "no"],
    "include_github_actions": ["yes", "no"],
    "include_kubernetes": ["yes", "no"],
    "include_sentry": ["yes", "no"],
}

# Minimum test matrix (covers key combinations)
MINIMUM_TEST_MATRIX = [
    # All features enabled
    {
        "include_observability": "yes",
        "include_github_actions": "yes",
        "include_kubernetes": "yes",
        "include_sentry": "yes",
    },
    # All features disabled
    {
        "include_observability": "no",
        "include_github_actions": "no",
        "include_kubernetes": "no",
        "include_sentry": "no",
    },
    # Observability only (original template default)
    {
        "include_observability": "yes",
        "include_github_actions": "no",
        "include_kubernetes": "no",
        "include_sentry": "no",
    },
    # CI/CD only
    {
        "include_observability": "no",
        "include_github_actions": "yes",
        "include_kubernetes": "no",
        "include_sentry": "no",
    },
    # K8s without observability (valid for external monitoring)
    {
        "include_observability": "no",
        "include_github_actions": "yes",
        "include_kubernetes": "yes",
        "include_sentry": "no",
    },
    # Full production setup
    {
        "include_observability": "yes",
        "include_github_actions": "yes",
        "include_kubernetes": "yes",
        "include_sentry": "yes",
    },
]

# Full matrix (2^4 = 16 combinations)
def generate_full_matrix():
    """Generate all possible option combinations."""
    import itertools

    options = list(CONDITIONAL_OPTIONS.keys())
    values = list(CONDITIONAL_OPTIONS.values())

    combinations = []
    for combo in itertools.product(*values):
        combinations.append(dict(zip(options, combo)))

    return combinations


FULL_TEST_MATRIX = generate_full_matrix()

# Default values for non-conditional options
DEFAULT_OPTIONS = {
    "project_name": "Test Project",
    "project_slug": "test-project",
    "project_short_description": "A test project",
    "author_name": "Test Author",
    "author_email": "test@example.com",
    "postgres_version": "18",
    "redis_version": "7",
    "keycloak_version": "23.0",
    "python_version": "3.13",
    "node_version": "20",
    "license": "MIT",
}
```

### 2. Pytest Validation Tests

```python
# template/tests/test_template_generation.py

"""Tests for cookiecutter template generation."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

from option_combinations import (
    DEFAULT_OPTIONS,
    MINIMUM_TEST_MATRIX,
    FULL_TEST_MATRIX,
)

TEMPLATE_DIR = Path(__file__).parent.parent


@pytest.fixture
def temp_dir():
    """Create a temporary directory for generated projects."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


def merge_options(custom_options: dict) -> dict:
    """Merge custom options with defaults."""
    return {**DEFAULT_OPTIONS, **custom_options}


class TestTemplateGeneration:
    """Test template generation with various option combinations."""

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX)
    def test_template_generates_successfully(self, temp_dir, options):
        """Test that template generates without errors."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        assert os.path.isdir(result_dir)
        assert os.path.isfile(os.path.join(result_dir, "README.md"))

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX)
    def test_required_files_exist(self, temp_dir, options):
        """Test that all required files are generated."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        # Core files always present
        required_files = [
            "README.md",
            "compose.yml",
            "backend/app/main.py",
            "frontend/package.json",
            "CLAUDE.md",
        ]

        for file_path in required_files:
            full_path = os.path.join(result_dir, file_path)
            assert os.path.exists(full_path), f"Missing required file: {file_path}"

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX)
    def test_conditional_github_actions(self, temp_dir, options):
        """Test GitHub Actions conditional generation."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        ci_workflow = os.path.join(result_dir, ".github", "workflows", "ci.yml")

        if options.get("include_github_actions") == "yes":
            assert os.path.exists(ci_workflow), "CI workflow should exist"
        else:
            assert not os.path.exists(ci_workflow), "CI workflow should not exist"

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX)
    def test_conditional_kubernetes(self, temp_dir, options):
        """Test Kubernetes conditional generation."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        k8s_dir = os.path.join(result_dir, "k8s")

        if options.get("include_kubernetes") == "yes":
            assert os.path.isdir(k8s_dir), "k8s directory should exist"
            assert os.path.exists(
                os.path.join(k8s_dir, "base", "kustomization.yaml")
            ), "kustomization.yaml should exist"
        else:
            assert not os.path.exists(k8s_dir), "k8s directory should not exist"

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX)
    def test_conditional_sentry(self, temp_dir, options):
        """Test Sentry conditional generation."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        sentry_file = os.path.join(result_dir, "backend", "app", "services", "sentry.py")
        main_file = os.path.join(result_dir, "backend", "app", "main.py")

        if options.get("include_sentry") == "yes":
            assert os.path.exists(sentry_file), "Sentry service should exist"
            with open(main_file) as f:
                assert "sentry" in f.read().lower(), "main.py should reference Sentry"
        else:
            assert not os.path.exists(sentry_file), "Sentry service should not exist"

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX)
    def test_conditional_observability(self, temp_dir, options):
        """Test observability conditional generation."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        obs_dir = os.path.join(result_dir, "observability")

        if options.get("include_observability") == "yes":
            assert os.path.isdir(obs_dir), "observability directory should exist"
            assert os.path.exists(
                os.path.join(obs_dir, "prometheus", "prometheus.yml")
            ), "prometheus.yml should exist"
        else:
            assert not os.path.exists(obs_dir), "observability directory should not exist"


class TestGeneratedProjectValidity:
    """Test that generated projects are valid and buildable."""

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX[:3])  # Subset for speed
    def test_python_syntax_valid(self, temp_dir, options):
        """Test that generated Python files have valid syntax."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        backend_dir = os.path.join(result_dir, "backend")

        # Check all Python files for syntax errors
        for root, dirs, files in os.walk(backend_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    result = subprocess.run(
                        ["python", "-m", "py_compile", file_path],
                        capture_output=True,
                        text=True,
                    )
                    assert result.returncode == 0, f"Syntax error in {file_path}: {result.stderr}"

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX[:3])
    def test_yaml_syntax_valid(self, temp_dir, options):
        """Test that generated YAML files have valid syntax."""
        import yaml

        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        for root, dirs, files in os.walk(result_dir):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    file_path = os.path.join(root, file)
                    with open(file_path) as f:
                        try:
                            yaml.safe_load(f)
                        except yaml.YAMLError as e:
                            pytest.fail(f"YAML syntax error in {file_path}: {e}")

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX[:3])
    def test_json_syntax_valid(self, temp_dir, options):
        """Test that generated JSON files have valid syntax."""
        import json

        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        for root, dirs, files in os.walk(result_dir):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path) as f:
                        try:
                            json.load(f)
                        except json.JSONDecodeError as e:
                            pytest.fail(f"JSON syntax error in {file_path}: {e}")

    @pytest.mark.parametrize("options", MINIMUM_TEST_MATRIX[:2])
    def test_dockerfile_valid(self, temp_dir, options):
        """Test that generated Dockerfiles are valid."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        # Check backend Dockerfile
        backend_dockerfile = os.path.join(result_dir, "backend", "Dockerfile")
        assert os.path.exists(backend_dockerfile)

        # Use docker build --check if available (Docker 25+)
        # Otherwise just verify file exists and has content
        with open(backend_dockerfile) as f:
            content = f.read()
            assert "FROM" in content, "Dockerfile should have FROM instruction"
            assert "WORKDIR" in content or "COPY" in content, "Dockerfile should have basic instructions"


class TestNoRenderPatterns:
    """Test that no-render patterns work correctly."""

    def test_grafana_dashboards_not_rendered(self, temp_dir):
        """Test that Grafana dashboard JSON is not Jinja2-rendered."""
        full_options = merge_options({"include_observability": "yes"})

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        dashboard_dir = os.path.join(result_dir, "observability", "grafana", "dashboards")

        if os.path.isdir(dashboard_dir):
            for file in os.listdir(dashboard_dir):
                if file.endswith(".json"):
                    with open(os.path.join(dashboard_dir, file)) as f:
                        content = f.read()
                        # Should not have Jinja2 artifacts
                        assert "{{" not in content or "cookiecutter" not in content


class TestFullMatrix:
    """Full matrix tests (run in CI only due to time)."""

    @pytest.mark.slow
    @pytest.mark.parametrize("options", FULL_TEST_MATRIX)
    def test_all_combinations_generate(self, temp_dir, options):
        """Test all 16 option combinations generate successfully."""
        full_options = merge_options(options)

        result_dir = cookiecutter(
            str(TEMPLATE_DIR),
            output_dir=temp_dir,
            no_input=True,
            extra_context=full_options,
        )

        assert os.path.isdir(result_dir)
```

### 3. Test Configuration (`conftest.py`)

```python
# template/tests/conftest.py

"""Pytest configuration for template tests."""

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--full-matrix",
        action="store_true",
        default=False,
        help="Run full matrix tests (16 combinations)",
    )


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")


def pytest_collection_modifyitems(config, items):
    """Skip slow tests unless --full-matrix is specified."""
    if config.getoption("--full-matrix"):
        return

    skip_slow = pytest.mark.skip(reason="Use --full-matrix to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
```

### 4. CI Workflow for Matrix Testing

```yaml
# .github/workflows/template-validation.yml

name: Template Validation

on:
  push:
    branches: [main]
    paths:
      - 'template/**'
      - '.github/workflows/template-validation.yml'
  pull_request:
    branches: [main]
    paths:
      - 'template/**'

jobs:
  validate-minimum:
    name: Validate Template (Minimum Matrix)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install cookiecutter pytest pyyaml

      - name: Run minimum matrix tests
        run: |
          cd template
          pytest tests/ -v --ignore=tests/test_full_matrix.py

  validate-full:
    name: Validate Template (Full Matrix)
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install cookiecutter pytest pyyaml

      - name: Run full matrix tests
        run: |
          cd template
          pytest tests/ -v --full-matrix

  validate-generation:
    name: Validate Generated Project
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - name: "All Features"
            options: "include_observability=yes include_github_actions=yes include_kubernetes=yes include_sentry=yes"
          - name: "Minimal"
            options: "include_observability=no include_github_actions=no include_kubernetes=no include_sentry=no"
          - name: "CI Only"
            options: "include_observability=no include_github_actions=yes include_kubernetes=no include_sentry=no"

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install cookiecutter
        run: pip install cookiecutter

      - name: Generate project
        run: |
          cookiecutter . --no-input \
            project_name="Test Project" \
            ${{ matrix.options }}

      - name: Verify Python syntax
        run: |
          cd test-project
          python -m py_compile backend/app/main.py
          python -m py_compile backend/app/core/config.py

      - name: Verify YAML syntax
        run: |
          cd test-project
          python -c "import yaml; yaml.safe_load(open('compose.yml'))"

      - name: Install backend dependencies
        run: |
          cd test-project/backend
          pip install uv
          uv sync --frozen

      - name: Run backend linting
        run: |
          cd test-project/backend
          uv run ruff check app/

      - name: Install frontend dependencies
        run: |
          cd test-project/frontend
          npm ci

      - name: Run frontend linting
        run: |
          cd test-project/frontend
          npm run lint
```

### 5. Manual Validation Script

```bash
#!/bin/bash
# scripts/validate-template.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$PROJECT_ROOT/template"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/template-validation}"
RUN_FULL_MATRIX="${RUN_FULL_MATRIX:-false}"

echo -e "${GREEN}=== Template Validation Script ===${NC}"

# Clean up
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Option combinations to test
declare -a COMBINATIONS=(
    "include_observability=yes include_github_actions=yes include_kubernetes=yes include_sentry=yes"
    "include_observability=no include_github_actions=no include_kubernetes=no include_sentry=no"
    "include_observability=yes include_github_actions=no include_kubernetes=no include_sentry=no"
    "include_observability=no include_github_actions=yes include_kubernetes=no include_sentry=no"
    "include_observability=yes include_github_actions=yes include_kubernetes=yes include_sentry=no"
)

PASSED=0
FAILED=0

for combo in "${COMBINATIONS[@]}"; do
    echo -e "\n${YELLOW}Testing: $combo${NC}"

    # Create unique output directory
    COMBO_HASH=$(echo "$combo" | md5sum | cut -c1-8)
    COMBO_DIR="$OUTPUT_DIR/test-$COMBO_HASH"

    # Generate project
    if cookiecutter "$TEMPLATE_DIR" --no-input \
        --output-dir "$COMBO_DIR" \
        project_name="Test Project" \
        $combo 2>&1; then

        PROJECT_DIR="$COMBO_DIR/test-project"

        # Validate Python syntax
        echo "  Checking Python syntax..."
        if find "$PROJECT_DIR/backend" -name "*.py" -exec python -m py_compile {} \; 2>&1; then
            echo -e "  ${GREEN}Python syntax OK${NC}"
        else
            echo -e "  ${RED}Python syntax FAILED${NC}"
            ((FAILED++))
            continue
        fi

        # Validate YAML syntax
        echo "  Checking YAML syntax..."
        if find "$PROJECT_DIR" -name "*.yml" -o -name "*.yaml" | while read -r f; do
            python -c "import yaml; yaml.safe_load(open('$f'))" 2>&1
        done; then
            echo -e "  ${GREEN}YAML syntax OK${NC}"
        else
            echo -e "  ${RED}YAML syntax FAILED${NC}"
            ((FAILED++))
            continue
        fi

        # Check conditional files
        echo "  Checking conditional files..."
        if [[ "$combo" == *"include_github_actions=yes"* ]]; then
            if [[ -f "$PROJECT_DIR/.github/workflows/ci.yml" ]]; then
                echo -e "    ${GREEN}GitHub Actions: Present (expected)${NC}"
            else
                echo -e "    ${RED}GitHub Actions: Missing (expected present)${NC}"
                ((FAILED++))
                continue
            fi
        else
            if [[ ! -f "$PROJECT_DIR/.github/workflows/ci.yml" ]]; then
                echo -e "    ${GREEN}GitHub Actions: Absent (expected)${NC}"
            else
                echo -e "    ${RED}GitHub Actions: Present (expected absent)${NC}"
                ((FAILED++))
                continue
            fi
        fi

        echo -e "  ${GREEN}PASSED${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}Generation FAILED${NC}"
        ((FAILED++))
    fi
done

# Summary
echo -e "\n${GREEN}=== Validation Summary ===${NC}"
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [[ $FAILED -gt 0 ]]; then
    echo -e "${RED}Some validations failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All validations passed!${NC}"
    exit 0
fi
```

## Success Criteria

### Functional Requirements
- [ ] NFR-002: Template generation succeeds for all option combinations
- [ ] All 16 option combinations generate without errors
- [ ] Generated Python files have valid syntax
- [ ] Generated YAML files have valid syntax
- [ ] Generated JSON files have valid syntax
- [ ] Conditional files appear/disappear correctly
- [ ] No Jinja2 artifacts in rendered output

### Verification Steps
1. **Run Pytest Tests:**
   ```bash
   cd template
   pytest tests/ -v
   ```

2. **Run Full Matrix:**
   ```bash
   cd template
   pytest tests/ -v --full-matrix
   ```

3. **Run Manual Script:**
   ```bash
   ./scripts/validate-template.sh
   ```

4. **CI Verification:**
   - Open PR with template changes
   - Verify template-validation workflow passes

### Quality Gates
- [ ] All minimum matrix tests pass
- [ ] All full matrix tests pass
- [ ] CI workflow runs successfully
- [ ] No false positives (tests don't pass when they should fail)
- [ ] Tests run in reasonable time (<5 minutes for minimum matrix)

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P1-01 | include_github_actions variable | Must exist in cookiecutter.json |
| P3-04 | include_sentry variable | Must exist in cookiecutter.json |
| P4-06 | include_kubernetes variable | Must exist in cookiecutter.json |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-04 | Validation passes | E2E depends on valid template |

### Integration Contract
```yaml
# Contract: Template validation

# Test matrix options
- include_observability: yes/no
- include_github_actions: yes/no
- include_kubernetes: yes/no
- include_sentry: yes/no

# Validation checks
- Template generates without errors
- Python files have valid syntax
- YAML files have valid syntax
- JSON files have valid syntax
- Conditional files present/absent correctly

# CI trigger
- On push to main (paths: template/**)
- On PR to main (paths: template/**)
```

## Monitoring and Observability

### Validation Metrics
- Template generation success rate
- Test execution time
- Common failure patterns

### CI Visibility
- GitHub Actions workflow status
- Test coverage for option combinations
- Failure investigation via logs

## Infrastructure Needs

### CI Requirements
- Python 3.13 for test execution
- Node.js 20 for frontend validation
- Cookiecutter installed
- Pytest with markers support

### Local Development
- Same as CI requirements
- Docker optional (for full project validation)

## Estimated Effort

**Size:** M (Medium)
**Time:** 2-3 days
**Justification:**
- Test framework setup requires careful design
- 16 option combinations to test
- CI workflow configuration
- Debugging conditional rendering issues
- Documentation of validation procedures

## Notes

### Design Decisions

**1. Minimum vs Full Matrix:**
- Minimum matrix (6 combinations) runs on every PR
- Full matrix (16 combinations) runs on merge to main
- Balances thoroughness with CI speed

**2. Pytest-Based Testing:**
- Pytest is already used in the template
- Familiar to contributors
- Good fixture support for temp directories

**3. Syntax Validation Only:**
- Tests validate syntax, not runtime behavior
- Runtime testing is P6-04's responsibility
- Keeps validation fast

**4. CI Integration:**
- Runs on template changes only (path filtering)
- Matrix strategy for parallel testing
- Clear failure messages

### Related Requirements
- NFR-002: Template generation shall succeed for all option combinations
- Ensures template quality before release
- Prevents regressions in conditional logic

### Coordination Notes
- Must run after all cookiecutter variables are finalized
- Update test matrix if new options are added
- Review failed tests to determine if test or template is wrong
