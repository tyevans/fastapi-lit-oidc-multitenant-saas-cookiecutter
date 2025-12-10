#!/usr/bin/env bash
# Check and optionally update dependencies in the cookiecutter template
# Usage: ./scripts/check-dependencies.sh [--update]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../template/{{cookiecutter.project_slug}}"
UPDATE_MODE="${1:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Cookiecutter Template Dependency Checker${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo

# ============================================================================
# Python Dependencies (pyproject.toml)
# ============================================================================
check_python_deps() {
    echo -e "${YELLOW}📦 Checking Python dependencies...${NC}"

    local pyproject="$TEMPLATE_DIR/backend/pyproject.toml"

    if [[ ! -f "$pyproject" ]]; then
        echo -e "${RED}  ✗ pyproject.toml not found${NC}"
        return 1
    fi

    # Extract pinned packages (format: "package==version" or "package>=version,<version")
    local packages
    packages=$(grep -oP '^\s+"[a-zA-Z0-9_-]+[^"]*' "$pyproject" | \
               sed 's/^\s*"//; s/"$//' | \
               grep -E '==' | \
               sed 's/\[.*\]//' | \
               head -30)

    echo -e "  Current pinned versions in pyproject.toml:"
    echo

    while IFS= read -r line; do
        if [[ -z "$line" ]]; then continue; fi

        pkg=$(echo "$line" | sed 's/==.*//' | sed 's/>.*//' | tr -d ' ')
        current=$(echo "$line" | grep -oP '==\K[0-9]+\.[0-9]+\.[0-9]+' || echo "unpinned")

        # Query PyPI for latest
        latest=$(curl -s "https://pypi.org/pypi/$pkg/json" 2>/dev/null | \
                 python3 -c "import sys, json; d=json.load(sys.stdin); print(d['info']['version'])" 2>/dev/null || echo "unknown")

        if [[ "$current" == "$latest" ]]; then
            echo -e "  ${GREEN}✓${NC} $pkg: $current (up to date)"
        elif [[ "$latest" == "unknown" ]]; then
            echo -e "  ${YELLOW}?${NC} $pkg: $current (couldn't check)"
        else
            echo -e "  ${RED}↑${NC} $pkg: $current → $latest"
        fi
    done <<< "$packages"
    echo
}

# ============================================================================
# npm Dependencies (package.json)
# ============================================================================
check_npm_deps() {
    echo -e "${YELLOW}📦 Checking npm dependencies...${NC}"

    local package_json="$TEMPLATE_DIR/frontend/package.json"

    if [[ ! -f "$package_json" ]]; then
        echo -e "${RED}  ✗ package.json not found${NC}"
        return 1
    fi

    # Check if npm-check-updates is available
    if command -v npx &> /dev/null; then
        echo "  Running npm-check-updates..."
        echo
        cd "$TEMPLATE_DIR/frontend"

        if [[ "$UPDATE_MODE" == "--update" ]]; then
            npx npm-check-updates -u
            echo -e "\n${GREEN}  ✓ package.json updated. Run 'npm install' to update lock file.${NC}"
        else
            npx npm-check-updates
        fi
        cd - > /dev/null
    else
        echo -e "${YELLOW}  ⚠ npx not found, showing current versions only${NC}"
        python3 -c "
import json
with open('$package_json') as f:
    data = json.load(f)
for section in ['dependencies', 'devDependencies']:
    if section in data:
        print(f'\n  {section}:')
        for pkg, ver in data[section].items():
            print(f'    {pkg}: {ver}')
"
    fi
    echo
}

# ============================================================================
# Docker Base Images
# ============================================================================
check_docker_images() {
    echo -e "${YELLOW}🐳 Checking Docker base images...${NC}"

    for dockerfile in "$TEMPLATE_DIR"/*/Dockerfile; do
        if [[ ! -f "$dockerfile" ]]; then continue; fi

        echo "  $dockerfile:"
        grep -E "^FROM " "$dockerfile" | while read -r line; do
            echo "    $line"
        done
    done
    echo
    echo -e "  ${BLUE}ℹ${NC}  Check Docker Hub or GitHub registries for latest tags"
    echo
}

# ============================================================================
# Service Versions (compose.yml)
# ============================================================================
check_compose_services() {
    echo -e "${YELLOW}🔧 Checking compose.yml service versions...${NC}"

    local compose_file="$TEMPLATE_DIR/compose.yml"

    if [[ ! -f "$compose_file" ]]; then
        echo -e "${RED}  ✗ compose.yml not found${NC}"
        return 1
    fi

    echo "  Service images in compose.yml:"
    grep -E "^\s+image:" "$compose_file" | sed 's/image:/  /' | while read -r line; do
        echo "   $line"
    done
    echo
}

# ============================================================================
# cookiecutter.json version defaults
# ============================================================================
check_cookiecutter_versions() {
    echo -e "${YELLOW}⚙️  Checking cookiecutter.json version defaults...${NC}"

    local cc_json="$SCRIPT_DIR/../template/cookiecutter.json"

    if [[ ! -f "$cc_json" ]]; then
        echo -e "${RED}  ✗ cookiecutter.json not found${NC}"
        return 1
    fi

    echo "  Version-related defaults:"
    python3 -c "
import json
with open('$cc_json') as f:
    data = json.load(f)
for key, val in data.items():
    if 'version' in key.lower() or key in ['postgres_version', 'redis_version', 'keycloak_version', 'python_version', 'node_version']:
        print(f'    {key}: {val}')
"
    echo
}

# ============================================================================
# Main
# ============================================================================
main() {
    if [[ "$UPDATE_MODE" == "--update" ]]; then
        echo -e "${YELLOW}Running in UPDATE mode - will modify files${NC}\n"
    else
        echo -e "${BLUE}Running in CHECK mode - use --update to modify files${NC}\n"
    fi

    check_cookiecutter_versions
    check_python_deps
    check_npm_deps
    check_docker_images
    check_compose_services

    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Done! Review the output above for outdated dependencies.${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    if [[ "$UPDATE_MODE" != "--update" ]]; then
        echo
        echo "  Next steps:"
        echo "    1. Run with --update to auto-update npm dependencies"
        echo "    2. Manually update Python versions in pyproject.toml"
        echo "    3. Update Docker base image tags in Dockerfiles"
        echo "    4. Run template validation: pytest template/tests/ -v"
        echo
    fi
}

main
