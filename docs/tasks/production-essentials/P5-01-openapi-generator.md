# P5-01: Configure OpenAPI Generator for TypeScript

## Task Identifier
**ID:** P5-01
**Phase:** 5 - Developer Experience
**Domain:** Frontend
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| None | - | - | Can be developed independently |

## Scope

### In Scope
- Configure OpenAPI Generator CLI for TypeScript client generation
- Create `openapitools.json` configuration file
- Create npm scripts for client generation
- Create generation script with validation
- Document the generated client integration pattern
- Add TypeScript client generation to CI workflow (optional enhancement)
- Create `.openapi-generator-ignore` for customization
- Update frontend package.json with generator dependencies

### Out of Scope
- Modifying existing hand-written API client (`frontend/src/api/client.ts`)
- Breaking change detection in CI (documented as future enhancement)
- Automatic regeneration on backend changes (webhook pattern)
- Publishing generated client to npm registry

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/frontend/
  openapitools.json                    # OpenAPI Generator configuration
  .openapi-generator-ignore            # Files to preserve during generation
  src/api/generated/                   # Directory for generated client (gitignored initially)

template/{{cookiecutter.project_slug}}/scripts/
  generate-api-client.sh               # Generation script
```

### Files to Modify
```
template/{{cookiecutter.project_slug}}/frontend/package.json    # Add generator scripts and deps
template/{{cookiecutter.project_slug}}/frontend/.gitignore      # Ignore generated directory (optional)
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/backend/app/main.py             # OpenAPI schema source
template/{{cookiecutter.project_slug}}/frontend/src/api/client.ts      # Existing client pattern
template/{{cookiecutter.project_slug}}/frontend/src/api/types.ts       # Existing type definitions
```

## Implementation Details

### 1. OpenAPI Generator Configuration (`frontend/openapitools.json`)

```json
{
  "$schema": "node_modules/@openapitools/openapi-generator-cli/config.schema.json",
  "spaces": 2,
  "generator-cli": {
    "version": "7.2.0",
    "generators": {
      "typescript-fetch": {
        "generatorName": "typescript-fetch",
        "output": "#{cwd}/src/api/generated",
        "inputSpec": "#{cwd}/../backend/openapi.json",
        "additionalProperties": {
          "supportsES6": true,
          "typescriptThreePlus": true,
          "withInterfaces": true,
          "useSingleRequestParameter": true,
          "prefixParameterInterfaces": true,
          "npmName": "{{ cookiecutter.project_slug }}-api-client",
          "npmVersion": "0.0.1",
          "enumPropertyNaming": "original"
        },
        "globalProperty": {
          "apis": "",
          "models": "",
          "supportingFiles": "runtime.ts,index.ts"
        }
      }
    }
  }
}
```

### 2. Generator Ignore File (`frontend/.openapi-generator-ignore`)

```
# OpenAPI Generator Ignore
# Use this file to prevent regeneration of specific files

# Preserve custom configuration
.openapi-generator-ignore

# Preserve README customizations
README.md

# Preserve custom runtime modifications (if any)
# src/api/generated/runtime.ts
```

### 3. Generation Script (`scripts/generate-api-client.sh`)

```bash
#!/bin/bash
set -euo pipefail

# {{ cookiecutter.project_name }} - OpenAPI Client Generator
#
# Generates TypeScript API client from backend OpenAPI schema.
#
# Usage:
#   ./scripts/generate-api-client.sh [options]
#
# Options:
#   --from-url    Fetch OpenAPI spec from running backend (default)
#   --from-file   Use local openapi.json file
#   --validate    Validate spec only, don't generate
#   --dry-run     Show what would be generated
#
# Prerequisites:
#   - Node.js 18+ (for openapi-generator-cli)
#   - Java 11+ (for generator execution)
#   - Backend running (for --from-url)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_URL="${BACKEND_URL:-http://localhost:{{ cookiecutter.backend_port }}}"
OPENAPI_SPEC_PATH="$PROJECT_ROOT/backend/openapi.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
FROM_URL=true
VALIDATE_ONLY=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --from-file)
            FROM_URL=false
            shift
            ;;
        --from-url)
            FROM_URL=true
            shift
            ;;
        --validate)
            VALIDATE_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}=== OpenAPI TypeScript Client Generator ===${NC}"

