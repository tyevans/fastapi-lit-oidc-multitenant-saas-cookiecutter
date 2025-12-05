# ADR-005: Row-Level Security for Multi-Tenancy

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template implements a multi-tenant architecture where multiple organizations (tenants) share the same application infrastructure while maintaining strict data isolation. Requirements include:

1. **Security**: Tenant data must be completely isolated; no tenant should ever access another tenant's data
2. **Defense in Depth**: Data isolation should not rely solely on application code
3. **Performance**: Tenant filtering should not significantly impact query performance
4. **Simplicity**: The solution should be maintainable and understandable
5. **Scalability**: Must support many tenants without operational complexity
6. **Development Experience**: Developers should not need to remember to add tenant filters

The system uses JWT tokens with a `tenant_id` claim to identify the current user's tenant.

## Decision

We chose **PostgreSQL Row-Level Security (RLS)** for tenant data isolation.

RLS is a PostgreSQL feature that automatically filters rows based on security policies. The database enforces tenant isolation at the query execution level, making it impossible for application code to accidentally (or maliciously) access other tenants' data.

**Schema with RLS** (`alembic/versions/e10757622a70_initial_schema.py`):
```python
# Enable RLS on tenant-scoped tables
op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
op.execute("ALTER TABLE oauth_providers ENABLE ROW LEVEL SECURITY")

# Create isolation policy
op.execute("""
    CREATE POLICY tenant_isolation_policy ON users
    USING (tenant_id = COALESCE(
        NULLIF(current_setting('app.current_tenant_id', TRUE), '')::UUID,
        '00000000-0000-0000-0000-000000000000'::UUID
    ))
""")
```

**Tenant Context Setting** (`backend/app/services/tenant_context.py`):
```python
async def set_tenant_context(session: AsyncSession, tenant_id: UUID) -> None:
    """Set PostgreSQL session variable for RLS tenant filtering."""
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, TRUE)"),
        {"tenant_id": str(tenant_id)}
    )
```

**Middleware Integration** (`backend/app/middleware/tenant.py`):
```python
class TenantResolutionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_id = await self._extract_tenant_id(request)
        if tenant_id:
            request.state.tenant_id = tenant_id
            set_current_tenant(tenant_id)
        return await call_next(request)
```

**Dual Database Users**:
- `app_user`: Normal user with RLS enforced - used by the application runtime
- `migration_user`: Has `BYPASSRLS` privilege - used only for Alembic migrations

## Consequences

### Positive

1. **Defense in Depth**: Even if application code has a bug that omits tenant filtering, the database enforces isolation. This is a critical security property:
   ```sql
   -- Without RLS, this returns ALL users
   SELECT * FROM users;

   -- With RLS and tenant context set, only returns current tenant's users
   SELECT * FROM users;  -- Automatically filtered
   ```

2. **Developer Safety**: Developers cannot accidentally forget to add `WHERE tenant_id = ?` - the database handles it automatically

3. **Simple Application Code**: No need for tenant filter mixins or base classes. Standard SQLAlchemy queries work correctly:
   ```python
   # No explicit tenant filter needed - RLS handles it
   result = await session.execute(select(User))
   users = result.scalars().all()  # Only current tenant's users
   ```

4. **Performance**: RLS policies are evaluated during query planning. PostgreSQL optimizes queries knowing the tenant filter, often using indexes on `tenant_id`

5. **Single Database**: All tenants share one database instance, simplifying operations, backups, and connection management

6. **Consistent Schema**: All tenants have identical schema, making upgrades straightforward (single migration applies to all data)

7. **SQL-Level Enforcement**: Works for any database access path - application code, database migrations, manual queries (when context is set)

### Negative

1. **PostgreSQL Specific**: RLS is a PostgreSQL feature. Migration to MySQL, SQLite, or other databases would require application-level filtering

2. **Context Management Complexity**: Every request must set `app.current_tenant_id` before database access. Missing context results in empty results (safe fail) but requires careful request handling

3. **Migration Complexity**: Migrations need `BYPASSRLS` to modify data across all tenants. Requires separate database user and connection configuration

4. **Debugging Difficulty**: When debugging, the implicit tenant filter can be confusing. Developers must understand RLS is active:
   ```python
   # In development, explicitly check context
   result = await session.execute(
       text("SELECT current_setting('app.current_tenant_id', TRUE)")
   )
   ```

5. **Cross-Tenant Operations**: System administration tasks (analytics, reporting across tenants) require explicit RLS bypass or superuser access

### Neutral

1. **Session Variable Approach**: Using `SET LOCAL` means the tenant context is transaction-scoped. Each request starts fresh, preventing context leakage between requests

2. **COALESCE Pattern**: The policy uses `COALESCE` to handle unset/empty context by comparing against a nil UUID, ensuring queries return no rows rather than failing

## Alternatives Considered

### Application-Level Filtering

**Approach**: Add `tenant_id` filter to every query in application code.

**Why Not Chosen**:
- **Security Risk**: Single missed filter exposes all tenants' data
- **Developer Burden**: Every query must include tenant filter
- **No Defense in Depth**: Security relies entirely on application code correctness
- **Code Duplication**: Tenant filter logic repeated throughout codebase

**Code Example (Not Used)**:
```python
# Every query would need this pattern
users = await session.execute(
    select(User).where(User.tenant_id == current_tenant_id)
)
```

### Separate Schemas per Tenant

**Approach**: Each tenant gets their own PostgreSQL schema (namespace).

**Why Not Chosen**:
- **Schema Management**: Creating schemas for new tenants is operational overhead
- **Migration Complexity**: Migrations must run against every schema
- **Connection Pooling**: Schema switching complicates connection management
- **Tenant Limits**: PostgreSQL has practical limits on schema count

### Separate Databases per Tenant

**Approach**: Each tenant gets their own PostgreSQL database.

**Why Not Chosen**:
- **Operational Overhead**: Managing N databases for N tenants doesn't scale
- **Resource Waste**: Each database has connection overhead
- **Cross-Tenant Queries**: Impossible for system administration
- **Cost**: Significantly more expensive at scale

### Django-Style Tenant Middleware with Query Filtering

**Approach**: Use SQLAlchemy events or custom base classes to auto-add filters.

**Why Not Chosen**:
- **Complexity**: Requires custom SQLAlchemy integration
- **Incomplete Coverage**: Raw SQL queries bypass the filtering
- **No Database Enforcement**: Still relies on application code

---

## Related ADRs

- [ADR-001: FastAPI as Backend Framework](./001-fastapi-backend-framework.md) - Middleware and dependency injection for context
- [ADR-004: Keycloak as Identity Provider](./004-keycloak-identity-provider.md) - Source of tenant_id claim

## Implementation References

- `backend/alembic/versions/e10757622a70_*.py` - RLS policy creation
- `backend/app/services/tenant_context.py` - Tenant context management
- `backend/app/middleware/tenant.py` - Tenant resolution middleware
- `backend/app/api/dependencies/tenant.py` - Tenant dependency injection
- `backend/app/core/config.py` - Database user configuration
