# ADR-014: Rate Limiting Strategy

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template exposes OAuth and API endpoints that are susceptible to abuse:

1. **Brute Force Attacks**: Attackers may attempt to guess tokens or credentials via rapid requests
2. **Denial of Service**: Excessive requests can overwhelm backend resources
3. **Token Enumeration**: Attackers may probe for valid tokens via timing analysis
4. **Resource Exhaustion**: Unbounded request rates can exhaust database connections and Redis operations

The rate limiting solution must:
- Work across multiple backend instances (distributed)
- Distinguish between general requests and failed authentication attempts
- Provide meaningful feedback to legitimate users when limits are hit
- Gracefully degrade if the rate limiting infrastructure fails

## Decision

We implement **Redis-based rate limiting** with a sliding window algorithm and dual limits for authentication endpoints.

**Rate Limiter Implementation** (`backend/app/core/rate_limit.py`):
```python
class RateLimiter:
    """
    Distributed rate limiter using Redis with sliding window algorithm.

    Implements two tiers of rate limiting:
    - General authentication: Limits all auth requests per IP
    - Failed authentication: Stricter limit for failed auth attempts
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        general_limit: int = 100,      # Max requests per window
        failed_limit: int = 10,         # Max failed auth per window
        window_seconds: int = 60,       # Time window (1 minute)
        enabled: bool = True,
    ):
        ...

    async def check_rate_limit(self, identifier: str, is_failed_auth: bool = False) -> None:
        """
        Check if request is within rate limits.

        Uses sliding window algorithm:
        1. Calculate current window start time
        2. Build Redis key: rate_limit:{type}:{identifier}:{window_start}
        3. Increment counter and get current count
        4. Set TTL on first request in window
        5. Check if count exceeds limit
        """
        limit_type = "failed_auth" if is_failed_auth else "auth"
        limit = self.failed_limit if is_failed_auth else self.general_limit

        # Calculate window start (aligned to window_seconds boundary)
        current_time = int(time.time())
        window_start = current_time - (current_time % self.window_seconds)

        # Redis key: rate_limit:{type}:{identifier}:{window_start}
        redis_key = f"rate_limit:{limit_type}:{identifier}:{window_start}"

        count = await self.redis_client.incr(redis_key)
        if count == 1:
            await self.redis_client.expire(redis_key, self.window_seconds * 2)

        if count > limit:
            retry_after = (window_start + self.window_seconds) - current_time
            raise RateLimitExceeded(retry_after=retry_after, limit_type=limit_type)
```

**Configuration** (`backend/app/core/config.py`):
```python
# Rate Limiting Configuration
RATE_LIMIT_ENABLED: bool = True                    # Enable/disable rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100          # General auth request limit
RATE_LIMIT_FAILED_AUTH_PER_MINUTE: int = 10        # Failed auth attempt limit
RATE_LIMIT_WINDOW_SECONDS: int = 60                # Time window for rate limiting
```

**Integration with Authentication** (`backend/app/api/dependencies/auth.py`):
```python
async def get_current_user(
    request: Request,
    credentials: ...,
    rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
    ...
) -> AuthenticatedUser:
    client_ip = request.client.host if request.client else "unknown"

    # Check general auth rate limit
    try:
        await rate_limiter.check_rate_limit(client_ip, is_failed_auth=False)
    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limit_exceeded", ...},
            headers={"Retry-After": str(e.retry_after)},
        )

    # After validation failure, track failed auth attempt
    try:
        await rate_limiter.check_rate_limit(client_ip, is_failed_auth=True)
    except RateLimitExceeded:
        # Stricter limit for repeated failures
        raise HTTPException(status_code=429, ...)
```

## Consequences

### Positive

1. **Dual-Tier Protection**: Two separate limits provide defense against different attack patterns:
   ```
   General limit (100/min): Prevents DoS by limiting total request volume
   Failed auth limit (10/min): Prevents brute force by limiting invalid attempts
   ```

2. **Distributed State**: Redis enables consistent rate limiting across multiple backend instances:
   ```python
   # Backend 1: Client makes 50 requests
   redis: rate_limit:auth:192.168.1.100:1733400000 = 50

   # Backend 2: Same client makes 60 more requests
   redis: rate_limit:auth:192.168.1.100:1733400000 = 110  # Exceeds limit
   ```

3. **Sliding Window Accuracy**: Window-aligned keys provide accurate rate limiting without complex data structures:
   ```python
   # Time-aligned windows prevent gaming the system
   window_start = current_time - (current_time % window_seconds)
   # All requests within same 60-second window use same key
   ```

