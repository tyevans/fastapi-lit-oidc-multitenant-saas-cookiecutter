# TASK-09: Keycloak Realm Script Updates

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-09 |
| Title | Keycloak Realm Script Updates |
| Domain | DevOps |
| Complexity | M (Medium) |
| Estimated Effort | 3-4 hours |
| Dependencies | TASK-04 |
| Blocks | TASK-13 |

---

## Scope

### What This Task Includes

1. Add realm role creation for Playwright test users
2. Add test user creation for all 6 Playwright users
3. Assign roles to test users
4. Set tenant_id attributes for multi-tenancy
5. Ensure script is idempotent (can run multiple times)
6. Preserve existing tenant-based users (alice, bob, charlie, diana)

### What This Task Excludes

- Test user module (TASK-04 - defines what users to create)
- Backend changes (TASK-06)
- Playwright test infrastructure (TASK-01 through TASK-08)

---

## Relevant Code Areas

### Files to Modify

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/keycloak/setup-realm.sh` | Add test users and roles |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/keycloak/setup-realm.sh` | Current script structure |
| TASK-04 test-users.ts | Source of truth for user definitions |

---

## Implementation Details

### Current Script Analysis

The existing `setup-realm.sh` script:
- Creates the realm
- Creates backend and frontend OAuth clients
- Creates 4 tenant-based users (alice, bob, charlie, diana)
- Does NOT create role-based test users
- Does NOT create realm roles (user, admin, readonly, manager, service)

### Roles to Create

| Role Name | Description |
|-----------|-------------|
| `user` | Standard user access (base role for most users) |
| `admin` | Administrative access to admin-only endpoints |
| `readonly` | Read-only access to resources |
| `manager` | Manager-level elevated permissions |
| `service` | Service account role for API-to-API integration |

### Users to Create

| Username | Password | Email | Roles | Tenant ID |
|----------|----------|-------|-------|-----------|
| admin | admin123 | admin@example.com | user, admin | tenant-1 |
| testuser | test123 | test@example.com | user | tenant-1 |
| readonly | readonly123 | readonly@example.com | user, readonly | tenant-1 |
| newuser | newuser123 | newuser@example.com | user | tenant-1 |
| manager | manager123 | manager@example.com | user, manager | tenant-1 |
| service-account | service123 | service@example.com | service | tenant-1 |

### Script Additions

Add the following after the existing user creation section:

```bash
# ============================================
# Playwright Test Roles and Users
# ============================================

echo -e "${YELLOW}Creating Playwright test roles...${NC}"

# Function to create a realm role if it doesn't exist
create_role_if_not_exists() {
    local ROLE_NAME=$1
    local DESCRIPTION=$2

    # Check if role exists
    ROLE_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/roles/$ROLE_NAME")

    if [ "$ROLE_CHECK" == "404" ]; then
        echo "  Creating role: $ROLE_NAME"
        curl -s -X POST \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"name\": \"$ROLE_NAME\", \"description\": \"$DESCRIPTION\"}" \
            "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/roles"
    else
        echo "  Role already exists: $ROLE_NAME"
    fi
}

# Create realm roles for Playwright tests
create_role_if_not_exists "user" "Standard user access"
create_role_if_not_exists "admin" "Administrative access"
create_role_if_not_exists "readonly" "Read-only access"
create_role_if_not_exists "manager" "Manager-level permissions"
create_role_if_not_exists "service" "Service account role"

echo -e "${GREEN}Playwright test roles created${NC}"

# ============================================
# Playwright Test Users
# ============================================

echo -e "${YELLOW}Creating Playwright test users...${NC}"

# Function to create a test user with roles
create_playwright_user() {
    local USERNAME=$1
    local PASSWORD=$2
    local EMAIL=$3
    local FIRST_NAME=$4
    local LAST_NAME=$5
    shift 5
    local ROLES=("$@")

    # Check if user exists
    USER_EXISTS=$(curl -s \
        -H "Authorization: Bearer $TOKEN" \
        "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/users?username=$USERNAME&exact=true" | \
        grep -c '"id"')

    if [ "$USER_EXISTS" -eq 0 ]; then
        echo "  Creating user: $USERNAME"

        # Create user
        curl -s -X POST \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "{
                \"username\": \"$USERNAME\",
                \"email\": \"$EMAIL\",
                \"firstName\": \"$FIRST_NAME\",
                \"lastName\": \"$LAST_NAME\",
                \"enabled\": true,
                \"emailVerified\": true,
                \"credentials\": [{
                    \"type\": \"password\",
                    \"value\": \"$PASSWORD\",
                    \"temporary\": false
                }],
                \"attributes\": {
                    \"tenant_id\": [\"tenant-1\"]
                }
            }" \
            "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/users"
    else
        echo "  User already exists: $USERNAME"
    fi

    # Get user ID
    USER_ID=$(curl -s \
        -H "Authorization: Bearer $TOKEN" \
        "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/users?username=$USERNAME&exact=true" | \
        grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -n "$USER_ID" ]; then
        # Build role array for assignment
        ROLE_ARRAY="["
        FIRST=true
        for ROLE in "${ROLES[@]}"; do
            # Get role representation
            ROLE_JSON=$(curl -s \
                -H "Authorization: Bearer $TOKEN" \
                "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/roles/$ROLE")

            ROLE_ID=$(echo "$ROLE_JSON" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
            ROLE_NAME=$(echo "$ROLE_JSON" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)

            if [ -n "$ROLE_ID" ]; then
                if [ "$FIRST" = true ]; then
                    FIRST=false
                else
                    ROLE_ARRAY="$ROLE_ARRAY,"
                fi
                ROLE_ARRAY="$ROLE_ARRAY{\"id\":\"$ROLE_ID\",\"name\":\"$ROLE_NAME\"}"
            fi
        done
        ROLE_ARRAY="$ROLE_ARRAY]"

        # Assign roles
        echo "    Assigning roles: ${ROLES[*]}"
        curl -s -X POST \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$ROLE_ARRAY" \
            "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/users/$USER_ID/role-mappings/realm"
    fi
}

# Create Playwright test users
create_playwright_user "admin" "admin123" "admin@example.com" "Admin" "User" "user" "admin"
create_playwright_user "testuser" "test123" "test@example.com" "Test" "User" "user"
create_playwright_user "readonly" "readonly123" "readonly@example.com" "Readonly" "User" "user" "readonly"
create_playwright_user "newuser" "newuser123" "newuser@example.com" "New" "User" "user"
create_playwright_user "manager" "manager123" "manager@example.com" "Manager" "User" "user" "manager"
create_playwright_user "service-account" "service123" "service@example.com" "Service" "Account" "service"

echo -e "${GREEN}Playwright test users created${NC}"

echo ""
echo -e "${GREEN}=== Playwright Test Setup Complete ===${NC}"
echo "Test users created with credentials:"
echo "  - admin / admin123 (roles: user, admin)"
echo "  - testuser / test123 (roles: user)"
echo "  - readonly / readonly123 (roles: user, readonly)"
echo "  - newuser / newuser123 (roles: user)"
echo "  - manager / manager123 (roles: user, manager)"
echo "  - service-account / service123 (roles: service)"
echo ""
```

