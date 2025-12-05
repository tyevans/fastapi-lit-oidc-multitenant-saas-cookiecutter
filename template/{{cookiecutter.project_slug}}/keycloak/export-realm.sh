#!/bin/bash
set -e

# Keycloak Realm Export Script
# Exports the {{ cookiecutter.keycloak_realm_name }} realm with clients and configuration

KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost:{{ cookiecutter.keycloak_port }}}"
ADMIN_USER="${KEYCLOAK_ADMIN:-{{ cookiecutter.keycloak_admin }}}"
ADMIN_PASS="${KEYCLOAK_ADMIN_PASSWORD:-{{ cookiecutter.keycloak_admin_password }}}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=== Keycloak Realm Export ==="
echo "Getting admin token..."

# Get admin token
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -d "client_id=admin-cli" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Failed to get admin token"
    exit 1
fi

echo "Exporting realm {{ cookiecutter.keycloak_realm_name }} (partial export with clients and users)..."

# Use partial export endpoint to include clients and users
curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/partial-export?exportClients=true&exportGroupsAndRoles=true" \
    | jq '.' > "$SCRIPT_DIR/realm-export.json"

if [ $? -eq 0 ]; then
    echo "✓ Realm exported to keycloak/realm-export.json"
    echo ""
    echo "Export includes:"
    jq -r '{realm: .realm, clients: [.clients // [] | .[] | .clientId], usersCount: (.users // [] | length)}' "$SCRIPT_DIR/realm-export.json"
else
    echo "✗ Export failed"
    exit 1
fi
