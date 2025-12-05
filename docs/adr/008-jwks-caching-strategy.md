# ADR-008: JWKS Caching Strategy

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template uses JWT tokens for API authentication. JWT signature validation requires fetching the OAuth provider's public keys from their JWKS (JSON Web Key Set) endpoint. Key challenges include:

1. **Performance**: Fetching JWKS for every request adds significant latency (10-50ms HTTP call per request)
2. **Availability**: JWKS endpoint availability affects all authentication operations
3. **Key Rotation**: OAuth providers periodically rotate signing keys; the system must handle this gracefully
4. **Multi-Tenancy**: Different tenants could theoretically use different OAuth providers (multi-issuer support)
5. **Scalability**: With multiple backend instances, JWKS should be cached centrally to avoid redundant fetches

The backend validates JWT tokens via Keycloak's JWKS endpoint at `{issuer_url}/.well-known/openid-configuration` -> `jwks_uri`.

## Decision

We implement a **Redis-backed JWKS caching strategy** with OIDC discovery and automatic key rotation support.

**Implementation** (`backend/app/services/jwks_client.py`):

```python
class JWKSClient:
    """Async JWKS client with Redis caching."""

    def __init__(
        self,
        redis_client: redis.Redis,
        cache_ttl: int = 3600,  # 1 hour default
        http_timeout: int = 10,
    ):
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl
        self._http_client = httpx.AsyncClient(timeout=http_timeout)
```

**Caching Strategy**:

1. **Redis as Central Cache**: JWKS stored in Redis with key pattern `jwks:{issuer_url}`
2. **TTL-Based Expiration**: Default 1-hour TTL (`JWKS_CACHE_TTL` setting)
3. **Force Refresh**: `force_refresh=True` bypasses cache for key rotation scenarios

**OIDC Discovery Flow**:
```python
async def _fetch_jwks(self, issuer_url: str) -> Dict[str, Any]:
    # 1. Fetch OIDC discovery document
    discovery_url = f"{issuer_url}/.well-known/openid-configuration"
    discovery_response = await self._http_client.get(discovery_url)
    jwks_uri = discovery_response.json().get("jwks_uri")

    # 2. Fetch JWKS from discovered endpoint
    jwks_response = await self._http_client.get(jwks_uri)
    return jwks_response.json()
```

**Key Rotation Handling** (`backend/app/api/dependencies/auth.py`):
```python
# First attempt with cached JWKS
signing_key = await jwks_client.get_signing_key(issuer_url, key_id, force_refresh=False)

if signing_key is None:
    # Key not found - trigger refresh (handles key rotation)
    signing_key = await jwks_client.get_signing_key(issuer_url, key_id, force_refresh=True)
```

**Graceful Degradation**:
```python
async def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
    try:
        cached_data = await self.redis_client.get(cache_key)
        return json.loads(cached_data) if cached_data else None
    except redis.RedisError:
        return None  # Fail gracefully, fetch from provider
```

## Consequences

### Positive

1. **Performance**: Cache hit eliminates 10-50ms HTTP call; Redis lookup is ~0.1ms
2. **Reduced Provider Load**: JWKS fetched once per hour instead of per-request
3. **Shared Across Instances**: All backend instances share the same cached JWKS
4. **Automatic Key Rotation**: Unknown `kid` triggers cache refresh, picking up new keys
5. **Multi-Issuer Support**: Each issuer URL gets its own cache entry (`jwks:{issuer_url}`)
6. **Redis Failure Tolerance**: Falls back to direct provider fetch if Redis unavailable

### Negative

1. **Key Rotation Delay**: Up to 1 hour before new keys are picked up (mitigated by force refresh on unknown kid)
2. **Redis Dependency**: Adds Redis as an infrastructure dependency (though fails gracefully)
3. **Stale Key Risk**: If a key is compromised and rotated, tokens signed with old key could validate for up to 1 hour

### Neutral

1. **TTL Tradeoff**: Shorter TTL = fresher keys but more provider requests; 1 hour is a reasonable balance
2. **Discovery Overhead**: OIDC discovery adds one extra HTTP call per cache miss (but enables dynamic endpoint configuration)

## Alternatives Considered

### In-Memory Caching (No Redis)

**Approach**: Cache JWKS in application memory using Python dict or LRU cache.

**Why Not Chosen**:
- Each backend instance maintains separate cache
- Key rotation not synchronized across instances
- Memory usage grows with multiple issuers
- Cache lost on process restart

### No Caching (Direct Fetch)

**Approach**: Fetch JWKS from provider for every token validation.

**Why Not Chosen**:
- 10-50ms latency added to every authenticated request
- Creates single point of failure (provider availability)
- Excessive load on OAuth provider
- Not scalable for high-traffic applications

### Longer TTL (24 hours)

**Approach**: Cache JWKS for 24 hours to minimize provider requests.

**Why Not Chosen**:
- Key compromise scenarios require faster rotation
- OAuth providers typically recommend 1-hour or less
- Risk outweighs performance benefit

### Pre-Fetching on Startup

**Approach**: Fetch and cache JWKS at application startup.

**Why Not Chosen**:
- Delays startup if provider unavailable
- Still need refresh mechanism for key rotation
- Current lazy-loading approach works well with force_refresh

---

## Related ADRs

- [ADR-004: Keycloak as Identity Provider](./004-keycloak-identity-provider.md) - JWKS source
- [ADR-007: Redis Token Revocation](./007-redis-token-revocation.md) - Same Redis instance used

## Implementation References

- `backend/app/services/jwks_client.py` - JWKSClient class with Redis caching
- `backend/app/api/dependencies/auth.py` - JWKS usage in token validation
- `backend/app/core/config.py` - `JWKS_CACHE_TTL`, `JWKS_HTTP_TIMEOUT` settings
- `backend/tests/unit/test_jwks_client.py` - Comprehensive caching tests
