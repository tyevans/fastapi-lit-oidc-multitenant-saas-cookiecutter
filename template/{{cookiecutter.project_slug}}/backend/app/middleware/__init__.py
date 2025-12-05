"""
Middleware package for FastAPI application.

This package contains middleware components for cross-cutting concerns
such as tenant resolution, authentication, logging, and metrics.
"""

from app.middleware.tenant import TenantResolutionMiddleware

__all__ = ["TenantResolutionMiddleware"]