# Step 1: Get OpenAPI spec
if [ "$FROM_URL" = true ]; then
    echo -e "${YELLOW}Fetching OpenAPI spec from $BACKEND_URL...${NC}"

    # Check if backend is running
    if ! curl -s "$BACKEND_URL{{ cookiecutter.backend_api_prefix }}/health" > /dev/null 2>&1; then
        echo -e "${RED}Error: Backend is not running at $BACKEND_URL${NC}"
        echo "Start the backend with: ./scripts/docker-dev.sh up"
        exit 1
    fi

    # Fetch OpenAPI spec
    curl -s "$BACKEND_URL/openapi.json" > "$OPENAPI_SPEC_PATH"
    echo -e "${GREEN}OpenAPI spec saved to $OPENAPI_SPEC_PATH${NC}"
else
    if [ ! -f "$OPENAPI_SPEC_PATH" ]; then
        echo -e "${RED}Error: OpenAPI spec not found at $OPENAPI_SPEC_PATH${NC}"
        echo "Run with --from-url to fetch from running backend"
        exit 1
    fi
    echo -e "${YELLOW}Using existing OpenAPI spec: $OPENAPI_SPEC_PATH${NC}"
fi

# Step 2: Validate spec
echo -e "${YELLOW}Validating OpenAPI spec...${NC}"
cd "$FRONTEND_DIR"

if ! npx @openapitools/openapi-generator-cli validate -i "$OPENAPI_SPEC_PATH"; then
    echo -e "${RED}OpenAPI spec validation failed${NC}"
    exit 1
fi
echo -e "${GREEN}OpenAPI spec is valid${NC}"

if [ "$VALIDATE_ONLY" = true ]; then
    echo -e "${GREEN}Validation complete. Exiting.${NC}"
    exit 0
fi

# Step 3: Generate client
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}Dry run - would generate client to: $FRONTEND_DIR/src/api/generated/${NC}"
    exit 0
fi

echo -e "${YELLOW}Generating TypeScript client...${NC}"

# Clear previous generation (except ignored files)
if [ -d "src/api/generated" ]; then
    echo "Cleaning previous generated files..."
    rm -rf src/api/generated/apis src/api/generated/models 2>/dev/null || true
fi

# Run generator
npx @openapitools/openapi-generator-cli generate \
    --config openapitools.json \
    --generator-key typescript-fetch

# Step 4: Post-processing
echo -e "${YELLOW}Post-processing generated code...${NC}"

# Fix imports if needed (optional)
# sed -i '' 's/from '\''\.\.\/runtime'\''/from '\''\.\/runtime'\''/' src/api/generated/apis/*.ts 2>/dev/null || true

# Format generated code
echo "Formatting generated code..."
npx prettier --write src/api/generated/ 2>/dev/null || true

# Step 5: Summary
echo -e "${GREEN}=== Generation Complete ===${NC}"
echo ""
echo "Generated files:"
find src/api/generated -type f -name "*.ts" | head -20
TOTAL_FILES=$(find src/api/generated -type f -name "*.ts" | wc -l | tr -d ' ')
echo ""
echo -e "${GREEN}Total: $TOTAL_FILES TypeScript files generated${NC}"
echo ""
echo "Usage example:"
echo "  import { DefaultApi, Configuration } from './api/generated'"
echo "  const api = new DefaultApi(new Configuration({ basePath: '$BACKEND_URL' }))"
echo "  const response = await api.healthCheck()"
```

### 4. Package.json Updates

Add to `frontend/package.json`:

```json
{
  "scripts": {
    "generate:api": "npx @openapitools/openapi-generator-cli generate --config openapitools.json --generator-key typescript-fetch",
    "generate:api:validate": "npx @openapitools/openapi-generator-cli validate -i ../backend/openapi.json",
    "generate:api:fetch": "../scripts/generate-api-client.sh --from-url"
  },
  "devDependencies": {
    "@openapitools/openapi-generator-cli": "^2.13.4"
  }
}
```

### 5. Integration Pattern Documentation

Create `frontend/src/api/generated/README.md` (preserved during regeneration):

```markdown
# Generated API Client

