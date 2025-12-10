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

{%- if cookiecutter.include_sentry == "yes" %}
    # Sentry Configuration (Optional - P3-03)
    # Error tracking is enabled when SENTRY_DSN is set
    SENTRY_DSN: str = "{{ cookiecutter.sentry_dsn }}"  # Empty string disables Sentry
    SENTRY_ENVIRONMENT: str = "development"  # Environment tag (staging, production)
    SENTRY_RELEASE: str = ""  # Defaults to APP_VERSION if empty
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of requests traced for performance monitoring
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1  # 10% of traces profiled
{%- endif %}

    # ==========================================================================
    # Security Headers Configuration (P2-02)
    # These settings control the SecurityHeadersMiddleware behavior
    # Reference: OWASP Secure Headers Project
    # ==========================================================================

    # Master toggle for security headers
    SECURITY_HEADERS_ENABLED: bool = True

    # Content-Security-Policy (CSP)
    # Default allows Lit components (requires unsafe-inline for script/style)
    CSP_ENABLED: bool = True
    CSP_DEFAULT_SRC: str = "'self'"
    CSP_SCRIPT_SRC: str = "'self' 'unsafe-inline'"
    CSP_STYLE_SRC: str = "'self' 'unsafe-inline'"
    CSP_IMG_SRC: str = "'self' data: https:"
    CSP_FONT_SRC: str = "'self'"
    CSP_CONNECT_SRC: str = "'self'"  # Will be extended with FRONTEND_URL in main.py
    CSP_FRAME_ANCESTORS: str = "'none'"
    CSP_BASE_URI: str = "'self'"
    CSP_FORM_ACTION: str = "'self'"
    CSP_REPORT_URI: str = ""  # Empty = disabled, set to CSP reporting endpoint

    # Strict-Transport-Security (HSTS)
    # Only applied for HTTPS requests
    HSTS_ENABLED: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year in seconds
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    HSTS_PRELOAD: bool = False  # Requires careful consideration before enabling

    # Other Security Headers
    X_FRAME_OPTIONS: str = "DENY"  # DENY, SAMEORIGIN, or empty to disable
    X_CONTENT_TYPE_OPTIONS: str = "nosniff"
    REFERRER_POLICY: str = "strict-origin-when-cross-origin"
    PERMISSIONS_POLICY: str = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
    X_XSS_PROTECTION: str = "1; mode=block"  # Legacy but still useful

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
