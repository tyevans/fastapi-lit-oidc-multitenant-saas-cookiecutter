# ADR-004: Keycloak as Identity Provider

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template requires an identity provider (IdP) for OAuth 2.0 / OpenID Connect authentication. Requirements include:

1. **OAuth 2.0 / OIDC Compliance**: Standard protocol support for interoperability
2. **PKCE Support**: Proof Key for Code Exchange for secure public client authentication
3. **Multi-Tenancy**: Custom claims in tokens (specifically `tenant_id`) for tenant identification
4. **Self-Hosted Option**: Ability to run the IdP locally for development and in private infrastructure for production
5. **User Management**: Built-in user registration, password reset, and account management
6. **Role-Based Access Control**: Realm and client roles for authorization
7. **Protocol Mappers**: Custom token claims for application-specific data
8. **JWKS Endpoint**: Public keys for JWT signature validation

The authentication system is critical for security, supporting JWT validation, token revocation, and tenant context extraction.

## Decision

We chose **Keycloak** as the identity provider.

Keycloak is an open-source identity and access management solution developed by Red Hat. Key implementation details:

**Realm Configuration** (`keycloak/setup-realm.sh`):
```bash
# Creates realm with security settings
REALM_JSON='{
    "realm": "{{ cookiecutter.keycloak_realm_name }}",
    "enabled": true,
    "sslRequired": "none",  # Development only
    "bruteForceProtected": true,
    "accessTokenLifespan": 300,
    "ssoSessionIdleTimeout": 1800
}'
```

**Backend Client (Confidential)**:
```json
{
    "clientId": "{{ cookiecutter.keycloak_backend_client_id }}",
    "publicClient": false,
    "standardFlowEnabled": true,
    "serviceAccountsEnabled": true,
    "protocolMappers": [
        {
            "name": "tenant-id",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-usermodel-attribute-mapper",
            "config": {
                "claim.name": "tenant_id",
                "access.token.claim": "true"
            }
        }
    ]
}
```

**Frontend Client (Public with PKCE)**:
```json
{
    "clientId": "{{ cookiecutter.keycloak_frontend_client_id }}",
    "publicClient": true,
    "standardFlowEnabled": true,
    "attributes": {
        "pkce.code.challenge.method": "S256"
    }
}
```

**Backend Integration** (`backend/app/core/config.py`):
```python
OAUTH_ISSUER_URL: str = "http://keycloak:{{ cookiecutter.keycloak_port }}/realms/{{ cookiecutter.keycloak_realm_name }}"
OAUTH_AUDIENCE: str = "{{ cookiecutter.keycloak_backend_client_id }}"
OAUTH_ALGORITHMS: List[str] = ["RS256"]
```

**Frontend Integration** (`frontend/src/auth/config.ts`):
```typescript
export const OIDC_CONFIG = {
  authority: 'http://keycloak.localtest.me:{{ cookiecutter.keycloak_port }}/realms/{{ cookiecutter.keycloak_realm_name }}',
  client_id: '{{ cookiecutter.keycloak_frontend_client_id }}',
  response_type: 'code',
  scope: 'openid profile email',
}
```

## Consequences

### Positive

1. **Full OIDC Compliance**: Implements complete OpenID Connect specification including discovery (`.well-known/openid-configuration`), JWKS endpoints, userinfo, and standard flows

2. **Self-Hosted Control**: Runs in Docker alongside other services. No external dependencies, no vendor lock-in, full control over user data and configuration

3. **Custom Claims via Protocol Mappers**: The `tenant_id` user attribute is mapped to JWT access tokens, enabling the multi-tenant architecture:
   ```json
   {
       "name": "tenant-id",
       "protocolMapper": "oidc-usermodel-attribute-mapper",
       "config": {
           "claim.name": "tenant_id",
           "access.token.claim": "true"
       }
   }
   ```

4. **PKCE Enforcement**: Frontend client is configured with `pkce.code.challenge.method: "S256"`, ensuring authorization code flow uses PKCE

