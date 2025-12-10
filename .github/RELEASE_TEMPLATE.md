# Release: v{VERSION}

## {RELEASE_NAME}

{BRIEF_DESCRIPTION}

---

## Highlights

- **{FEATURE_1}**: {DESCRIPTION_1}
- **{FEATURE_2}**: {DESCRIPTION_2}
- **{FEATURE_3}**: {DESCRIPTION_3}

---

## What's New

### New Features

{LIST_NEW_FEATURES}

### Improvements

{LIST_IMPROVEMENTS}

### Bug Fixes

{LIST_BUG_FIXES}

---

## New Cookiecutter Options

| Option | Default | Description |
|--------|---------|-------------|
| `option_name` | `default` | Description of option |

---

## Breaking Changes

{LIST_BREAKING_CHANGES_OR_NONE}

See [Migration Guide](docs/MIGRATION.md) for upgrade instructions.

---

## Installation

### New Projects

```bash
# Install cookiecutter
pip install cookiecutter

# Generate a new project
cookiecutter gh:your-org/project-starter

# Or with specific options
cookiecutter gh:your-org/project-starter \
  include_github_actions=yes \
  include_kubernetes=yes \
  include_sentry=no
```

### Upgrading Existing Projects

See the [Migration Guide](docs/MIGRATION.md) for detailed upgrade instructions.

---

## Documentation

- [Full Changelog](CHANGELOG.md)
- [Migration Guide](docs/MIGRATION.md)
- [CLAUDE.md Reference](CLAUDE.md)
- [E2E Validation Checklist](docs/E2E_VALIDATION_CHECKLIST.md)

---

## Contributors

Thanks to all contributors who helped with this release!

{CONTRIBUTOR_LIST}

---

## Checksums

```
SHA256 (project-starter-{VERSION}.tar.gz) = {HASH}
SHA256 (project-starter-{VERSION}.zip) = {HASH}
```

---

**Full Changelog**: https://github.com/your-org/project-starter/compare/v{PREVIOUS_VERSION}...v{VERSION}
