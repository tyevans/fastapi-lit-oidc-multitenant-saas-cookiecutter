#!/usr/bin/env python3
"""
Post-generation hook for {{ cookiecutter.project_name }}
This script runs after the cookiecutter template has been generated.
"""
import os
import shutil
import subprocess
from pathlib import Path

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Cookiecutter context variables
include_observability = "{{ cookiecutter.include_observability }}"


def print_info(msg):
    print(f"{BLUE}[INFO]{NC} {msg}")


def print_success(msg):
    print(f"{GREEN}[SUCCESS]{NC} {msg}")


def print_warning(msg):
    print(f"{YELLOW}[WARNING]{NC} {msg}")


def remove_observability_files(project_dir: Path) -> None:
    """Remove observability-related files when observability is disabled."""
    if include_observability.lower() == "no":
        print_info("Observability disabled - removing observability files...")

        # Remove observability directory
        observability_dir = project_dir / "observability"
        if observability_dir.exists():
            shutil.rmtree(observability_dir)
            print_success("Removed observability/ directory")

        # Remove backend observability module
        observability_module = project_dir / "backend" / "app" / "observability.py"
        if observability_module.exists():
            observability_module.unlink()
            print_success("Removed backend/app/observability.py")
    else:
        print_info("Observability enabled - keeping observability files")


def main():
    """Main post-generation setup."""
    project_dir = Path.cwd()

    print_info("Running post-generation setup...")

    # 1. Handle conditional file removal
    remove_observability_files(project_dir)

    # 2. Make scripts executable
    print_info("Making scripts executable...")
    scripts_to_chmod = [
        project_dir / "scripts" / "docker-dev.sh",
        project_dir / "keycloak" / "setup-realm.sh",
        project_dir / "keycloak" / "export-realm.sh",
        project_dir / "backend" / "scripts" / "verify_seed_data.py",
        project_dir / "backend" / "scripts" / "verify_api.py",
    ]

    for script in scripts_to_chmod:
        if script.exists():
            os.chmod(script, 0o755)
            print_success(f"Made {script.name} executable")

    # 3. Create .env file if it doesn't exist
    env_file = project_dir / ".env"
    env_example = project_dir / ".env.example"

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print_success("Created .env from .env.example")
        print_warning("⚠️  Please review and update .env with your configuration")

    # 4. Generate uv.lock file for backend
    print_info("Generating uv.lock for backend dependencies...")
    backend_dir = project_dir / "backend"
    if backend_dir.exists():
        try:
            subprocess.run(
                ["uv", "lock"],
                cwd=backend_dir,
                check=True,
                capture_output=True
            )
            print_success("Generated uv.lock file")
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to generate uv.lock: {e}")
            print_warning("You will need to run 'uv lock' in the backend directory before building")
        except FileNotFoundError:
            print_warning("uv not found - skipping uv.lock generation")
            print_warning("Install uv and run 'uv lock' in the backend directory before building")

    # 5. Initialize git repository
    print_info("Initializing git repository...")
    git_dir = project_dir / ".git"
    if not git_dir.exists():
        try:
            subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
            print_success("Initialized git repository")
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to initialize git repository: {e}")
        except FileNotFoundError:
            print_warning("git not found - skipping git initialization")

    # 6. Create .gitignore if it doesn't exist
    gitignore_file = project_dir / ".gitignore"
    if not gitignore_file.exists():
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.pytest_cache/
.ruff_cache/
*.egg-info/
dist/
build/

# Node
node_modules/
dist/
build/
.next/
.vite/
npm-debug.log*

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Docker
.docker/

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite

# Logs
*.log

# Test coverage
.coverage
coverage/
htmlcov/
"""
        gitignore_file.write_text(gitignore_content)
        print_success("Created .gitignore")

    # 7. Create initial git commit
    if git_dir.exists():
        print_info("Creating initial git commit...")
        try:
            subprocess.run(["git", "add", "."], cwd=project_dir, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from cookiecutter template"],
                cwd=project_dir,
                check=True,
                capture_output=True
            )
            print_success("Created initial git commit")
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to create initial commit: {e}")

    # 8. Print next steps
    print()
    print_success("=" * 60)
    print_success(f"  {{ cookiecutter.project_name }} - Project Generated!")
    print_success("=" * 60)
    print()
    print_info("Next steps:")
    print()
    print("  1. Review and update .env file:")
    print("     $ nano .env")
    print()
    print("  2. Start the Docker environment:")
    print("     $ ./scripts/docker-dev.sh up")
    print()
    print("  3. Wait for services to be healthy (about 1-2 minutes)")
    print()
    print("  4. Set up Keycloak realm:")
    print("     $ ./keycloak/setup-realm.sh")
    print()
    print("  5. Run database migrations:")
    print("     $ ./scripts/docker-dev.sh shell backend")
    print("     container# alembic upgrade head")
    print()
    print("  6. Access your application:")
    print(f"     - Frontend:  http://localhost:{{ cookiecutter.frontend_port }}")
    print(f"     - Backend:   http://localhost:{{ cookiecutter.backend_port }}")
    print(f"     - API Docs:  http://localhost:{{ cookiecutter.backend_port }}/docs")
    print(f"     - Keycloak:  http://localhost:{{ cookiecutter.keycloak_port }}")
    print()
    print_info("For more information, see README.md")
    print()


if __name__ == "__main__":
    main()
