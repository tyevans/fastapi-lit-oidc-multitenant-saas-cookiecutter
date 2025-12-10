#!/bin/bash
# Template Validation Script
# Validates that cookiecutter template generates correctly with various option combinations
#
# Usage:
#   ./scripts/validate-template.sh                # Run minimum matrix (5 combinations)
#   RUN_FULL_MATRIX=true ./scripts/validate-template.sh  # Run all 16 combinations

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$PROJECT_ROOT/template"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/template-validation}"
RUN_FULL_MATRIX="${RUN_FULL_MATRIX:-false}"
KEEP_OUTPUT="${KEEP_OUTPUT:-false}"

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  Cookiecutter Template Validation${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
echo -e "${BLUE}Template:${NC} $TEMPLATE_DIR"
echo -e "${BLUE}Output:${NC}   $OUTPUT_DIR"
echo -e "${BLUE}Matrix:${NC}   $([ "$RUN_FULL_MATRIX" = "true" ] && echo "Full (16 combinations)" || echo "Minimum (5 combinations)")"
echo ""

# Clean up
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Check for required tools
check_requirements() {
    local missing=()

    if ! command -v cookiecutter &> /dev/null; then
        missing+=("cookiecutter")
    fi

    if ! command -v python &> /dev/null; then
        missing+=("python")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}Missing required tools: ${missing[*]}${NC}"
        echo "Install with: pip install cookiecutter"
        exit 1
    fi
}

check_requirements

# Define test combinations
if [ "$RUN_FULL_MATRIX" = "true" ]; then
    # All 16 combinations
    COMBINATIONS=(
        "include_observability=yes include_github_actions=yes include_kubernetes=yes include_sentry=yes"
        "include_observability=yes include_github_actions=yes include_kubernetes=yes include_sentry=no"
        "include_observability=yes include_github_actions=yes include_kubernetes=no include_sentry=yes"
        "include_observability=yes include_github_actions=yes include_kubernetes=no include_sentry=no"
        "include_observability=yes include_github_actions=no include_kubernetes=yes include_sentry=yes"
        "include_observability=yes include_github_actions=no include_kubernetes=yes include_sentry=no"
        "include_observability=yes include_github_actions=no include_kubernetes=no include_sentry=yes"
        "include_observability=yes include_github_actions=no include_kubernetes=no include_sentry=no"
        "include_observability=no include_github_actions=yes include_kubernetes=yes include_sentry=yes"
        "include_observability=no include_github_actions=yes include_kubernetes=yes include_sentry=no"
        "include_observability=no include_github_actions=yes include_kubernetes=no include_sentry=yes"
        "include_observability=no include_github_actions=yes include_kubernetes=no include_sentry=no"
        "include_observability=no include_github_actions=no include_kubernetes=yes include_sentry=yes"
        "include_observability=no include_github_actions=no include_kubernetes=yes include_sentry=no"
        "include_observability=no include_github_actions=no include_kubernetes=no include_sentry=yes"
        "include_observability=no include_github_actions=no include_kubernetes=no include_sentry=no"
    )
else
    # Minimum matrix (5 key combinations)
    COMBINATIONS=(
        "include_observability=yes include_github_actions=yes include_kubernetes=yes include_sentry=yes"
        "include_observability=no include_github_actions=no include_kubernetes=no include_sentry=no"
        "include_observability=yes include_github_actions=no include_kubernetes=no include_sentry=no"
        "include_observability=no include_github_actions=yes include_kubernetes=no include_sentry=no"
        "include_observability=no include_github_actions=yes include_kubernetes=yes include_sentry=no"
    )
fi