5. **Realm Roles**: Users can be assigned roles (`user`, `admin`, `manager`, etc.) that appear in token claims for RBAC:
   ```python
   if token_payload.realm_access and token_payload.realm_access.roles:
       scopes.extend(token_payload.realm_access.roles)
   ```

6. **Brute Force Protection**: Built-in protection against password guessing attacks complements application-level rate limiting

7. **Admin Console**: Web-based administration for user management, client configuration, and realm settings during development

8. **Audience Mapping**: Custom audience mapper ensures tokens include the backend client ID in the `aud` claim for proper validation

### Negative

1. **Resource Intensive**: Keycloak (Java-based) requires significant memory (~512MB-1GB) compared to lighter alternatives

2. **Configuration Complexity**: Initial setup requires understanding realms, clients, roles, and protocol mappers. The `setup-realm.sh` script mitigates this

3. **Version Upgrades**: Major version upgrades can require database migrations and configuration changes

4. **Admin UI Learning Curve**: The Keycloak admin console has many options; finding specific settings requires familiarity

5. **Startup Time**: Java startup time means Keycloak takes longer to become healthy than other services

### Neutral

1. **Red Hat Backing**: Keycloak is developed by Red Hat and is the upstream for Red Hat SSO. Provides enterprise support option but introduces vendor consideration

2. **Docker Image Size**: The Keycloak image is larger (~400MB) than the application containers

3. **PostgreSQL Dependency**: Keycloak can use its own H2 database for development, but production deployments typically use PostgreSQL (can share the existing database)

## Alternatives Considered

### Auth0

**Why Not Chosen**:
- SaaS-only: Cannot self-host, requires internet connectivity
- Pricing: Free tier has limitations; costs scale with active users
- Data Sovereignty: User data stored in Auth0's infrastructure
- Custom Claims: Requires Auth0 Actions/Rules, more complex than Keycloak protocol mappers
- Vendor Lock-in: Migration requires significant effort

**When Auth0 Would Be Better**: Teams wanting managed infrastructure without operational burden, or needing advanced features like passwordless, MFA, or social login without configuration effort

### Okta

**Why Not Chosen**:
- Similar SaaS concerns as Auth0
- Higher pricing tier for self-hosted (Okta Advanced Server Access)
- More enterprise-focused with corresponding complexity
- Custom claims require Okta Expression Language

### Custom Implementation (JWT Signing)

**Why Not Chosen**:
- Security Risk: Building authentication is notoriously error-prone
- Feature Gap: Would need to implement user management, password reset, session management, JWKS rotation
- Maintenance Burden: Ongoing security updates and vulnerability patching
- Compliance: Would need to ensure OAuth 2.0 / OIDC compliance manually

### Authentik

**Why Not Chosen**:
- Smaller community and ecosystem than Keycloak
- Less mature protocol mapper system
- Fewer enterprise deployments and battle-testing
- Django-based (Python) but less documentation for customization

### Ory (Hydra + Kratos)

**Why Not Chosen**:
- Split architecture (Hydra for OAuth, Kratos for users) adds complexity
- Requires more configuration for equivalent functionality
- Smaller community than Keycloak
- Cloud offering (Ory Network) has similar SaaS concerns

---

## Related ADRs

- [ADR-001: FastAPI as Backend Framework](./001-fastapi-backend-framework.md) - Backend JWT validation
- [ADR-002: Lit as Frontend Framework](./002-lit-frontend-framework.md) - Frontend OIDC client
- [ADR-005: Row-Level Security for Multi-Tenancy](./005-row-level-security-multitenancy.md) - Uses tenant_id from Keycloak tokens
- [ADR-013: PKCE Enforcement for Public Clients](./013-pkce-enforcement-public-clients.md) - Keycloak client configuration

## Implementation References

- `keycloak/setup-realm.sh` - Realm and client configuration script
- `backend/app/services/jwks_client.py` - JWKS fetching from Keycloak
- `backend/app/services/oauth_client.py` - OAuth client for authorization code flow
- `backend/app/api/dependencies/auth.py` - JWT validation using Keycloak public keys
- `frontend/src/auth/` - Frontend OIDC integration with Keycloak