---

## Sync with TASK-04

The users created MUST match the definitions in `test-users.ts`:

| Key in test-users.ts | Username in Keycloak | Sync Status |
|---------------------|---------------------|-------------|
| admin | admin | Must Match |
| user | testuser | Must Match |
| readOnly | readonly | Must Match |
| newUser | newuser | Must Match |
| manager | manager | Must Match |
| serviceAccount | service-account | Must Match |

---

## Success Criteria

1. **Roles Created**: All 5 roles exist in Keycloak
2. **Users Created**: All 6 users exist with correct credentials
3. **Role Assignments**: Users have correct role combinations
4. **Tenant ID**: All users have tenant_id attribute set
5. **Idempotent**: Script can run multiple times without errors
6. **Existing Users Preserved**: alice, bob, charlie, diana still exist

---

## Verification Steps

```bash
# Start Keycloak
docker compose up -d keycloak postgres

# Wait for Keycloak to be ready
./keycloak/wait-for-keycloak.sh

# Run setup script
./keycloak/setup-realm.sh

# Verify roles exist
curl -s -X GET \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/admin/realms/{{ cookiecutter.keycloak_realm_name }}/roles" | jq '.[] | .name'

# Verify users exist
curl -s -X GET \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/admin/realms/{{ cookiecutter.keycloak_realm_name }}/users" | jq '.[] | .username'

# Test authentication for each user
for USER in admin testuser readonly newuser manager service-account; do
  PASSWORD="${USER}123"
  [ "$USER" = "testuser" ] && PASSWORD="test123"
  [ "$USER" = "service-account" ] && PASSWORD="service123"

  TOKEN=$(curl -s -X POST \
    "http://localhost:8080/realms/{{ cookiecutter.keycloak_realm_name }}/protocol/openid-connect/token" \
    -d "client_id={{ cookiecutter.keycloak_backend_client_id }}" \
    -d "client_secret={{ cookiecutter.keycloak_backend_client_id }}-secret" \
    -d "username=$USER" \
    -d "password=$PASSWORD" \
    -d "grant_type=password" | jq -r '.access_token')

  if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "OK: $USER authenticated successfully"
  else
    echo "FAIL: $USER authentication failed"
  fi
done
```

---

## Integration Points

### Upstream Dependencies

- **TASK-04**: Defines which users to create (source of truth)

### Downstream Dependencies

This task enables:
- **TASK-13**: Validation requires users to exist in Keycloak

### Contracts

**Data Contract:**
The script MUST create users that match TASK-04 definitions exactly:
- Usernames must match
- Passwords must match
- Roles must match

---

## Monitoring and Observability

The script outputs colored status messages:
- GREEN: Success
- YELLOW: In progress
- RED: Error

---

## Infrastructure Needs

Requires:
- Running Keycloak instance
- Running PostgreSQL (Keycloak database)
- Admin credentials for Keycloak

---

## Notes

1. **Idempotency**: The script checks if roles/users exist before creating them. Running multiple times is safe.

2. **Tenant ID**: All Playwright test users use `tenant-1` for simplicity. This differs from the existing users (alice, bob use UUID-based tenant IDs).

3. **Existing Users**: The script adds to, not replaces, existing users. alice, bob, charlie, diana will still work.

4. **Role Hierarchy**: The `user` role is a base role. All users except `service-account` have it.

5. **Service Account**: Intentionally does NOT have the `user` role to enable testing service-level authentication patterns.

---

## FRD References

- FR-6.1: Realm Setup Script Updates
- FR-6.2: Realm Role Creation
- IP-5: Phase 5 - Keycloak Integration
- DM-4: Keycloak Realm Schema Changes
- TA-5: Test User Management

---

*Task Created: 2025-12-04*
*Status: Not Started*