4. **Automatic Cleanup**: Redis TTL ensures rate limit keys expire automatically:
   ```python
   await self.redis_client.expire(redis_key, self.window_seconds * 2)  # 2x for edge cases
   ```

5. **Graceful Degradation**: If Redis is unavailable, rate limiting is skipped (fail-open for availability):
   ```python
   except redis.RedisError as e:
       logger.warning("Redis error during rate limit check - allowing request")
       return  # Allow request to proceed
   ```

6. **Retry-After Header**: HTTP 429 responses include `Retry-After` header for client feedback:
   ```python
   headers={"Retry-After": str(e.retry_after)}
   # Client knows exactly when to retry
   ```

7. **Per-IP Tracking**: Rate limits by client IP, preventing a single source from consuming all capacity

### Negative

1. **IP-Based Limitations**:
   - **NAT/Proxy Issues**: Users behind shared IP (corporate NAT, VPN) share rate limits
   - **IPv6 Subnets**: May need /64 aggregation for IPv6
   - **IP Spoofing**: Doesn't prevent attacks from distributed botnets

2. **Redis Dependency**: Rate limiting adds Redis dependency to auth flow:
   - Redis failure impacts rate limiting (falls back to no limiting)
   - Adds latency (~0.1-0.5ms) per request for Redis operations

3. **No Per-Tenant Limits**: Current implementation is global per-IP, not per-tenant:
   ```python
   # All tenants share the same IP rate limit
   # A tenant's legitimate high-volume user could be limited
   ```

4. **Fixed Window Granularity**: 60-second windows may allow burst at window boundaries:
   ```
   Window 1: 100 requests at t=59
   Window 2: 100 requests at t=61
   # 200 requests in 2 seconds (edge case)
   ```

5. **Configuration Requires Restart**: Changing limits requires application restart (loaded from settings at startup)

### Neutral

1. **Default Limits**: 100 requests/minute for general, 10 for failed auth. May need tuning based on actual usage patterns

2. **Fail-Open vs Fail-Closed**: We chose fail-open (allow requests if Redis fails) to prioritize availability. For higher security environments, fail-closed may be preferred

## Alternatives Considered

### In-Memory Rate Limiting

**Approach**: Use local memory (dict with TTL) for rate limiting.

**Why Not Chosen**:
- **Not Distributed**: Each backend instance has separate limits
- **Load Balancer Gaming**: Attacker can hit different instances to bypass limits
- **Memory Growth**: Long-running process accumulates rate limit entries

### Token Bucket Algorithm

**Approach**: Implement token bucket for smoother rate limiting.

**Why Not Chosen**:
- **Complexity**: Requires tracking bucket state per client
- **Storage Overhead**: More data to store in Redis per client
- **Overkill**: Sliding window sufficient for authentication protection

### nginx/HAProxy Rate Limiting

**Approach**: Implement rate limiting at reverse proxy layer.

**Why Not Chosen**:
- **Limited Context**: Proxy doesn't know if auth succeeded or failed
- **No Dual-Tier**: Can't differentiate general vs failed auth limits
- **Deployment Coupling**: Rate limit config tied to infrastructure

### Per-User Rate Limiting

**Approach**: Rate limit by authenticated user ID instead of IP.

**Why Not Chosen**:
- **Chicken-and-Egg**: Can't know user ID before authentication
- **Unauthenticated Attacks**: Brute force attacks are from unauthenticated clients
- **Complementary**: Could add per-user limits for authenticated endpoints

### Distributed Rate Limiting Service

**Approach**: Use dedicated service like Envoy Rate Limit Service.

**Why Not Chosen**:
- **Complexity**: Additional service to deploy and manage
- **Latency**: External service call adds latency
- **Overkill**: Redis-based solution sufficient for current scale

---

## Related ADRs

- [ADR-007: Redis Token Revocation Strategy](./007-redis-token-revocation.md) - Shared Redis infrastructure
- [ADR-001: FastAPI as Backend Framework](./001-fastapi-backend-framework.md) - Dependency injection for rate limiter

## Implementation References

- `backend/app/core/rate_limit.py` - RateLimiter class and RateLimitExceeded exception
- `backend/app/api/dependencies/auth.py` - Rate limit integration in authentication
- `backend/app/core/config.py` - Rate limit configuration settings
- `backend/app/core/cache.py` - Redis client configuration
