"""Cookiecutter option combinations for validation testing.

This module defines all possible combinations of boolean cookiecutter options
to enable comprehensive template validation testing.
"""

import itertools
from typing import Any

# Boolean options that create conditional content
CONDITIONAL_OPTIONS: dict[str, list[str]] = {
    "include_observability": ["yes", "no"],
    "include_github_actions": ["yes", "no"],
    "include_kubernetes": ["yes", "no"],
    "include_sentry": ["yes", "no"],
}

# Minimum test matrix (covers key combinations for fast CI)
MINIMUM_TEST_MATRIX: list[dict[str, str]] = [
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
    # Full production setup (duplicate of first but named differently for clarity)
    {
        "include_observability": "yes",
        "include_github_actions": "yes",
        "include_kubernetes": "yes",
        "include_sentry": "yes",
    },
]


def generate_full_matrix() -> list[dict[str, str]]:
    """Generate all possible option combinations.

    Returns:
        List of 16 dictionaries, each representing one combination of the 4 boolean options.
    """
    options = list(CONDITIONAL_OPTIONS.keys())
    values = list(CONDITIONAL_OPTIONS.values())

    combinations = []
    for combo in itertools.product(*values):
        combinations.append(dict(zip(options, combo)))

    return combinations


# Full matrix (2^4 = 16 combinations)
FULL_TEST_MATRIX: list[dict[str, str]] = generate_full_matrix()


# Default values for non-conditional options
DEFAULT_OPTIONS: dict[str, Any] = {
    "project_name": "Test Project",
    "project_slug": "test-project",
    "project_short_description": "A test project for validation",
    "author_name": "Test Author",
    "author_email": "test@example.com",
    "github_username": "test-user",
    "postgres_version": "18",
    "postgres_db": "test_project_db",
    "postgres_user": "test_project_user",
    "postgres_password": "test_password",
    "postgres_port": "5435",
    "postgres_app_user": "test_project_app_user",
    "postgres_app_password": "app_password_dev",
    "postgres_migration_user": "test_project_migration_user",
    "postgres_migration_password": "migration_password_dev",
    "redis_version": "7",
    "redis_password": "test_project_redis_pass",
    "redis_port": "6379",
    "keycloak_version": "23.0",
    "keycloak_port": "8080",
    "keycloak_admin": "admin",
    "keycloak_admin_password": "admin",
    "keycloak_realm_name": "test-project-dev",
    "keycloak_backend_client_id": "test-project-backend",
    "keycloak_frontend_client_id": "test-project-frontend",
    "backend_port": "8000",
    "backend_api_prefix": "/api/v1",
    "python_version": "3.13",
    "frontend_port": "5173",
    "node_version": "20",
    "sentry_dsn": "",
    "include_security_headers": "yes",
    "prometheus_version": "v2.54.1",
    "grafana_version": "11.3.0",
    "loki_version": "3.2.1",
    "promtail_version": "3.2.1",
    "tempo_version": "2.6.1",
    "grafana_port": "3000",
    "prometheus_port": "9090",
    "loki_port": "3100",
    "tempo_http_port": "3200",
    "tempo_otlp_grpc_port": "4317",
    "tempo_otlp_http_port": "4318",
    "license": "MIT",
}


def get_combination_id(options: dict[str, str]) -> str:
    """Generate a unique identifier for a combination of options.

    Args:
        options: Dictionary of option names to values.

    Returns:
        A string identifier like "obs-yes_gh-no_k8s-no_sentry-no".
    """
    abbreviations = {
        "include_observability": "obs",
        "include_github_actions": "gh",
        "include_kubernetes": "k8s",
        "include_sentry": "sentry",
    }
    parts = []
    for key, abbr in abbreviations.items():
        if key in options:
            parts.append(f"{abbr}-{options[key]}")
    return "_".join(parts)


def merge_options(custom_options: dict[str, str]) -> dict[str, Any]:
    """Merge custom options with default options.

    Args:
        custom_options: Dictionary of custom option values.

    Returns:
        Complete options dictionary with defaults filled in.
    """
    return {**DEFAULT_OPTIONS, **custom_options}


# Human-readable names for test combinations
COMBINATION_NAMES: dict[str, str] = {
    "obs-yes_gh-yes_k8s-yes_sentry-yes": "All Features Enabled",
    "obs-no_gh-no_k8s-no_sentry-no": "All Features Disabled",
    "obs-yes_gh-no_k8s-no_sentry-no": "Observability Only",
    "obs-no_gh-yes_k8s-no_sentry-no": "GitHub Actions Only",
    "obs-no_gh-no_k8s-yes_sentry-no": "Kubernetes Only",
    "obs-no_gh-no_k8s-no_sentry-yes": "Sentry Only",
    "obs-yes_gh-yes_k8s-no_sentry-no": "Observability + CI",
    "obs-yes_gh-no_k8s-yes_sentry-no": "Observability + K8s",
    "obs-yes_gh-no_k8s-no_sentry-yes": "Observability + Sentry",
    "obs-no_gh-yes_k8s-yes_sentry-no": "CI + K8s",
    "obs-no_gh-yes_k8s-no_sentry-yes": "CI + Sentry",
    "obs-no_gh-no_k8s-yes_sentry-yes": "K8s + Sentry",
    "obs-yes_gh-yes_k8s-yes_sentry-no": "All except Sentry",
    "obs-yes_gh-yes_k8s-no_sentry-yes": "All except K8s",
    "obs-yes_gh-no_k8s-yes_sentry-yes": "All except CI",
    "obs-no_gh-yes_k8s-yes_sentry-yes": "All except Observability",
}