This directory contains TypeScript API client code auto-generated from the backend OpenAPI specification.

## Regeneration

To regenerate the client after backend API changes:

```bash
# From project root (requires backend running)
./scripts/generate-api-client.sh

# From frontend directory
npm run generate:api:fetch
```

## Usage

### Basic Setup

```typescript
import { Configuration, DefaultApi } from './generated'

const config = new Configuration({
  basePath: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  accessToken: async () => {
    const token = await authService.getAccessToken()
    return token || ''
  }
})

const api = new DefaultApi(config)
```

### With Authentication

The Configuration class supports an `accessToken` callback for automatic authentication:

```typescript
const config = new Configuration({
  basePath: import.meta.env.VITE_API_URL,
  accessToken: async () => {
    const token = await authService.getAccessToken()
    return token || ''
  }
})

// All requests automatically include Authorization header
const user = await api.getMe()
```

### Type-Safe Responses

```typescript
// Types are automatically generated from OpenAPI schemas
import type { HealthCheckResponse, UserResponse } from './generated'

const health: HealthCheckResponse = await api.healthCheck()
const user: UserResponse = await api.getMe()
```

### Error Handling

```typescript
try {
  const result = await api.createResource({ body: data })
} catch (error) {
  if (error instanceof ResponseError) {
    console.error(`API Error: ${error.response.status}`)
    const body = await error.response.json()
    console.error(body.detail)
  }
}
```

## Coexistence with Hand-Written Client

The generated client can coexist with the hand-written `client.ts`:

- **Generated client**: Use for type-safe API calls with full IDE support
- **Hand-written client**: Use for custom logic, error handling patterns

```typescript
// Option 1: Use generated client directly
import { DefaultApi, Configuration } from './generated'
const api = new DefaultApi(config)

// Option 2: Wrap generated client in service layer
import { apiClient } from './client'  // Hand-written
```

## Customization

Files listed in `.openapi-generator-ignore` are preserved during regeneration.

To customize generated code:
1. Add file to `.openapi-generator-ignore`
2. Modify the file as needed
3. Re-run generation (your changes are preserved)

## Troubleshooting

### Backend not running
```
Error: Backend is not running at http://localhost:8000
```
Start backend: `./scripts/docker-dev.sh up`

### Java not found
OpenAPI Generator requires Java 11+:
```bash
# macOS
brew install openjdk@11

# Ubuntu
sudo apt-get install openjdk-11-jdk
```

### Validation errors
```bash
# Validate OpenAPI spec
npm run generate:api:validate
```
```

### 6. Optional: CI Integration

Add to `.github/workflows/ci.yml` (when GitHub Actions enabled):

```yaml
  generate-api-client:
    name: Validate API Client Generation
    runs-on: ubuntu-latest
    needs: [backend-test]  # Ensure backend tests pass first
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Start backend for OpenAPI spec
        run: |
          docker compose up -d backend postgres redis
          sleep 30  # Wait for backend to be ready

      - name: Generate API client
        run: ./scripts/generate-api-client.sh --from-url

      - name: Check for uncommitted changes
        working-directory: frontend
        run: |
          if [ -n "$(git status --porcelain src/api/generated/)" ]; then
            echo "Generated API client has uncommitted changes!"
            echo "Run './scripts/generate-api-client.sh' and commit the changes."
            git diff src/api/generated/
            exit 1
          fi

      - name: Type check generated client
        working-directory: frontend
        run: npx tsc --noEmit
