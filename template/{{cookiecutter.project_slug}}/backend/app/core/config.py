"""
Configuration management for the {{ cookiecutter.project_name }} backend.

Uses pydantic-settings to load configuration from environment variables
with sensible defaults for development.
"""

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "{{ cookiecutter.project_name }}"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "{{ cookiecutter.backend_api_prefix }}"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:{{ cookiecutter.frontend_port }}", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Database Configuration
    # Application runtime uses {{ cookiecutter.postgres_app_user }} (NO BYPASSRLS - RLS policies enforced)
    DATABASE_URL: str = "postgresql+asyncpg://{{ cookiecutter.postgres_app_user }}:{{ cookiecutter.postgres_app_password }}@postgres:{{ cookiecutter.postgres_port }}/{{ cookiecutter.postgres_db }}"

    # Migration database URL uses {{ cookiecutter.postgres_migration_user }} (with BYPASSRLS for schema management)
    MIGRATION_DATABASE_URL: str = "postgresql+asyncpg://{{ cookiecutter.postgres_migration_user }}:{{ cookiecutter.postgres_migration_password }}@postgres:{{ cookiecutter.postgres_port }}/{{ cookiecutter.postgres_db }}"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = {{ cookiecutter.backend_port }}
    RELOAD: bool = True

    # OAuth Configuration
    OAUTH_ISSUER_URL: str = "http://keycloak:{{ cookiecutter.keycloak_port }}/realms/{{ cookiecutter.keycloak_realm_name }}"
    OAUTH_AUDIENCE: str = "{{ cookiecutter.keycloak_backend_client_id }}"  # Expected 'aud' claim in tokens
    OAUTH_ALGORITHMS: List[str] = ["RS256"]  # Supported signing algorithms

    # JWKS Configuration
    JWKS_CACHE_TTL: int = 3600  # Cache JWKS for 1 hour (seconds)
    JWKS_HTTP_TIMEOUT: int = 10  # HTTP timeout for JWKS/OIDC requests (seconds)

    # OAuth Client Configuration (TASK-011)
    OAUTH_CLIENT_ID: str = "{{ cookiecutter.keycloak_backend_client_id }}"
    OAUTH_CLIENT_SECRET: str = "your-client-secret"  # Set via environment variable in production
    OAUTH_REDIRECT_URI: str = "http://localhost:{{ cookiecutter.backend_port }}{{ cookiecutter.backend_api_prefix }}/auth/callback"
    OAUTH_SCOPES: List[str] = ["openid", "profile", "email"]
    OAUTH_USE_PKCE: bool = True  # Enable PKCE for enhanced security

    # Redis Configuration
    REDIS_URL: str = "redis://default:{{ cookiecutter.redis_password }}@redis:{{ cookiecutter.redis_port }}/0"

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True  # Enable/disable rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100  # General auth request limit
    RATE_LIMIT_FAILED_AUTH_PER_MINUTE: int = 10  # Failed auth attempt limit
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # Time window for rate limiting

    # Session Configuration (TASK-012)
    SESSION_COOKIE_SECURE: bool = False  # Set Secure flag on cookies (True for HTTPS in production)
    SESSION_COOKIE_MAX_AGE: int = 86400 * 7  # Max age for session cookies (7 days)
    FRONTEND_URL: str = "http://localhost:{{ cookiecutter.frontend_port }}"  # Frontend URL for post-auth redirect

    # Multi-Tenancy Configuration
    TENANT_CLAIM_NAME: str = "tenant_id"  # Claim name in OAuth token for tenant ID
    REQUIRE_TENANT_CLAIM: bool = True  # Require tenant claim in all OAuth tokens

    # Tenant Resolver Configuration (TASK-016)
    TENANT_CACHE_TTL: int = 3600  # Tenant cache TTL in seconds (1 hour)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            return v
        return []


# Global settings instance
settings = Settings()
