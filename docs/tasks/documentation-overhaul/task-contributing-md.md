# OPT-01: Create CONTRIBUTING.md (Optional)

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | OPT-01 |
| Title | Create CONTRIBUTING.md (Optional) |
| Domain | Documentation |
| Complexity | S (Small) |
| Estimated Effort | 2-3 hours |
| Dependencies | ADR-P1-01 (P1 ADRs should exist for reference) |
| Blocks | None |

---

## Scope

### What This Task Includes

Create a CONTRIBUTING.md file for the project-starter template that provides guidance for contributors, including:

1. How to set up a development environment
2. Code style and standards
3. How to submit changes (PR process)
4. How to write and update documentation
5. How to create new ADRs
6. Testing requirements

### What This Task Excludes

- Code of Conduct (could be separate file)
- Issue templates (GitHub-specific configuration)
- PR templates (GitHub-specific configuration)
- Detailed style guides (link to external resources)

---

## Relevant Code Areas

### File to Create

| File Path | Purpose |
|-----------|---------|
| `/home/ty/workspace/project-starter/CONTRIBUTING.md` | Contribution guidelines |

### Reference Materials

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/README.md` | Project overview, existing developer setup info |
| `/home/ty/workspace/project-starter/docs/adr/README.md` | ADR format and process |
| `/home/ty/workspace/project-starter/template/cookiecutter.json` | Template configuration reference |

---

## Implementation Details

### Proposed CONTRIBUTING.md Structure

```markdown
# Contributing to Project-Starter

Thank you for your interest in contributing to the project-starter template!

## Table of Contents

- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Standards](#code-standards)
- [Documentation](#documentation)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Architecture Decisions](#architecture-decisions)

## Development Setup

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Node.js 20+
- cookiecutter

### Getting Started
[Steps to clone, setup, and run locally]

## Making Changes

### Types of Contributions
- Bug fixes
- New features
- Documentation improvements
- Template improvements

### Branch Naming
[Convention for branch names]

## Code Standards

### Python (Backend)
- Follow PEP 8
- Use type hints
- Run `ruff` for linting

### TypeScript (Frontend)
- Follow project ESLint configuration
- Use strict TypeScript

### Template Files
- Use cookiecutter variable syntax: `{{ cookiecutter.variable }}`
- Test with multiple cookiecutter configurations

## Documentation

### Where to Document
- Template changes: Update root README.md
- Generated project changes: Update template documentation
- Architectural decisions: Create ADR in docs/adr/

### Documentation Standards
- Use consistent terminology (see README for capitalization)
- Include code examples where helpful
- Keep docs up to date with code changes

## Testing

### Template Testing
[How to test cookiecutter template changes]

### Generated Project Testing
[How to test that generated projects work correctly]

## Submitting Changes

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit PR with clear description

### PR Requirements
- Clear description of changes
- Tests pass
- Documentation updated (if applicable)
- ADR created (if architectural decision)

## Architecture Decisions

When making significant architectural decisions:

1. Review existing ADRs in `docs/adr/`
2. Use the ADR format specified in `docs/adr/README.md`
3. Submit ADR as part of or before the implementation PR

See [ADR Index](docs/adr/README.md) for existing decisions and format guidance.
```

---

## Success Criteria

1. **File Exists:** CONTRIBUTING.md exists at repository root
2. **Complete Sections:** All major sections from proposed structure are included
3. **Accurate Information:** All instructions are accurate and tested
4. **Links Work:** All internal links resolve correctly
5. **ADR Reference:** Includes clear guidance on ADR process with link to ADR index

---

## Verification Steps

```bash
# Verify file exists
ls -la /home/ty/workspace/project-starter/CONTRIBUTING.md

# Verify key sections exist
grep -E "^## " /home/ty/workspace/project-starter/CONTRIBUTING.md

# Verify links to ADR documentation
grep "docs/adr" /home/ty/workspace/project-starter/CONTRIBUTING.md

# Check line count (should be substantial but not excessive)
wc -l /home/ty/workspace/project-starter/CONTRIBUTING.md
# Expected: 100-200 lines

# Verify README links to CONTRIBUTING (should add link if not present)
grep "CONTRIBUTING" /home/ty/workspace/project-starter/README.md
```

---

## Integration Points

### Upstream Dependencies

- **ADR-P1-01:** P1 ADRs should be written to reference in contribution guidelines
- **docs/adr/README.md:** ADR format and process already documented

### Downstream Dependencies

- None directly

### Follow-up Actions

After CONTRIBUTING.md is created, consider:
- Adding link from README.md to CONTRIBUTING.md
- Adding GitHub PR template referencing contribution guidelines
- Adding GitHub issue templates

---

## Monitoring and Observability

Not applicable for documentation tasks.

---

## Infrastructure Needs

None - this task creates a documentation file.

---

## Notes

1. **Optional Task:** This task is marked optional in the FRD (OQ-3). It should be prioritized based on contributor activity and need.

2. **Reference Other Projects:** Look at well-maintained open source projects for CONTRIBUTING.md inspiration.

3. **Keep It Focused:** Avoid duplicating content from README.md. Link instead.

4. **ADR Emphasis:** Since this documentation overhaul focuses on ADRs, the ADR contribution process should be prominent.

5. **Cookiecutter-Specific:** Include guidance on testing cookiecutter templates, which is different from regular code testing.

6. **Living Document:** CONTRIBUTING.md should be updated as processes evolve.

---

## FRD References

- OQ-3: Contributing Guidelines (resolved as Option B - defer to separate effort)
- G5: Documentation Consistency
- G6: Future-Proof Documentation Structure

---

*Task Created: 2025-12-05*
*Status: Not Started*
*Priority: Optional*