```

## Success Criteria

### Functional Requirements
- [ ] FR-DX-001: OpenAPI Generator configuration exists (`openapitools.json`)
- [ ] Generation script successfully creates TypeScript client
- [ ] Generated client compiles without TypeScript errors
- [ ] Generated client includes all backend API endpoints
- [ ] Generated types match Pydantic schemas from backend

### Verification Steps
1. **Configuration Validation:**
   ```bash
   # Check config exists
   test -f frontend/openapitools.json

   # Validate config schema
   cd frontend && npm run generate:api:validate
   ```

2. **Generation Test:**
   ```bash
   # Start backend
   ./scripts/docker-dev.sh up

   # Generate client
   ./scripts/generate-api-client.sh

   # Verify files generated
   ls frontend/src/api/generated/
   # Should show: apis/, models/, runtime.ts, index.ts
   ```

3. **Type Check:**
   ```bash
   cd frontend
   npx tsc --noEmit
   # Should pass without errors
   ```

4. **Integration Test:**
   ```typescript
   // Verify generated client is importable
   import { DefaultApi, Configuration } from './api/generated'
   const api = new DefaultApi(new Configuration({ basePath: 'http://localhost:8000' }))
   ```

### Quality Gates
- [ ] `openapitools.json` is valid JSON
- [ ] Generator version is pinned (not `latest`)
- [ ] Generated client has no TypeScript errors
- [ ] README documents usage patterns
- [ ] Script has proper error handling
- [ ] `.openapi-generator-ignore` preserves customizations

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| None | - | Independent task |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P5-05 | API client available | Performance baselines may use generated client |
| P6-01 | Generation script documented | CLAUDE.md update includes API client commands |

### Integration Contract
```yaml
# Contract: OpenAPI Generator configuration

# Configuration file
frontend/openapitools.json

# Generated output directory
frontend/src/api/generated/
  index.ts          # Re-exports all APIs and models
  runtime.ts        # Fetch configuration and helpers
  apis/             # API classes by tag
  models/           # TypeScript interfaces from schemas

# Generation command
./scripts/generate-api-client.sh --from-url

# npm scripts
npm run generate:api           # Generate from local spec
npm run generate:api:validate  # Validate spec only
npm run generate:api:fetch     # Fetch spec and generate

# Configuration options
generator: typescript-fetch
supportsES6: true
typescriptThreePlus: true
withInterfaces: true
```

## Monitoring and Observability

### Generation Metrics
- Track generation time in CI
- Monitor for schema validation failures
- Alert on breaking changes (future enhancement)

### Developer Experience
- Provide clear error messages for common issues
- Include troubleshooting section in README
- Log generation summary (files created, endpoint count)

## Infrastructure Needs

### Development Dependencies
- Node.js 18+ (for openapi-generator-cli npm wrapper)
- Java 11+ (OpenAPI Generator runtime)
- Backend running (for spec fetching)

### CI Requirements
- Java installed in CI environment
- Backend service available during generation job
- npm cache for faster builds

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Configuration setup is straightforward
- Script development requires error handling
- Documentation and integration patterns needed
- Testing across different scenarios
- Optional CI integration adds complexity

## Notes

### Design Decisions

**1. typescript-fetch Generator:**
- Native fetch API (no axios dependency)
- Modern TypeScript support
- Matches existing client.ts pattern
- Good tree-shaking support

**2. Separate Generated Directory:**
- Clear separation from hand-written code
- Can be gitignored or committed
- Easy to regenerate without conflicts

**3. Generation Script:**
- Handles spec fetching from running backend
- Validates spec before generation
- Provides clear error messages
- Supports dry-run for testing

**4. Coexistence Pattern:**
- Generated client alongside hand-written
- Developers choose which to use
- Migration path from hand-written to generated

### Alternative Generators Considered

| Generator | Pros | Cons |
|-----------|------|------|
| `typescript-fetch` | Native fetch, lightweight | Less features |
| `typescript-axios` | Feature-rich, interceptors | Axios dependency |
| `typescript-angular` | Angular-specific | Framework-locked |
| `openapi-typescript` | Types only | No runtime client |

### Migration Strategy

For projects with existing hand-written clients:
1. Generate client to `src/api/generated/`
2. Keep hand-written client for custom patterns
3. Gradually migrate endpoints to generated client
4. Eventually deprecate hand-written client

### Related Requirements
- FR-DX-001: OpenAPI Generator configuration for TypeScript
- FR-DX-002: TypeScript client generation in CI (optional)
- US-5.1: Auto-generated TypeScript API clients
