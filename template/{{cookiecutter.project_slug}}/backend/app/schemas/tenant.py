"""
Pydantic schemas for tenant data.

This module provides Pydantic models for tenant information used in API
responses and caching. The TenantInfo schema can be serialized to JSON for
Redis caching and is used by the tenant resolver service.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TenantInfo(BaseModel):
    """
    Tenant information schema for API responses and caching.

    This schema is used by the tenant resolver service and can be
    serialized to JSON for Redis caching. It provides a lightweight
    representation of tenant data optimized for caching and API responses.

    Attributes:
        id: Tenant UUID (primary key)
        slug: Tenant slug (URL-safe identifier)
        name: Tenant display name
        is_active: Whether tenant is active (soft delete flag)
        created_at: Tenant creation timestamp (UTC)
        updated_at: Tenant last update timestamp (UTC)
        settings: Tenant-specific settings (JSONB)
    """

    id: UUID = Field(..., description="Tenant UUID")
    slug: str = Field(..., description="Tenant slug (URL-safe identifier)")
    name: str = Field(..., description="Tenant display name")
    is_active: bool = Field(..., description="Whether tenant is active")
    created_at: datetime = Field(..., description="Tenant creation timestamp")
    updated_at: datetime = Field(..., description="Tenant last update timestamp")
    settings: Optional[dict] = Field(
        None, description="Tenant-specific settings (JSONB)"
    )

    class Config:
        """Pydantic model configuration."""

        from_attributes = True  # Enables ORM mode for SQLAlchemy models


class TenantNotFoundError(Exception):
    """
    Raised when tenant cannot be found.

    This exception is raised by the tenant resolver when a tenant with the
    specified ID, slug, or subdomain does not exist in the database.
    """

    pass


class TenantInactiveError(Exception):
    """
    Raised when tenant is not active.

    This exception is raised by the tenant resolver when a tenant exists but
    is marked as inactive (soft deleted) and require_active=True is specified.
    """

    pass
