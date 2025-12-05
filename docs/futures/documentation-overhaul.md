# Documentation Overhaul for Project-Starter Template

| Field | Value |
|-------|-------|
| **Title** | Documentation Overhaul |
| **Date Created** | 2025-12-05 |
| **Last Updated** | 2025-12-05 |
| **Author/Agent** | FRD Builder Agent |
| **Status** | Ready for FRD Refiner - All sections complete |

---

## Table of Contents

- [x] [Problem Statement](#problem-statement)
- [x] [Goals & Success Criteria](#goals--success-criteria)
- [x] [Scope & Boundaries](#scope--boundaries)
- [x] [User Stories / Use Cases](#user-stories--use-cases)
- [x] [Functional Requirements](#functional-requirements)
- [x] [Technical Approach](#technical-approach)
- [x] [Architecture & Integration Considerations](#architecture--integration-considerations)
- [x] [Data Models & Schema Changes](#data-models--schema-changes)
- [x] [UI/UX Considerations](#uiux-considerations)
- [x] [Security & Privacy Considerations](#security--privacy-considerations)
- [x] [Testing Strategy](#testing-strategy)
- [x] [Implementation Phases](#implementation-phases)
- [x] [Dependencies & Risks](#dependencies--risks)
- [x] [Open Questions](#open-questions)
- [x] [Status](#status)

---

## Problem Statement

### Current Documentation Landscape

The project-starter cookiecutter template at `/home/ty/workspace/project-starter/` has accumulated documentation across multiple files and locations, resulting in fragmented, overlapping, and partially outdated content. This FRD addresses a comprehensive documentation overhaul across four key areas.

### Documentation Files Inventory

**Root-Level Documentation:**
| File | Lines | Purpose | Issues Identified |
|------|-------|---------|-------------------|
| `README.md` | 497 lines | Main project documentation | Long, covers too many topics, some outdated references |
| `QUICKSTART.md` | 340 lines | Getting started guide | Overlaps significantly with README, Python version mismatch (says 3.8+, should be 3.12+) |
| `TEMPLATE_SUMMARY.md` | 328 lines | Template technical summary | Significant overlap with README and generated project docs |

**Template-Level Documentation (in `template/{{cookiecutter.project_slug}}/`):**
| File | Lines | Purpose |
|------|-------|---------|
| `README.md` | 532 lines | Generated project documentation |
| `CLAUDE.md` | ~200 lines | AI assistant guidance |
| `backend/README.md` | 317 lines | Backend-specific documentation |
| `backend/QUICKSTART.md` | 153 lines | Backend quick start |
| `frontend/README.md` | 328 lines | Frontend documentation |
| `observability/README.md` | 427 lines | Observability stack documentation |
| `playwright/README.md` | 303 lines | API testing documentation |
| `playwright/QUICK_START.md` | (exists) | Testing quick start |

### Issue 1: README Complexity and Organization

**Current Problems:**
1. **Information Overload**: The root README.md (497 lines) tries to serve multiple audiences (template users, generated project developers, contributors) simultaneously
2. **Redundant Structure Diagrams**: Contains both "Cookiecutter Template Structure" and "Generated Project Structure" sections that could be better organized
3. **Feature List Inflation**: Lists 14 features in the "Built-in Features" section without clear hierarchy or grouping
4. **Configuration Sprawl**: Environment variables section mixes essential variables with defaults that rarely need changing
5. **Troubleshooting as Afterthought**: Troubleshooting section is buried at the end rather than linked prominently

**Specific Issues Found:**
- Line 45: References `gh:your-username/your-template-repo` - placeholder not useful
- Line 484: Contains `{{ cookiecutter.license }}` - template variable leaked into template docs
- Quick Start section is 7 steps which could be streamlined
- Development Workflow section could link to component-specific READMEs instead of duplicating

### Issue 2: QUICKSTART.md Redundancy and Inconsistencies

**Current Problems:**
1. **Python Version Mismatch**: States "Python 3.8+" in prerequisites (line 8) when template requires Python 3.12+ (as shown in cookiecutter.json line 58)
2. **Heavy Overlap with README**: Approximately 60% of content duplicates README.md Quick Start and Development Workflow sections
3. **Inconsistent Path References**: Uses `/path/to/project-starter` which differs from README's pattern
4. **Missing Modern Tooling**: Does not mention `uv` package manager which is used in the generated backend

**Specific Issues Found:**
- Line 30: `cookiecutter /path/to/project-starter` should be `cookiecutter /path/to/project-starter/template`
- Lines 155-188: Development workflow section duplicates README entirely
- "Next Steps" section at line 297 is generic and could be more actionable

### Issue 3: TEMPLATE_SUMMARY.md Redundancy Assessment

**Current Problems:**
1. **Unclear Purpose**: Sits between README (user guide) and generated project docs (developer guide) without a clear audience
2. **Massive Overlap**:
   - "What's Included" section duplicates README "Features" section
   - "Template Structure" duplicates README "Cookiecutter Template Structure"
   - "Generated Project Features" duplicates README "Generated Project Structure"
   - "Usage" section duplicates QUICKSTART.md entirely
3. **Maintenance Burden**: Any feature change requires updating 3+ files
4. **Potentially Confusing**: New users may not know which document to read

**Redundancy Analysis:**
| Section in TEMPLATE_SUMMARY.md | Also Found In |
|--------------------------------|---------------|
| Core Technologies | README.md line 5-14 |
| Key Features (1-5) | README.md line 16-28 |
| Template Structure | README.md line 118-134 |
| Template Variables | Partially in cookiecutter.json, README |
| Generated Project Features | README.md line 139-188 |
| Development Workflow | QUICKSTART.md, README.md |
| Production Deployment | README.md |

**Recommendation**: Consider deprecating TEMPLATE_SUMMARY.md and consolidating its unique content into README.md and/or a new `docs/ARCHITECTURE.md`.

### Issue 4: Missing Architecture Decision Records (ADRs)

**Current State:**
The project contains no ADRs despite having made numerous architectural decisions that should be documented for future maintainers and contributors.

**Evidence of Undocumented Decisions:**

1. **Technology Stack Choices**
   - Why FastAPI over Flask/Django?
   - Why Lit over React/Vue/Svelte?
   - Why PostgreSQL with RLS over other multi-tenancy approaches?
   - Why Keycloak over Auth0/Okta/custom OAuth?

2. **Architectural Patterns**
   - Multi-tenancy via Row-Level Security (RLS)
   - Dual database users (migration vs app user)
   - Token revocation via Redis blacklist
   - JWKS caching strategy
   - Cookie-based vs header-based auth token transport

3. **Operational Decisions**
   - Docker Compose as primary development environment
   - Port allocation strategy (5435 for Postgres, 8080 for Keycloak)
   - Observability stack as optional feature
   - `uv` over `pip` for Python package management

4. **Template Design Decisions**
   - Cookiecutter over Copier/Yeoman
   - Include vs exclude patterns for features
   - Default values for template variables
   - File organization within generated projects

5. **Security Decisions**
   - PKCE enforcement for public clients
   - JWT validation approach
   - Rate limiting strategy
   - CORS configuration approach

### Impact of Current State

**For New Template Users:**
- Must read multiple documents to understand the full picture
- May miss important information due to document sprawl
- Confusion about which document is authoritative

**For Template Contributors:**
- Unclear where to document new features
- Risk of introducing inconsistencies across documents
- No record of why decisions were made

**For Generated Project Developers:**
- Better documentation exists in generated projects than in template docs
- Must trace back to template to understand certain choices

### Documentation Debt from Recent Changes

The `docs/todo.txt` file indicates known documentation debt:
```
[] we removed the ability to generate projects without multitenancy or rate limiting, we should make sure we got all the docs cleaned up properly.
[] move to using uv and a pyproject.toml for the backend
```

This confirms that documentation has fallen behind implementation changes.

### Opportunity

A comprehensive documentation overhaul will:
1. **Reduce Cognitive Load**: Single source of truth for each topic
2. **Improve Maintainability**: Fewer files to update when features change
3. **Preserve Decision History**: ADRs provide context for architectural choices
4. **Enhance Discoverability**: Clear navigation and organization
5. **Accelerate Onboarding**: New users and contributors can get productive faster

---

## Goals & Success Criteria

### Primary Goals

#### G1: Streamlined README with Clear Information Architecture

Transform the root README.md into a focused, well-organized entry point that guides users to the right information quickly.

**Success Criteria:**
- README reduced to under 300 lines (currently 497)
- Clear separation between "using the template" and "understanding the generated project"
- All placeholder text replaced with actionable information
- No template variables appearing in documentation (fix `{{ cookiecutter.license }}` issue)
- Time to first successful project generation < 10 minutes for new users
- All code examples tested and verified working

#### G2: Effective Quickstart Experience

Create a quickstart guide that gets users from zero to a running generated project in under 5 minutes with copy-paste commands.

**Success Criteria:**
- Prerequisites section reflects actual requirements (Python 3.12+, not 3.8+)
- Maximum 5 numbered steps to first successful project generation
- All commands copy-paste ready with no placeholder substitution required
- Include verification steps ("you should see X") after each major step
- Zero duplication with README.md - link to README for deeper dives
- Mentions `uv` as the recommended Python package manager

#### G3: Consolidate or Deprecate TEMPLATE_SUMMARY.md

Make a clear decision on TEMPLATE_SUMMARY.md and implement it to eliminate documentation fragmentation.

**Success Criteria:**
- Clear recommendation with rationale documented in this FRD
- If deprecated: content migration plan to appropriate locations
- If retained: clear purpose statement and audience definition
- Single source of truth for each piece of information
- Maintenance burden reduced (fewer files to update per feature change)

#### G4: Comprehensive ADR Index for Future Creation

Identify and catalog all architectural decisions that warrant ADRs, providing a roadmap for future documentation work.

**Success Criteria:**
- Minimum 10 ADRs identified with clear titles and brief descriptions
- ADRs categorized by theme (Technology, Architecture, Operations, Security, Template Design)
- Priority ranking for ADR creation order
- Each ADR description includes: decision made, alternatives considered (if known), consequences
- ADR file naming convention and location established (`docs/adr/NNN-title.md`)

### Secondary Goals

#### G5: Documentation Consistency

Ensure all documentation follows consistent patterns and terminology.

**Success Criteria:**
- Consistent capitalization (FastAPI, PostgreSQL, Keycloak - not fastapi, postgres, keycloak)
- Consistent code block language tags (bash, python, typescript, yaml)
- Consistent command formatting (`./scripts/docker-dev.sh` not `docker-dev.sh`)
- Port numbers match between docs and cookiecutter.json

#### G6: Future-Proof Documentation Structure

Create a documentation structure that scales with project growth.

**Success Criteria:**
- Clear location for new documentation (where to add new feature docs)
- Separation between template docs and generated project docs
- Version compatibility notes where applicable
- Links to external documentation (FastAPI, Lit, Keycloak) for deep dives

### Quantitative Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Root README lines | 497 | < 300 | `wc -l README.md` |
| QUICKSTART steps to running project | 7+ | 5 | Manual count |
| Documentation files with overlapping content | 3 | 1 | Manual audit |
| ADRs documented | 0 | Index of 10+ | File count in docs/adr/ |
| Broken/placeholder links | 2+ | 0 | Link checker |
| Outdated version references | 2+ | 0 | Manual audit |

### Non-Goals

- **Not rewriting generated project documentation**: The `template/{{cookiecutter.project_slug}}/` docs are generally well-organized and will not be significantly changed
- **Not creating all ADRs**: This FRD creates the index/plan; actual ADR writing is future work
- **Not changing documentation tooling**: We will continue using Markdown files, not moving to a documentation framework (MkDocs, Docusaurus, etc.)
- **Not internationalizing documentation**: English only for this phase

---

## Scope & Boundaries

### In Scope

#### 1. README.md Rework
- Restructure for clarity and reduced length
- Remove redundant content
- Fix outdated references and placeholders
- Improve navigation with better section headers
- Add table of contents
- Ensure all code examples are accurate

#### 2. QUICKSTART.md Rework
- Update prerequisites to reflect actual requirements
- Streamline to 5-step process
- Fix path references
- Add verification steps
- Remove content that duplicates README
- Add `uv` package manager instructions

#### 3. TEMPLATE_SUMMARY.md Evaluation
- Formal recommendation (keep, deprecate, or transform)
- If deprecating: migration plan for unique content
- If keeping: purpose statement and maintenance guidelines

#### 4. ADR Index Creation
- Survey codebase for architectural decisions
- Create prioritized list of ADRs needed
- Define ADR format and location
- Write brief descriptions for each planned ADR
- **Note**: Actually writing the ADRs is out of scope

### Out of Scope

#### Generated Project Documentation
The following files in `template/{{cookiecutter.project_slug}}/` are **not** in scope:
- `README.md` - Well-structured, serves its purpose
- `CLAUDE.md` - Specialized AI guidance document
- `backend/README.md` - Comprehensive backend documentation
- `backend/QUICKSTART.md` - Effective quick start guide
- `frontend/README.md` - Complete frontend documentation
- `observability/README.md` - Thorough observability docs
- `playwright/README.md` - Complete testing documentation
- `playwright/QUICK_START.md` - Effective testing quick start

**Rationale**: These documents are in better shape than root-level docs and serve a different audience (developers working in generated projects).

#### Documentation Tooling Changes
- No migration to MkDocs, Docusaurus, GitBook, or similar
- No automated documentation generation
- No documentation hosting/deployment changes

#### Code Changes
- No changes to template code
- No changes to generated project code
- No changes to cookiecutter.json (except documentation references)

#### Actual ADR Writing
- ADR index will be created
- Individual ADR documents will be written in a future effort

### Boundary Conditions

#### Files Modified
| File | Action |
|------|--------|
| `/home/ty/workspace/project-starter/README.md` | Restructure and reduce |
| `/home/ty/workspace/project-starter/QUICKSTART.md` | Rewrite with streamlined steps |
| `/home/ty/workspace/project-starter/TEMPLATE_SUMMARY.md` | Evaluate and potentially deprecate |
| `/home/ty/workspace/project-starter/docs/adr/` | Create directory and index file |

#### Files NOT Modified
| File | Reason |
|------|--------|
| `template/{{cookiecutter.project_slug}}/**/*.md` | Out of scope - generated project docs |
| `template/cookiecutter.json` | No documentation impact |
| `hooks/**` | Code, not documentation |
| `.claude/**` | Internal tooling |

### Dependencies on Other Work

| Dependency | Impact |
|------------|--------|
| `docs/todo.txt` items | Should be completed before or during this work |
| Any pending feature additions | May require documentation updates post-completion |

### Related Features (Separate Scope)

These are related but explicitly separate efforts:
- **Observability documentation** - Already well-documented in generated projects
- **Playwright testing documentation** - Already well-documented in generated projects
- **Contributing guidelines** - Could be a future addition but not in this scope

---

## User Stories / Use Cases

### User Personas

#### P1: New Template User (Primary)
**Description**: A developer who wants to quickly generate a new full-stack project using this template.

**Goals**:
- Understand what the template provides
- Generate a working project quickly
- Get the project running locally

**Pain Points Today**:
- Must read multiple documents to understand the full picture
- Confused by overlapping content between README and QUICKSTART
- Encounters outdated information (Python 3.8+ vs 3.12+)

#### P2: Template Evaluator
**Description**: A developer or architect evaluating whether this template meets their project needs.

**Goals**:
- Quickly understand the technology stack
- Understand architectural decisions
- Assess production-readiness
- Compare with alternative templates

**Pain Points Today**:
- No ADRs to understand why decisions were made
- Feature list is long but lacks depth
- Cannot quickly assess security posture

#### P3: Template Contributor
**Description**: A developer who wants to contribute improvements to the template.

**Goals**:
- Understand the codebase structure
- Know where to document new features
- Understand existing architectural decisions

**Pain Points Today**:
- No ADRs to provide context
- Unclear which doc file to update
- Risk of introducing inconsistencies

#### P4: Generated Project Developer
**Description**: A developer working on a project that was generated from this template.

**Goals**:
- Understand how features work
- Extend the generated project
- Troubleshoot issues

**Pain Points Today**:
- Good documentation exists in generated project
- Sometimes needs to trace back to template for context

### User Stories

#### US-1: Quick Project Generation
**As a** new template user,
**I want to** generate a working project in under 5 minutes,
**So that** I can start building my application quickly.

**Acceptance Criteria:**
- Prerequisites are clearly listed and accurate
- Steps are numbered and sequential
- Each step has a verification check
- No more than 5 steps to a running project
- All commands can be copy-pasted without modification

#### US-2: Understanding Template Features
**As a** template evaluator,
**I want to** quickly understand what this template provides,
**So that** I can decide if it meets my needs.

**Acceptance Criteria:**
- Feature list is organized by category
- Each feature has a brief explanation
- Links to detailed documentation for each feature
- Comparison with alternatives is implied through feature depth

#### US-3: Understanding Architectural Decisions
**As a** template contributor or evaluator,
**I want to** understand why certain technologies and patterns were chosen,
**So that** I can make informed decisions about extensions or alternatives.

**Acceptance Criteria:**
- ADR index exists with all major decisions listed
- Each ADR has a clear title and brief description
- ADRs are categorized by theme
- Priority order for ADR creation is clear

#### US-4: Finding the Right Documentation
**As a** new template user,
**I want to** quickly find the documentation I need,
**So that** I don't waste time reading irrelevant content.

**Acceptance Criteria:**
- README has a clear table of contents
- QUICKSTART is clearly linked from README
- No overlapping content between documents
- Each document has a clear purpose statement

#### US-5: Contributing Documentation
**As a** template contributor,
**I want to** know where to add documentation for new features,
**So that** I maintain consistency with existing docs.

**Acceptance Criteria:**
- Documentation structure is explained
- Guidelines for which file to update are clear
- ADR process is documented for architectural decisions

### Use Cases

#### UC-1: First-Time Project Generation

**Actor**: New Template User
**Preconditions**: User has Python 3.12+, Docker, and cookiecutter installed
**Main Flow**:
1. User reads QUICKSTART.md
2. User runs cookiecutter command
3. User answers prompts (or accepts defaults)
4. User changes to generated directory
5. User runs docker compose up
6. User verifies services are running
7. User accesses the application in browser

**Postconditions**: User has a running local development environment
**Expected Time**: < 5 minutes

#### UC-2: Template Evaluation

**Actor**: Template Evaluator
**Preconditions**: User has found the template repository
**Main Flow**:
1. User reads README.md introduction
2. User scans feature list
3. User checks technology stack
4. User reviews ADR index for architectural insights
5. User optionally generates a test project

**Postconditions**: User can make informed decision about template suitability
**Expected Time**: < 15 minutes

#### UC-3: Architecture Investigation

**Actor**: Template Contributor or Evaluator
**Preconditions**: User wants to understand a specific architectural decision
**Main Flow**:
1. User navigates to docs/adr/
2. User reads ADR index
3. User selects relevant ADR
4. User reads decision context and rationale
5. User understands consequences and trade-offs

**Postconditions**: User understands why a decision was made
**Expected Time**: < 10 minutes per ADR

#### UC-4: Documentation Update for New Feature

**Actor**: Template Contributor
**Preconditions**: User has implemented a new feature
**Main Flow**:
1. User consults documentation structure guide
2. User identifies which files need updates
3. User updates relevant files following existing patterns
4. User creates ADR if architectural decision was made
5. User verifies no duplicate content was introduced

**Postconditions**: Documentation is consistent and complete
**Expected Time**: Variable based on feature complexity

---

## Functional Requirements

### README.md Requirements

#### FR-R01: Table of Contents (Must Have)
README.md shall include a clickable table of contents at the beginning, allowing users to navigate directly to any section.

#### FR-R02: Introduction Section (Must Have)
README.md shall have an introduction section (< 50 lines) that clearly states:
- What the template creates
- Target audience
- Key differentiating features (max 5)

#### FR-R03: Prerequisites Section (Must Have)
README.md shall have a prerequisites section that lists:
- Python 3.12+ (not 3.8+)
- Docker & Docker Compose
- cookiecutter
- jq (for Keycloak scripts)
- Node.js 20+ (for frontend development)

#### FR-R04: Quick Start Reference (Must Have)
README.md shall contain a brief "Quick Start" section that links to QUICKSTART.md rather than duplicating its content.

#### FR-R05: Feature Overview (Must Have)
README.md shall organize features into categories:
- Core Stack (5-6 items)
- Security Features (4-5 items)
- Developer Experience (4-5 items)
- Optional Features (observability, etc.)

#### FR-R06: Template Variables Reference (Should Have)
README.md shall include a table of cookiecutter variables with descriptions, defaults, and examples.

#### FR-R07: Troubleshooting Reference (Should Have)
README.md shall include a concise troubleshooting section with links to detailed docs in generated projects.

#### FR-R08: No Template Variables (Must Have)
README.md shall not contain any raw template variables like `{{ cookiecutter.license }}`.

#### FR-R09: No Placeholder Links (Must Have)
README.md shall not contain placeholder links like `gh:your-username/your-template-repo`.

#### FR-R10: Line Count Target (Should Have)
README.md should be under 300 lines while maintaining completeness.

### QUICKSTART.md Requirements

#### FR-Q01: Accurate Prerequisites (Must Have)
QUICKSTART.md shall state Python 3.12+ as a prerequisite (not 3.8+).

#### FR-Q02: Five-Step Process (Must Have)
QUICKSTART.md shall present project generation in 5 numbered steps:
1. Install prerequisites
2. Generate project
3. Start services
4. Set up Keycloak
5. Access application

#### FR-Q03: Verification Steps (Must Have)
Each major step in QUICKSTART.md shall include a "You should see" verification that confirms success.

#### FR-Q04: Copy-Paste Commands (Must Have)
All commands in QUICKSTART.md shall be copy-paste ready without requiring placeholder substitution.

#### FR-Q05: Correct Path Reference (Must Have)
QUICKSTART.md shall use the correct path `cookiecutter /path/to/project-starter/template` (including `/template` suffix).

#### FR-Q06: Modern Tooling Reference (Should Have)
QUICKSTART.md should mention `uv` as the recommended Python package manager for the generated backend.

#### FR-Q07: No Duplication (Must Have)
QUICKSTART.md shall not duplicate content from README.md; instead, it shall link to README for additional information.

#### FR-Q08: Time Estimate (Should Have)
QUICKSTART.md should state "Get a running project in under 5 minutes" or similar time estimate.

### TEMPLATE_SUMMARY.md Requirements

#### FR-T01: Evaluation Decision (Must Have)
This FRD shall include a formal recommendation on whether to:
- **Option A**: Deprecate TEMPLATE_SUMMARY.md and migrate unique content
- **Option B**: Retain with clear purpose definition and maintenance guidelines
- **Option C**: Transform into a different document type (e.g., ARCHITECTURE.md)

#### FR-T02: Recommendation Rationale (Must Have)
The recommendation shall include:
- Rationale for the decision
- Impact analysis
- Migration plan (if deprecating)
- Maintenance guidelines (if retaining)

**RECOMMENDATION: Option A - Deprecate TEMPLATE_SUMMARY.md**

**Rationale:**
1. 90%+ of content duplicates README.md or QUICKSTART.md
2. Unique content (detailed template variables) can be moved to README
3. Reduces maintenance burden from 3 files to 2
4. Eliminates user confusion about which document to read
5. No clear audience that isn't served by README or QUICKSTART

**Migration Plan:**
1. Move "Template Variables" detailed table to README.md
2. Move "Customization Points" content to generated project README
3. Verify no unique content remains
4. Add deprecation notice pointing to README.md
5. Remove file in subsequent release

### ADR Index Requirements

#### FR-A01: ADR Directory (Must Have)
An ADR directory shall be created at `docs/adr/`.

#### FR-A02: ADR Index File (Must Have)
An index file shall be created at `docs/adr/README.md` containing:
- ADR format specification
- List of all planned ADRs
- Categories for ADRs
- Priority order for creation

#### FR-A03: ADR Format (Must Have)
The ADR format shall follow the standard structure:
- Title
- Status (Proposed, Accepted, Deprecated, Superseded)
- Context
- Decision
- Consequences
- Alternatives Considered (optional but recommended)

#### FR-A04: Minimum ADR Count (Must Have)
The ADR index shall contain at least 10 planned ADRs.

#### FR-A05: ADR Categories (Must Have)
ADRs shall be categorized into:
- Technology Stack
- Architecture Patterns
- Operational Decisions
- Security Decisions
- Template Design

#### FR-A06: ADR Descriptions (Must Have)
Each ADR in the index shall include:
- Unique identifier (ADR-NNN)
- Title
- Category
- Brief description (1-3 sentences)
- Priority (P1, P2, P3)

### ADR Index Content

The following ADRs shall be included in the index:

**Technology Stack (ADR-001 to ADR-004)**

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| ADR-001 | FastAPI as Backend Framework | Why FastAPI was chosen over Flask, Django, or other Python web frameworks. Factors: async support, automatic OpenAPI docs, Pydantic integration, performance. | P1 |
| ADR-002 | Lit as Frontend Framework | Why Lit was chosen over React, Vue, Svelte, or Angular. Factors: web components standard, small bundle size, no virtual DOM, native platform alignment. | P1 |
| ADR-003 | PostgreSQL as Primary Database | Why PostgreSQL was chosen over MySQL, MongoDB, or other databases. Factors: RLS support, JSONB, mature ecosystem, reliability. | P2 |
| ADR-004 | Keycloak as Identity Provider | Why Keycloak was chosen over Auth0, Okta, or custom implementation. Factors: open source, full-featured, self-hosted option, OIDC compliance. | P1 |

**Architecture Patterns (ADR-005 to ADR-009)**

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| ADR-005 | Row-Level Security for Multi-Tenancy | Why PostgreSQL RLS was chosen for tenant isolation over application-level filtering, separate schemas, or separate databases. Factors: security, simplicity, performance. | P1 |
| ADR-006 | Dual Database Users Pattern | Why separate migration and application database users are used. Factors: RLS bypass for migrations, principle of least privilege, security. | P2 |
| ADR-007 | Redis Token Revocation Strategy | Why Redis blacklist was chosen for token revocation over short-lived tokens, token introspection, or database storage. Factors: performance, simplicity, TTL support. | P2 |
| ADR-008 | JWKS Caching Strategy | How JWT validation keys are cached and refreshed. Factors: performance, security, key rotation support. | P3 |
| ADR-009 | Cookie-Based Authentication Transport | Why HTTP-only cookies are used for token transport over Authorization headers. Factors: XSS protection, CSRF considerations, browser security model. | P2 |

**Operational Decisions (ADR-010 to ADR-012)**

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| ADR-010 | Docker Compose for Development | Why Docker Compose is the primary development environment over local installation or Kubernetes. Factors: simplicity, reproducibility, service orchestration. | P2 |
| ADR-011 | Port Allocation Strategy | Why specific ports were chosen (5435 for Postgres, 8080 for Keycloak, etc.). Factors: avoiding conflicts, convention, debugging convenience. | P3 |
| ADR-012 | uv as Python Package Manager | Why uv was chosen over pip, poetry, or pipenv for the generated backend. Factors: speed, reproducibility, modern tooling. | P2 |

**Security Decisions (ADR-013 to ADR-015)**

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| ADR-013 | PKCE Enforcement for Public Clients | Why PKCE is enforced for frontend OAuth clients. Factors: security best practices, OAuth 2.1 compliance, authorization code interception protection. | P1 |
| ADR-014 | Rate Limiting Strategy | Why Redis-based rate limiting was implemented and the default limits chosen. Factors: DDoS protection, API abuse prevention, user experience. | P2 |
| ADR-015 | CORS Configuration Approach | How CORS origins are configured and why. Factors: security, development convenience, production deployment. | P3 |

**Template Design (ADR-016 to ADR-018)**

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| ADR-016 | Cookiecutter as Template Engine | Why Cookiecutter was chosen over Copier, Yeoman, or custom generation. Factors: Python ecosystem, maturity, simplicity, Jinja2 templating. | P2 |
| ADR-017 | Optional Observability Stack | Why observability is an optional feature rather than always-on or never-included. Factors: resource usage, complexity, developer preference. | P3 |
| ADR-018 | Always-On Multi-Tenancy | Why multi-tenancy and rate limiting are always enabled rather than optional. Factors: architectural complexity of removal, security defaults, production readiness. | P2 |

### Cross-Cutting Requirements

#### FR-C01: Consistent Terminology (Must Have)
All documentation shall use consistent capitalization:
- FastAPI (not fastapi, Fastapi)
- PostgreSQL (not postgres, Postgres, postgresql)
- Keycloak (not keycloak)
- Docker Compose (not docker-compose, docker compose)

#### FR-C02: Consistent Code Blocks (Must Have)
All code blocks shall use appropriate language tags:
- `bash` for shell commands
- `python` for Python code
- `typescript` for TypeScript code
- `yaml` for YAML configuration
- `json` for JSON

#### FR-C03: Consistent Command Formatting (Must Have)
All command examples shall use full paths:
- `./scripts/docker-dev.sh` not `docker-dev.sh`
- `./keycloak/setup-realm.sh` not `setup-realm.sh`

#### FR-C04: Version Accuracy (Must Have)
All version references shall match `template/cookiecutter.json`:
- Python: 3.13 (as per cookiecutter.json line 58)
- Node.js: 20
- PostgreSQL: 18
- Keycloak: 23.0

---

## Technical Approach

### Overview

This documentation overhaul is primarily a writing and restructuring effort, not a code change. The technical approach focuses on systematic analysis, content migration, and validation.

### README.md Restructuring Approach

#### Proposed New Structure

```markdown
# OAuth-Enabled Full-Stack Application Template

## Table of Contents
[auto-generated]

## Overview (20 lines)
- One paragraph description
- Target audience
- Link to QUICKSTART.md

## Features (40 lines)
### Core Stack
### Security Features
### Developer Experience
### Optional Features

## Prerequisites (15 lines)
- Bulleted list with version requirements

## Quick Start (10 lines)
- Link to QUICKSTART.md
- Brief 3-line summary

## Template Variables (50 lines)
- Table format from cookiecutter.json

## Generated Project Structure (30 lines)
- Tree diagram only
- Link to generated README for details

## Development Workflow (30 lines)
- Essential commands only
- Link to component READMEs

## Troubleshooting (20 lines)
- Common issues with links to detailed docs

## Contributing (10 lines)
- Brief guidelines
- Link to ADRs

## License (5 lines)
```

**Target: ~230 lines** (down from 497)

#### Content Migration Map

| Current Section | Action | Destination |
|-----------------|--------|-------------|
| Built-in Features (14 items) | Reorganize into categories | README Features section |
| Cookiecutter Template Structure | Keep, simplify | README |
| Generated Project Structure | Keep, simplify | README |
| Development Workflow | Reduce, link out | README + component READMEs |
| OAuth Integration code examples | Remove | Generated project docs |
| Multi-Tenancy code examples | Remove | Generated project docs |
| Rate Limiting code examples | Remove | Generated project docs |
| Token Revocation code examples | Remove | Generated project docs |
| Configuration details | Keep essential | README |
| Testing section | Remove | Generated project docs |
| Production Deployment | Keep checklist | README |
| Troubleshooting | Simplify | README |

### QUICKSTART.md Restructuring Approach

#### Proposed New Structure

```markdown
# Quick Start Guide

Get a running project in under 5 minutes.

## Prerequisites
- Python 3.12+
- Docker & Docker Compose
- cookiecutter (`pip install cookiecutter`)
- jq (`brew install jq` or `apt install jq`)

## Step 1: Generate Your Project
[command + verification]

## Step 2: Configure Environment
[command + verification]

## Step 3: Start Services
[command + verification]

## Step 4: Set Up OAuth
[command + verification]

## Step 5: Access Your Application
[URLs + verification]

## Next Steps
- Link to README for full documentation
- Link to generated project docs

## Troubleshooting
- Link to README troubleshooting section
```

**Target: ~100 lines** (down from 340)

### ADR Directory Structure

```
docs/
├── adr/
│   ├── README.md           # Index and format specification
│   ├── 001-fastapi.md      # (future - not created in this phase)
│   ├── 002-lit.md          # (future)
│   └── ...
├── futures/
│   └── documentation-overhaul.md
└── todo.txt
```

### ADR Index Template

The `docs/adr/README.md` file will follow this structure:

```markdown
# Architecture Decision Records

## About ADRs
[Brief explanation of ADR purpose and format]

## ADR Format
[Template for new ADRs]

## Index by Category

### Technology Stack
| ID | Title | Status | Priority |
[Table of ADRs]

### Architecture Patterns
[Table of ADRs]

[etc.]

## Priority Legend
- P1: Critical for understanding core architecture
- P2: Important for advanced usage/contribution
- P3: Nice to have for completeness
```

### Validation Approach

#### Pre-Implementation Validation
1. Review current README for any content not covered in migration plan
2. Verify all links in existing docs
3. Confirm version numbers against cookiecutter.json

#### Post-Implementation Validation
1. Line count verification (`wc -l` on each file)
2. Link checker (manual or automated)
3. Test project generation with new docs
4. Time-to-running-project test with fresh user
5. Content duplication audit (grep for duplicate paragraphs)

### Tools and Resources

| Tool | Purpose |
|------|---------|
| `wc -l` | Line counting |
| Manual review | Content accuracy |
| Cookiecutter | Test project generation |
| Markdown linter | Format consistency |

---

## Architecture & Integration Considerations

### Documentation Architecture

#### Document Hierarchy

```
Level 1: Entry Points
├── README.md          # Template overview and reference
└── QUICKSTART.md      # Action-oriented getting started

Level 2: Reference Documentation
├── docs/adr/          # Architectural decisions
└── cookiecutter.json  # Variable reference (linked from README)

Level 3: Generated Project Documentation
└── template/{{cookiecutter.project_slug}}/
    ├── README.md      # Generated project docs
    ├── CLAUDE.md      # AI assistance guidance
    └── [component]/README.md  # Component-specific docs
```

#### Information Flow

```
New User Journey:
README.md (scan features) → QUICKSTART.md (generate project) → Generated README.md (develop)

Evaluator Journey:
README.md (understand capabilities) → docs/adr/ (understand decisions)

Contributor Journey:
README.md (overview) → docs/adr/ (context) → Component READMEs (implementation)
```

### Integration with Existing Documentation

#### Linking Strategy

| From | To | Purpose |
|------|----|---------|
| README.md | QUICKSTART.md | Get started quickly |
| README.md | docs/adr/README.md | Understand decisions |
| README.md | Generated project READMEs | Deep dive on components |
| QUICKSTART.md | README.md | Full documentation |
| docs/adr/README.md | Implementation files | Code references |

#### Cross-Reference Standards

- Use relative links within the repository
- Include section anchors for specific topics
- Avoid deep linking to external documentation (link to main docs pages)

### Backward Compatibility

#### Breaking Changes
- Removing TEMPLATE_SUMMARY.md may break bookmarks or external links
- Mitigation: Keep file with redirect notice for one release cycle

#### Non-Breaking Changes
- README restructuring does not affect functionality
- ADR index addition is additive
- QUICKSTART improvements maintain same entry point

---

## Data Models & Schema Changes

*Not applicable - this is a documentation-only change*

---

## UI/UX Considerations

### Documentation User Experience

#### Scanability
- Use clear, descriptive headings
- Keep paragraphs short (3-5 lines)
- Use bullet points for lists
- Use tables for structured data
- Include visual breaks between sections

#### Navigation
- Table of contents at the beginning of long documents
- Consistent section naming across documents
- Clear "Next Steps" at end of each document
- Breadcrumb-style links where appropriate

#### Code Examples
- All code blocks have language tags for syntax highlighting
- Commands are copy-paste ready
- Include expected output where helpful
- Keep examples minimal but functional

### Accessibility

#### Text Formatting
- Use heading hierarchy correctly (h1 > h2 > h3)
- Avoid using only color to convey meaning
- Provide alt text concepts for diagrams (describe in text)

#### Readability
- Write at 8th grade reading level where possible
- Define acronyms on first use
- Avoid jargon without explanation
- Use active voice

### Design Patterns

#### Consistent Information Architecture

| Document Type | Purpose | Length Target |
|---------------|---------|---------------|
| README | Overview and reference | 200-300 lines |
| QUICKSTART | Step-by-step tutorial | 80-120 lines |
| ADR | Decision record | 50-100 lines |
| Component README | Component deep-dive | 150-300 lines |

#### Standard Sections by Document Type

**README Pattern:**
1. Title and badge area
2. One-line description
3. Table of contents
4. Features/capabilities
5. Getting started reference
6. Configuration reference
7. Troubleshooting
8. Contributing/license

**QUICKSTART Pattern:**
1. Time estimate
2. Prerequisites
3. Numbered steps with verification
4. Next steps
5. Help resources

**ADR Pattern:**
1. Title with ID
2. Status
3. Context
4. Decision
5. Consequences
6. Alternatives (optional)

---

## Security & Privacy Considerations

### Documentation Security

#### Sensitive Information
- Do not include real credentials, secrets, or API keys in examples
- Use clearly fake values (e.g., `change_me_in_production`, `your-secret-here`)
- Reference `.env.example` for credential templates
- Include warnings about production credential management

#### Security Documentation
- Production deployment checklist includes security items
- Default passwords are clearly marked as development-only
- HTTPS requirements documented for production
- Security ADRs (013-015) explain security decisions

### Privacy Considerations

#### User Data
- No user tracking or analytics in documentation
- No requirement to submit personal information
- Examples use fictional user data (alice@example.com, bob@example.com)

#### Repository Privacy
- Documentation assumes public repository
- No internal company information in docs
- No references to internal systems or tools

---

## Testing Strategy

### Documentation Testing

Since this is a documentation-only change, testing focuses on accuracy and usability rather than code functionality.

#### Content Accuracy Testing

| Test | Method | Pass Criteria |
|------|--------|---------------|
| Version accuracy | Compare against cookiecutter.json | All versions match |
| Command accuracy | Execute each command | All commands work |
| Link validity | Click each link | No 404s or broken anchors |
| Path accuracy | Verify paths exist | All referenced paths valid |

#### Usability Testing

| Test | Method | Pass Criteria |
|------|--------|---------------|
| Time to running project | Fresh user test | < 5 minutes |
| Documentation clarity | User feedback | No confusion reported |
| Information findability | Task-based test | Users find info in < 2 minutes |

### Test Procedures

#### T1: Fresh User Test
1. Create a test environment with prerequisites
2. Follow only QUICKSTART.md
3. Time from start to running application
4. Note any points of confusion
5. Pass: < 5 minutes, no blockers

#### T2: Link Verification
1. Use markdown link checker tool or manual review
2. Check all internal links resolve
3. Check all external links are valid
4. Check all anchor links work
5. Pass: 0 broken links

#### T3: Command Verification
1. Copy each code block command
2. Paste and execute in appropriate context
3. Verify expected outcome
4. Pass: All commands execute successfully

#### T4: Content Duplication Check
1. Grep for common phrases across README and QUICKSTART
2. Identify any significant duplicate content
3. Pass: No substantial duplication (< 10% overlap)

### Test Environment

- Clean VM or container with only prerequisites
- No cached project generations
- Standard terminal environment
- Common operating systems (Ubuntu, macOS)

---

## Implementation Phases

### Phase Overview

| Phase | Focus | Effort | Dependencies |
|-------|-------|--------|--------------|
| P1 | ADR Index Creation | 2-3 hours | None |
| P2 | QUICKSTART.md Rework | 2-3 hours | None |
| P3 | README.md Rework | 4-6 hours | P2 (to avoid duplication) |
| P4 | TEMPLATE_SUMMARY.md Deprecation | 1-2 hours | P3 (migration target ready) |
| P5 | Validation & Testing | 2-3 hours | P1-P4 complete |

**Total Estimated Effort**: 11-17 hours

### Phase 1: ADR Index Creation

**Objective**: Create the ADR directory and index file

**Tasks**:
1. Create `docs/adr/` directory
2. Create `docs/adr/README.md` with:
   - ADR format specification
   - Full index of planned ADRs (18 items from FR section)
   - Category organization
   - Priority indicators
3. Add link to ADR index from main README (placeholder)

**Deliverables**:
- `docs/adr/README.md` - ADR index and format guide

**Validation**:
- All 18 ADRs listed with descriptions
- Format template is clear and usable
- Links work correctly

### Phase 2: QUICKSTART.md Rework

**Objective**: Create a streamlined 5-step quickstart guide

**Tasks**:
1. Create backup of current QUICKSTART.md
2. Rewrite with new structure:
   - Update prerequisites (Python 3.12+)
   - Consolidate to 5 numbered steps
   - Add verification after each step
   - Remove duplicated content
   - Add uv reference
3. Fix path references
4. Test all commands

**Deliverables**:
- Updated `QUICKSTART.md` (~100 lines)

**Validation**:
- Fresh user test: < 5 minutes to running project
- No duplicate content with README
- All commands work as documented

### Phase 3: README.md Rework

**Objective**: Restructure README for clarity and reduced length

**Tasks**:
1. Create backup of current README.md
2. Add table of contents
3. Reorganize features into categories
4. Remove code examples (defer to generated project docs)
5. Fix placeholder text and template variables
6. Update prerequisites
7. Simplify Development Workflow with links
8. Add link to ADR index
9. Consolidate unique content from TEMPLATE_SUMMARY.md

**Deliverables**:
- Updated `README.md` (~230 lines)

**Validation**:
- Line count < 300
- No template variables visible
- No broken links
- Features clearly organized

### Phase 4: TEMPLATE_SUMMARY.md Deprecation

**Objective**: Deprecate TEMPLATE_SUMMARY.md with migration

**Tasks**:
1. Audit for any unique content not yet migrated
2. Migrate Template Variables table to README if needed
3. Replace content with deprecation notice:
   ```markdown
   # Deprecated

   This document has been consolidated into [README.md](./README.md).

   Please update your bookmarks.

   This file will be removed in a future release.
   ```
4. Update any internal links pointing to TEMPLATE_SUMMARY.md

**Deliverables**:
- Updated `TEMPLATE_SUMMARY.md` (deprecation notice only)

**Validation**:
- No unique content lost
- README contains all necessary information
- Deprecation notice is clear

### Phase 5: Validation & Testing

**Objective**: Verify all documentation changes

**Tasks**:
1. Run fresh user test (T1)
2. Run link verification (T2)
3. Run command verification (T3)
4. Run duplication check (T4)
5. Verify line count targets met
6. Update docs/todo.txt with completed items
7. Final review for consistency

**Deliverables**:
- Test results documentation
- Updated `docs/todo.txt`
- Sign-off on documentation changes

**Validation**:
- All tests pass
- Metrics meet targets
- No outstanding issues

### Rollout Strategy

1. **Implement in feature branch**
2. **Self-review** against FRD requirements
3. **Peer review** for clarity and accuracy
4. **Merge to main**
5. **Monitor** for user feedback

---

## Dependencies & Risks

### Dependencies

#### Internal Dependencies

| Dependency | Phase | Impact if Not Met |
|------------|-------|-------------------|
| docs/todo.txt items completion | All | Documentation may still have outdated references |
| QUICKSTART completion | P3 | README may have duplicate content |
| README completion | P4 | TEMPLATE_SUMMARY migration incomplete |

#### External Dependencies

| Dependency | Type | Mitigation |
|------------|------|------------|
| cookiecutter.json accuracy | Data | Verify versions during implementation |
| Generated project doc accuracy | Reference | Spot-check links work |

### Risks

#### R1: Content Loss During Migration (Medium)

**Description**: Unique content in TEMPLATE_SUMMARY.md may be lost during deprecation.

**Likelihood**: Medium
**Impact**: Medium

**Mitigation**:
- Detailed audit before migration
- Keep backup of original file
- Review by someone familiar with content

#### R2: User Confusion During Transition (Low)

**Description**: Users with bookmarks to old structure may be confused.

**Likelihood**: Low
**Impact**: Low

**Mitigation**:
- Deprecation notice with redirect
- Announce changes in release notes
- Keep deprecated file for one release cycle

#### R3: Scope Creep (Medium)

**Description**: Tendency to also update generated project documentation.

**Likelihood**: Medium
**Impact**: Medium (schedule)

**Mitigation**:
- Strict scope boundaries defined in this FRD
- Defer generated project doc changes to separate effort
- Track out-of-scope items for future work

#### R4: Version Drift (Low)

**Description**: cookiecutter.json versions change between FRD and implementation.

**Likelihood**: Low
**Impact**: Low

**Mitigation**:
- Verify versions at start of implementation
- Use cookiecutter.json as source of truth

### Risk Summary

| Risk | Likelihood | Impact | Mitigation Status |
|------|------------|--------|-------------------|
| R1: Content Loss | Medium | Medium | Planned |
| R2: User Confusion | Low | Low | Planned |
| R3: Scope Creep | Medium | Medium | Planned |
| R4: Version Drift | Low | Low | Planned |

### Contingency Plans

- **If content loss discovered post-migration**: Restore from backup, re-migrate
- **If user confusion reported**: Add more prominent redirect, extend deprecation period
- **If scope creep occurs**: Defer additions to future effort, document in Open Questions

---

## Open Questions

### Resolved Questions

| Question | Resolution | Date |
|----------|------------|------|
| Should TEMPLATE_SUMMARY.md be kept? | No - deprecate and migrate unique content | 2025-12-05 |
| How many ADRs should be indexed? | 18 ADRs across 5 categories | 2025-12-05 |
| What is the target line count for README? | < 300 lines | 2025-12-05 |

### Open Questions

#### OQ-1: TEMPLATE_SUMMARY.md Removal Timeline

**Question**: How long should the deprecation notice remain before full removal?

**Options**:
- A: Remove immediately with notice
- B: Keep for 1 release cycle (recommended)
- C: Keep for 2+ release cycles

**Status**: Pending decision

**Recommended**: Option B - provides time for bookmark updates without excessive maintenance burden

#### OQ-2: ADR Writing Schedule

**Question**: When should the actual ADR documents be written?

**Options**:
- A: Immediately after this documentation work
- B: Incrementally as time permits
- C: As a separate planned effort

**Status**: Pending decision

**Impact**: Does not affect this FRD scope (index only)

#### OQ-3: Contributing Guidelines

**Question**: Should a CONTRIBUTING.md file be added as part of this effort?

**Options**:
- A: Yes, add basic contributing guidelines
- B: No, defer to separate effort
- C: Add placeholder that links to ADRs

**Status**: Pending decision

**Recommended**: Option B - out of scope for this FRD, but a good follow-up item

#### OQ-4: Generated Project Docs Updates

**Question**: Should minor issues found in generated project docs be fixed opportunistically?

**Options**:
- A: Yes, fix minor issues as discovered
- B: No, strict scope adherence
- C: Document for future effort only

**Status**: Pending decision

**Recommended**: Option C - maintain scope integrity, track items for future work

### Items Discovered During Analysis

The following items were discovered during FRD creation and should be addressed:

1. **Python version inconsistency**: Root docs say 3.8+, cookiecutter.json says 3.13
2. **Leaked template variable**: `{{ cookiecutter.license }}` appears in README.md
3. **Placeholder link**: `gh:your-username/your-template-repo` in README.md
4. **Path inconsistency**: QUICKSTART says `/path/to/project-starter` but should include `/template`
5. **uv not mentioned**: Modern tooling not documented in root-level docs
6. **docs/todo.txt items**: Two known documentation debt items pending

---

## Status

**Current Status:** Ready for FRD Refiner
**Last Updated:** 2025-12-05
**Sections Completed:** 14/14 (All sections complete)
**Progress:** 100%

### Completion Summary

| Section | Status | Notes |
|---------|--------|-------|
| Problem Statement | Complete | Comprehensive analysis of all 4 documentation areas |
| Goals & Success Criteria | Complete | 6 goals with measurable success criteria |
| Scope & Boundaries | Complete | Clear in-scope and out-of-scope definitions |
| User Stories / Use Cases | Complete | 4 personas, 5 user stories, 4 use cases |
| Functional Requirements | Complete | 35 functional requirements across 5 categories |
| Technical Approach | Complete | Restructuring approaches for all documents |
| Architecture & Integration | Complete | Document hierarchy and linking strategy |
| Data Models & Schema Changes | N/A | Documentation-only change |
| UI/UX Considerations | Complete | Documentation UX patterns |
| Security & Privacy | Complete | Documentation security guidelines |
| Testing Strategy | Complete | 4 test procedures defined |
| Implementation Phases | Complete | 5 phases with effort estimates |
| Dependencies & Risks | Complete | 4 risks identified with mitigations |
| Open Questions | Complete | 3 resolved, 4 open questions |

### Key Deliverables Defined

1. **README.md Rework**: Reduce from 497 to ~230 lines with better organization
2. **QUICKSTART.md Rework**: Streamline to 5-step process, ~100 lines
3. **TEMPLATE_SUMMARY.md**: Deprecate with migration plan
4. **ADR Index**: 18 ADRs catalogued across 5 categories

### Estimated Implementation Effort

**Total: 11-17 hours** across 5 phases

### Ready for Implementation

This FRD is complete and ready for:
1. Review by stakeholders
2. Refinement if needed
3. Implementation planning
4. Task breakdown and assignment

### Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | FRD Builder Agent | Initial complete FRD |