PASSED=0
FAILED=0
TOTAL=${#COMBINATIONS[@]}

validate_python_syntax() {
    local project_dir="$1"
    local backend_dir="$project_dir/backend"

    if [ ! -d "$backend_dir" ]; then
        echo -e "    ${RED}Backend directory not found${NC}"
        return 1
    fi

    local errors=0
    while IFS= read -r -d '' pyfile; do
        if ! python -m py_compile "$pyfile" 2>/dev/null; then
            echo -e "    ${RED}Syntax error: $pyfile${NC}"
            ((errors++))
        fi
    done < <(find "$backend_dir" -name "*.py" -type f -print0)

    if [ $errors -eq 0 ]; then
        echo -e "    ${GREEN}Python syntax: OK${NC}"
        return 0
    else
        echo -e "    ${RED}Python syntax: $errors errors${NC}"
        return 1
    fi
}

validate_yaml_syntax() {
    local project_dir="$1"

    local errors=0
    while IFS= read -r -d '' yamlfile; do
        if ! python -c "import yaml; yaml.safe_load(open('$yamlfile'))" 2>/dev/null; then
            echo -e "    ${RED}YAML error: $yamlfile${NC}"
            ((errors++))
        fi
    done < <(find "$project_dir" -name "*.yml" -o -name "*.yaml" -type f -print0 2>/dev/null | grep -v node_modules)

    if [ $errors -eq 0 ]; then
        echo -e "    ${GREEN}YAML syntax: OK${NC}"
        return 0
    else
        echo -e "    ${RED}YAML syntax: $errors errors${NC}"
        return 1
    fi
}

validate_json_syntax() {
    local project_dir="$1"

    local errors=0
    while IFS= read -r -d '' jsonfile; do
        if ! python -c "import json; json.load(open('$jsonfile'))" 2>/dev/null; then
            echo -e "    ${RED}JSON error: $jsonfile${NC}"
            ((errors++))
        fi
    done < <(find "$project_dir" -name "*.json" -type f -print0 2>/dev/null | grep -v node_modules)

    if [ $errors -eq 0 ]; then
        echo -e "    ${GREEN}JSON syntax: OK${NC}"
        return 0
    else
        echo -e "    ${RED}JSON syntax: $errors errors${NC}"
        return 1
    fi
}

validate_conditional_files() {
    local project_dir="$1"
    local combo="$2"

    local validation_errors=0

    # Check GitHub Actions
    if [[ "$combo" == *"include_github_actions=yes"* ]]; then
        if [ -f "$project_dir/.github/workflows/ci.yml" ]; then
            echo -e "    ${GREEN}GitHub Actions: Present (expected)${NC}"
        else
            echo -e "    ${RED}GitHub Actions: Missing (expected present)${NC}"
            ((validation_errors++))
        fi
    else
        if [ ! -d "$project_dir/.github" ]; then
            echo -e "    ${GREEN}GitHub Actions: Absent (expected)${NC}"
        else
            echo -e "    ${RED}GitHub Actions: Present (expected absent)${NC}"
            ((validation_errors++))
        fi
    fi

    # Check Kubernetes
    if [[ "$combo" == *"include_kubernetes=yes"* ]]; then
        if [ -d "$project_dir/k8s" ]; then
            echo -e "    ${GREEN}Kubernetes: Present (expected)${NC}"
        else
            echo -e "    ${RED}Kubernetes: Missing (expected present)${NC}"
            ((validation_errors++))
        fi
    else
        if [ ! -d "$project_dir/k8s" ]; then
            echo -e "    ${GREEN}Kubernetes: Absent (expected)${NC}"
        else
            echo -e "    ${RED}Kubernetes: Present (expected absent)${NC}"
            ((validation_errors++))
        fi
    fi

    # Check Observability
    if [[ "$combo" == *"include_observability=yes"* ]]; then
        if [ -d "$project_dir/observability" ]; then
            echo -e "    ${GREEN}Observability: Present (expected)${NC}"
        else
            echo -e "    ${RED}Observability: Missing (expected present)${NC}"
            ((validation_errors++))
        fi
    else
        if [ ! -d "$project_dir/observability" ]; then
            echo -e "    ${GREEN}Observability: Absent (expected)${NC}"
        else
            echo -e "    ${RED}Observability: Present (expected absent)${NC}"
            ((validation_errors++))
        fi
    fi

    # Check Sentry
    if [[ "$combo" == *"include_sentry=yes"* ]]; then
        if [ -f "$project_dir/backend/app/sentry.py" ]; then
            echo -e "    ${GREEN}Sentry: Present (expected)${NC}"
        else
            echo -e "    ${RED}Sentry: Missing (expected present)${NC}"
            ((validation_errors++))
        fi
    else
        if [ ! -f "$project_dir/backend/app/sentry.py" ]; then
            echo -e "    ${GREEN}Sentry: Absent (expected)${NC}"
        else
            echo -e "    ${RED}Sentry: Present (expected absent)${NC}"
            ((validation_errors++))
        fi
    fi

    return $validation_errors
}

# Run tests
TEST_NUM=0
for combo in "${COMBINATIONS[@]}"; do
    ((TEST_NUM++))
    echo -e "\n${YELLOW}[$TEST_NUM/$TOTAL] Testing: $combo${NC}"

    # Create unique output directory
    COMBO_HASH=$(echo "$combo" | md5sum | cut -c1-8)
    COMBO_DIR="$OUTPUT_DIR/test-$COMBO_HASH"
    mkdir -p "$COMBO_DIR"

    # Generate project
    if cookiecutter "$TEMPLATE_DIR" --no-input \
        --output-dir "$COMBO_DIR" \
        project_name="Test Project" \
        author_name="Test Author" \
        author_email="test@example.com" \
        github_username="test-user" \
        $combo 2>&1 | head -20; then

        PROJECT_DIR="$COMBO_DIR/test-project"

        if [ ! -d "$PROJECT_DIR" ]; then
            echo -e "  ${RED}Generation FAILED - project directory not created${NC}"
            ((FAILED++))
            continue
        fi

        echo -e "  ${GREEN}Generation: OK${NC}"

        # Run validations
        COMBO_FAILED=0

        # Validate Python syntax
        if ! validate_python_syntax "$PROJECT_DIR"; then
            ((COMBO_FAILED++))
        fi

        # Validate YAML syntax
        if ! validate_yaml_syntax "$PROJECT_DIR"; then
            ((COMBO_FAILED++))
        fi

        # Validate JSON syntax
        if ! validate_json_syntax "$PROJECT_DIR"; then
            ((COMBO_FAILED++))
        fi

        # Validate conditional files
        if ! validate_conditional_files "$PROJECT_DIR" "$combo"; then
            ((COMBO_FAILED++))
        fi

        if [ $COMBO_FAILED -eq 0 ]; then
            echo -e "  ${GREEN}PASSED${NC}"
            ((PASSED++))
        else
            echo -e "  ${RED}FAILED ($COMBO_FAILED validation errors)${NC}"
            ((FAILED++))
        fi
    else
        echo -e "  ${RED}Generation FAILED${NC}"
        ((FAILED++))
    fi
done

# Summary
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  Validation Summary${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
echo -e "Total:  $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

# Cleanup
if [ "$KEEP_OUTPUT" != "true" ]; then
    rm -rf "$OUTPUT_DIR"
    echo -e "${BLUE}Cleaned up temporary files${NC}"
else
    echo -e "${BLUE}Output kept at: $OUTPUT_DIR${NC}"
fi

if [ $FAILED -gt 0 ]; then
    echo -e "\n${RED}Some validations failed!${NC}"
    exit 1
else
    echo -e "\n${GREEN}All validations passed!${NC}"
    exit 0
fi
