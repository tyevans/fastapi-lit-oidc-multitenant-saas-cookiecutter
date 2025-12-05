"""Authentication dependencies for OAuth token validation."""
import logging
import uuid
from typing import Annotated, Optional

import httpx
import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)
from pydantic import ValidationError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.security import get_unverified_jwt_header
from app.core.rate_limit import get_rate_limiter, RateLimiter, RateLimitExceeded
from app.schemas.auth import AuthenticatedUser, TokenPayload
from app.services.jwks_client import get_jwks_client, JWKSClient
from app.services.token_revocation import (
    get_token_revocation_service,
    TokenRevocationService,
)

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Depends(security)
    ],
    jwks_client: Annotated[JWKSClient, Depends(get_jwks_client)],
    rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
    token_revocation_service: Annotated[
        TokenRevocationService, Depends(get_token_revocation_service)
    ],
) -> AuthenticatedUser:
    """
    FastAPI dependency to validate OAuth token and extract user context.

    This dependency implements the complete OAuth 2.0 Bearer token validation flow:
    1. Rate limiting check (prevents brute force/DoS attacks)
    2. Extracts Bearer token from Authorization header
    3. Validates JWT signature using JWKS public keys
    4. Validates standard JWT claims (exp, iss, aud, jti)
    5. Checks if token has been revoked (supports logout and security incidents)
    6. Extracts user context (user_id, tenant_id, scopes)
    7. Returns AuthenticatedUser for use in route handlers

    The dependency handles key rotation by attempting to refresh JWKS when a
    signing key is not found in the cache. It also enforces multi-tenant
    architecture by requiring a tenant_id claim in all tokens.

    Rate limiting prevents:
    - Brute force authentication attacks
    - Denial of service attacks
    - Token enumeration attacks

    Token revocation enables:
    - Secure logout (invalidate access tokens immediately)
    - Compromised token invalidation
    - Forced logout for security incidents

    Args:
        request: FastAPI Request object (for extracting client IP)
        credentials: HTTP Bearer credentials from Authorization header
        jwks_client: JWKS client for fetching OAuth provider public keys
        rate_limiter: Rate limiter for distributed rate limiting
        token_revocation_service: Token revocation service for blacklist checking

    Returns:
        AuthenticatedUser: Authenticated user context with user_id, tenant_id, and scopes

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, revoked, or missing
        HTTPException: 429 Too Many Requests if rate limit exceeded
        HTTPException: 503 Service Unavailable if JWKS fetch or revocation check fails

    Example:
        >>> from app.api.dependencies.auth import get_current_user
        >>>
        >>> @router.get("/protected")
        >>> async def protected_route(user: Annotated[AuthenticatedUser, Depends(get_current_user)]):
        ...     return {"user_id": user.user_id, "tenant_id": user.tenant_id}
    """
    # Extract client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"

    # SECURITY: Rate limiting - Check general auth rate limit
    # This prevents brute force attacks and DoS by limiting requests per IP
    try:
        await rate_limiter.check_rate_limit(client_ip, is_failed_auth=False)
    except RateLimitExceeded as e:
        logger.warning(
            "Rate limit exceeded for authentication",
            extra={
                "client_ip": client_ip,
                "limit_type": e.limit_type,
                "retry_after": e.retry_after,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "error_description": "Too many authentication attempts. Please try again later.",
            },
            headers={"Retry-After": str(e.retry_after)},
        )

    # Check if Authorization header is present
    if credentials is None:
        logger.warning("Missing Authorization header")
        # Track failed auth attempt before raising
        try:
            await rate_limiter.check_rate_limit(client_ip, is_failed_auth=True)
        except RateLimitExceeded as e:
            logger.warning(
                "Failed auth rate limit exceeded",
                extra={
                    "client_ip": client_ip,
                    "retry_after": e.retry_after,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "error_description": "Too many failed authentication attempts. Please try again later.",
                },
                headers={"Retry-After": str(e.retry_after)},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "missing_token",
                "error_description": "Authorization header with Bearer token is required",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Wrap entire validation in try-except to track failed auth attempts
    try:
        # Extract header to get key ID (kid) before validation
        return await _validate_token_and_get_user(token, jwks_client, token_revocation_service)
    except HTTPException as e:
        # Check if this is an auth failure (401) that should count toward failed auth rate limit
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            # Track failed auth attempt
            try:
                await rate_limiter.check_rate_limit(client_ip, is_failed_auth=True)
            except RateLimitExceeded as rate_limit_err:
                logger.warning(
                    "Failed auth rate limit exceeded",
                    extra={
                        "client_ip": client_ip,
                        "retry_after": rate_limit_err.retry_after,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limit_exceeded",
                        "error_description": "Too many failed authentication attempts. Please try again later.",
                    },
                    headers={"Retry-After": str(rate_limit_err.retry_after)},
                )
        # Re-raise the original HTTPException (auth failure or other error)
        raise


async def _validate_token_and_get_user(
    token: str,
    jwks_client: JWKSClient,
    token_revocation_service: TokenRevocationService,
) -> AuthenticatedUser:
    """
    Internal helper to validate token and extract user context.

    Separated from get_current_user to allow clean try-except wrapping
    for failed auth tracking.

    Args:
        token: JWT token string
        jwks_client: JWKS client for fetching OAuth provider public keys
        token_revocation_service: Token revocation service for blacklist checking

    Returns:
        AuthenticatedUser: Authenticated user context

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or revoked
        HTTPException: 503 Service Unavailable if JWKS fetch or revocation check fails
    """
    # Extract header to get key ID (kid) before validation
    try:
        header = get_unverified_jwt_header(token)
        key_id = header.get("kid")
        alg = header.get("alg")

        # SECURITY: Prevent algorithm confusion attacks
        # Validate algorithm before signature verification to prevent:
        # 1. alg: "none" bypass attack
        # 2. HMAC/RSA confusion attack (using public key as HMAC secret)
        if not alg or alg not in settings.OAUTH_ALGORITHMS:
            logger.warning(
                "Unsupported or missing JWT algorithm",
                extra={"algorithm": alg, "expected": settings.OAUTH_ALGORITHMS}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_token",
                    "error_description": "Unsupported JWT algorithm",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # SECURITY: Only allow asymmetric algorithms (RS256, RS384, RS512, ES256, etc.)
        # Reject symmetric algorithms (HS256, HS384, HS512) to prevent
        # attackers from using the public key as an HMAC secret
        if alg.startswith("HS"):
            logger.warning(
                "Symmetric algorithm rejected",
                extra={"algorithm": alg}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_token",
                    "error_description": "Only asymmetric algorithms supported",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not key_id:
            logger.warning("JWT header missing 'kid' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_token",
                    "error_description": "JWT header missing 'kid' (key ID) claim",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

    except DecodeError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "error_description": "Malformed JWT token",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch signing key from JWKS
    try:
        signing_key = await jwks_client.get_signing_key(
            settings.OAUTH_ISSUER_URL, key_id, force_refresh=False
        )

        if signing_key is None:
            # Key not found - try refreshing JWKS (handles key rotation)
            logger.info(
                f"Signing key not found, refreshing JWKS (kid: {key_id})"
            )
            signing_key = await jwks_client.get_signing_key(
                settings.OAUTH_ISSUER_URL, key_id, force_refresh=True
            )

            if signing_key is None:
                logger.error(
                    f"Signing key not found after refresh (kid: {key_id})"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "invalid_token",
                        "error_description": "Signing key not found in JWKS",
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )

    except httpx.HTTPError as e:
        logger.error(f"JWKS fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "service_unavailable",
                "error_description": "Unable to fetch signing keys from OAuth provider",
            },
        )

    # Validate and decode JWT
    try:
        # Use PyJWT to validate signature and claims
        payload = jwt.decode(
            token,
            key=jwt.PyJWK(signing_key).key,  # Convert JWK to cryptography key
            algorithms=settings.OAUTH_ALGORITHMS,
            issuer=settings.OAUTH_ISSUER_URL,
            audience=settings.OAUTH_AUDIENCE,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
                "verify_iat": True,  # SECURITY: Prevent future-dated tokens
            },
        )

        # Parse payload into TokenPayload model (validates structure)
        token_payload = TokenPayload(**payload)

    except ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "expired_token",
                "error_description": "JWT token has expired",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidSignatureError as e:
        logger.warning(f"JWT signature validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "error_description": "JWT signature validation failed",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError as e:
        # SECURITY: Log detailed error server-side only, return generic message to client
        # to prevent information disclosure that could aid attackers
        logger.warning(
            "JWT validation failed",
            extra={
                "error_type": type(e).__name__,
                "error_details": str(e),
                "token_header": header,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "error_description": "JWT validation failed",  # Generic message
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    except ValidationError as e:
        # SECURITY: Token payload validation failed (e.g., missing required claims like jti)
        # Log detailed error server-side only, return generic message to client
        logger.warning(
            "JWT payload validation failed",
            extra={
                "error_type": "ValidationError",
                "error_details": str(e),
                "token_header": header,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "error_description": "JWT validation failed",  # Generic message
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # SECURITY: Check if token has been revoked (blacklist check)
    # This enables secure logout, compromised token invalidation, and forced logout
    try:
        is_revoked = await token_revocation_service.is_token_revoked(token_payload.jti)
        if is_revoked:
            logger.warning(
                "Token has been revoked",
                extra={
                    "jti": token_payload.jti,
                    "sub": token_payload.sub,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_token",
                    "error_description": "Token has been revoked",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        # Re-raise HTTP exceptions (401 for revoked token)
        raise
    except Exception as e:
        # SECURITY: Fail closed - if revocation check fails, reject the token
        # This prioritizes security over availability
        logger.error(
            "Token revocation check failed - rejecting token (fail closed)",
            extra={
                "jti": token_payload.jti,
                "error_type": type(e).__name__,
                "error_details": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "service_unavailable",
                "error_description": "Unable to verify token revocation status",
            },
        )

    # Extract tenant_id from custom claim (required for multi-tenancy)
    tenant_id = token_payload.tenant_id
    if not tenant_id:
        logger.error(
            "JWT missing required 'tenant_id' claim",
            extra={"sub": token_payload.sub},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "error_description": "JWT missing required 'tenant_id' claim",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # SECURITY: Validate tenant_id is a valid UUID format
    # This prevents SQL injection, path traversal, XSS, and other injection attacks
    # that could exploit tenant_id in database queries or file operations
    try:
        uuid_obj = uuid.UUID(tenant_id)
        # Normalize to lowercase canonical format (prevents case-based attacks)
        tenant_id = str(uuid_obj).lower()
    except (ValueError, AttributeError) as e:
        logger.error(
            "Invalid tenant_id format in JWT token",
            extra={
                "tenant_id": tenant_id,
                "user_id": token_payload.sub,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "error_description": "Invalid tenant_id format",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse scopes from space-separated string
    scopes = token_payload.scope.split() if token_payload.scope else []

    # Add Keycloak realm roles to scopes (roles are used as scopes in this system)
    if token_payload.realm_access and token_payload.realm_access.roles:
        scopes.extend(token_payload.realm_access.roles)

    # Log successful authentication
    logger.info(
        "User authenticated successfully",
        extra={
            "user_id": token_payload.sub,
            "tenant_id": tenant_id,
            "scopes": scopes,
        },
    )

    # Return authenticated user context
    return AuthenticatedUser(
        user_id=token_payload.sub,
        tenant_id=tenant_id,
        jti=token_payload.jti,
        exp=token_payload.exp,
        email=token_payload.email,
        name=token_payload.name,
        scopes=scopes,
        issuer=token_payload.iss,
    )


# Type alias for dependency injection
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
