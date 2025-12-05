"""
Authentication endpoints for OAuth token management.

This module provides endpoints for token management operations:
- Token revocation (logout)
- Token status checking (future)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies.auth import CurrentUser
from app.services.token_revocation import (
    get_token_revocation_service,
    TokenRevocationService,
)

router = APIRouter(tags=["auth"], prefix="/auth")


class RevokeTokenRequest(BaseModel):
    """Request model for token revocation (optional, for future extensions)."""

    # Future: Allow revoking specific tokens by jti
    # For now, we revoke the current token from the Authorization header
    pass


class RevokeTokenResponse(BaseModel):
    """Response model for successful token revocation."""

    message: str = Field(..., description="Success message")
    jti: str = Field(..., description="JWT ID of the revoked token")


@router.post(
    "/revoke",
    response_model=RevokeTokenResponse,
    summary="Revoke current access token",
    description="Revoke the current access token to implement secure logout. "
    "The token will be added to a blacklist and rejected for all future requests. "
    "This is useful for logout flows, compromised token invalidation, and forced logout.",
    responses={
        200: {
            "description": "Token revoked successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Token revoked successfully",
                        "jti": "cca5f515-b48f-4307-8152-ad3a031d832d",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {
                        "error": "invalid_token",
                        "error_description": "Authorization header with Bearer token is required",
                    }
                }
            },
        },
        503: {
            "description": "Service Unavailable - Token revocation service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "error": "service_unavailable",
                        "error_description": "Unable to revoke token at this time",
                    }
                }
            },
        },
    },
)
async def revoke_token(
    user: CurrentUser,
    token_revocation_service: Annotated[
        TokenRevocationService, Depends(get_token_revocation_service)
    ],
) -> RevokeTokenResponse:
    """
    Revoke the current access token (logout).

    This endpoint adds the current access token to a blacklist, preventing it from
    being used for authentication in future requests. This is the primary mechanism
    for implementing secure logout.

    The token is identified by its jti (JWT ID) claim, which is extracted from the
    authenticated user context. The token is added to Redis with a TTL matching the
    token's expiration time, ensuring automatic cleanup of expired tokens.

    Use Cases:
    - User logout: User explicitly logs out from the application
    - Security incident: Admin force-logs out a compromised account
    - Token rotation: Old token is revoked when new token is issued

    Security Notes:
    - The token must be valid and not already revoked to call this endpoint
    - After revocation, the token cannot be used again (401 Unauthorized)
    - Revocation is immediate and distributed across all backend instances
    - If Redis is unavailable, returns 503 Service Unavailable

    Args:
        user: Authenticated user context (from get_current_user dependency)
        token_revocation_service: Token revocation service for blacklist management

    Returns:
        RevokeTokenResponse: Success message with revoked token jti

    Raises:
        HTTPException: 401 Unauthorized if token is invalid
        HTTPException: 503 Service Unavailable if revocation service unavailable

    Example:
        >>> # curl -X POST http://localhost:8000/api/v1/auth/revoke \
        >>> #   -H "Authorization: Bearer <access_token>"
        >>> {
        ...   "message": "Token revoked successfully",
        ...   "jti": "cca5f515-b48f-4307-8152-ad3a031d832d"
        ... }
    """
    # Extract jti and exp from authenticated user context
    jti = user.jti
    exp = user.exp

    try:
        # Add token to revocation blacklist
        await token_revocation_service.revoke_token(jti=jti, exp=exp)

        return RevokeTokenResponse(
            message="Token revoked successfully",
            jti=jti,
        )

    except Exception as e:
        # If Redis is unavailable or revocation fails, return 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "service_unavailable",
                "error_description": "Unable to revoke token at this time",
            },
        )
