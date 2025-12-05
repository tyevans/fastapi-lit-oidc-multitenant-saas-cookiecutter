"""
Database models.

This module exports all database models for easy import throughout the
application. All models inherit from Base and include common audit columns
(id, created_at, updated_at).

Models:
    - Tenant: Organization or tenant in the multi-tenant system
    - User: User within a tenant, authenticated via OAuth
    - OAuthProvider: OAuth provider configuration for a tenant
    - ProviderType: Enum of supported OAuth provider types
"""

from app.models.oauth_provider import OAuthProvider, ProviderType
from app.models.tenant import Tenant
from app.models.user import User

__all__ = [
    "Tenant",
    "User",
    "OAuthProvider",
    "ProviderType",
]
