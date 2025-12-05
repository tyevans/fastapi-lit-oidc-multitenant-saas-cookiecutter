"""Authentication schemas for OAuth token validation."""
from typing import List, Optional, Union

from pydantic import BaseModel, Field


# OAuth Scope Constants for xAPI Endpoints
# These constants define the available OAuth 2.0 scopes for the API.
# Scopes control fine-grained access to xAPI resources following the principle
# of least privilege. These scope names MUST match the scopes configured in
# Keycloak (TASK-007) for token validation to work correctly.

# xAPI Statement Scopes
SCOPE_STATEMENTS_READ = "statements/read"
"""Read access to all xAPI statements in the tenant."""

SCOPE_STATEMENTS_WRITE = "statements/write"
"""Write access to create/update xAPI statements."""

SCOPE_STATEMENTS_READ_MINE = "statements/read/mine"
"""Read access to only the user's own xAPI statements."""

# xAPI State Scopes
SCOPE_STATE_READ = "state/read"
"""Read access to xAPI state resources."""

SCOPE_STATE_WRITE = "state/write"
"""Write access to xAPI state resources."""

# Admin Scopes
SCOPE_ADMIN = "admin"
"""System-wide administrative access."""

SCOPE_TENANT_ADMIN = "tenant/admin"
"""Tenant-level administrative access."""

# All defined scopes (for validation and documentation)
ALL_SCOPES = {
    SCOPE_STATEMENTS_READ,
    SCOPE_STATEMENTS_WRITE,
    SCOPE_STATEMENTS_READ_MINE,
    SCOPE_STATE_READ,
    SCOPE_STATE_WRITE,
    SCOPE_ADMIN,
    SCOPE_TENANT_ADMIN,
}


class RealmAccess(BaseModel):
    """Keycloak realm_access claim containing user roles."""

    roles: List[str] = Field(default_factory=list, description="User's realm roles")


class TokenPayload(BaseModel):
    """
    JWT token payload with standard and custom claims.

    This model validates the structure of decoded JWT tokens before
    extracting user context. It includes both standard OAuth claims
    (sub, iss, aud, exp, iat, jti) and custom claims (tenant_id).

    The jti (JWT ID) claim is required for token revocation support.
    """

    sub: str = Field(..., description="Subject (user ID from OAuth provider)")
    iss: str = Field(..., description="Issuer (OAuth provider URL)")
    aud: Union[str, List[str]] = Field(
        ..., description="Audience (client ID or API identifier)"
    )
    exp: int = Field(..., description="Expiration time (Unix timestamp)")
    iat: int = Field(..., description="Issued at time (Unix timestamp)")
    jti: str = Field(..., description="JWT ID (unique token identifier for revocation)")
    tenant_id: Optional[str] = Field(None, description="Tenant ID (custom claim)")
    scope: Optional[str] = Field(
        None, description="OAuth scopes (space-separated)"
    )
    realm_access: Optional[RealmAccess] = Field(
        None, description="Keycloak realm access with roles"
    )
    email: Optional[str] = Field(None, description="User email address")
    name: Optional[str] = Field(None, description="User full name")
    preferred_username: Optional[str] = Field(
        None, description="Preferred username"
    )


class AuthenticatedUser(BaseModel):
    """
    Authenticated user context extracted from validated JWT token.

    This model represents the user identity after successful token validation.
    It's injected into route handlers via the get_current_user() dependency.

    All authenticated requests MUST include a tenant_id for multi-tenant isolation.
    The jti and exp fields are included to support token revocation.
    """

    user_id: str = Field(..., description="User ID (OAuth subject claim)")
    tenant_id: str = Field(
        ..., description="Tenant ID (required for multi-tenancy)"
    )
    jti: str = Field(..., description="JWT ID (unique token identifier)")
    exp: int = Field(..., description="Token expiration time (Unix timestamp)")
    email: Optional[str] = Field(None, description="User email address")
    name: Optional[str] = Field(None, description="User display name")
    scopes: List[str] = Field(
        default_factory=list, description="OAuth scopes granted"
    )
    issuer: str = Field(..., description="OAuth issuer URL")

    def has_scope(self, scope: str) -> bool:
        """
        Check if user has a specific scope.

        Args:
            scope: OAuth scope to check (e.g., "statements/write")

        Returns:
            True if user has the scope, False otherwise

        Example:
            >>> user.has_scope("statements/write")
            True
        """
        return scope in self.scopes


class AuthError(BaseModel):
    """
    Authentication error response following OAuth 2.0 error format.

    Used to return structured error responses for authentication failures.
    Follows RFC 6750 (Bearer Token Usage) error response format.
    """

    error: str = Field(
        ...,
        description="Error type (e.g., 'invalid_token', 'expired_token', 'missing_token')",
    )
    error_description: str = Field(
        ..., description="Human-readable error description"
    )
