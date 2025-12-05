# ADR-016: Cookiecutter as Template Engine

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter needs a template engine to generate new project instances from the base template. Requirements include:

1. **Variable Substitution**: Project name, database credentials, port numbers, and other configuration values must be customizable per-project
2. **Conditional Content**: Some features (observability stack) should be optionally includable
3. **File Generation**: Generate multiple files and directories with proper structure
4. **Post-Generation Hooks**: Execute scripts after generation for setup tasks (git init, lock file generation)
5. **Python Ecosystem Alignment**: The template generates Python projects; the templating tool should integrate naturally
6. **Community Adoption**: Wide usage ensures documentation, examples, and community support

The template includes ~100+ files across backend, frontend, Docker configuration, Keycloak setup, and optional observability stack.

## Decision

We chose **Cookiecutter** as the project template engine.

Cookiecutter is a command-line utility that creates projects from project templates. It uses Jinja2 for templating and is the de-facto standard in the Python ecosystem.

**Template Configuration** (`cookiecutter.json`):
```json
{
  "project_name": "My Awesome Project",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
  "postgres_version": "18",
  "postgres_port": "5435",
  "include_observability": "yes",
  "license": ["MIT", "BSD-3-Clause", "Apache-2.0", "GPL-3.0", "Proprietary"]
}
```

**Directory Structure**:
```
project-starter/
├── template/
│   ├── cookiecutter.json          # Variable definitions and defaults
│   └── {{cookiecutter.project_slug}}/  # Template directory
│       ├── backend/
│       ├── frontend/
│       ├── compose.yml
│       └── ...
├── hooks/
│   └── post_gen_project.py        # Post-generation script
└── README.md
```

**Jinja2 Templating in Files**:
```yaml
# In compose.yml
postgres:
  image: postgres:{{ cookiecutter.postgres_version }}-alpine
  ports:
    - "{{ cookiecutter.postgres_port }}:5432"
```

**Conditional Content**:
```yaml
{% if cookiecutter.include_observability == "yes" %}
  prometheus:
    image: prom/prometheus:{{ cookiecutter.prometheus_version }}
{% endif %}
```

**Post-Generation Hook** (`hooks/post_gen_project.py`):
- Removes observability files when disabled
- Makes scripts executable
- Generates `uv.lock` for backend dependencies
- Initializes git repository with initial commit
- Creates `.env` from `.env.example`

## Consequences

### Positive

1. **Mature and Battle-Tested**: Cookiecutter has been widely used since 2013. Thousands of templates exist for various frameworks and languages

2. **Python Ecosystem Native**: Installed via pip, written in Python, integrates naturally with Python development workflows. Django, FastAPI, and most Python frameworks have Cookiecutter templates

3. **Powerful Jinja2 Templating**: Full Jinja2 feature set available:
   - Variable substitution: `{{ cookiecutter.project_name }}`
   - Filters: `{{ cookiecutter.project_name.lower().replace(' ', '-') }}`
   - Conditionals: `{% if cookiecutter.include_observability == "yes" %}`
   - Loops: `{% for item in cookiecutter.items %}`

4. **Pre/Post Generation Hooks**: Python scripts execute before and after generation, enabling:
   - Input validation (pre-hook)
   - File cleanup for conditional features
   - Dependency lock file generation
   - Git initialization

5. **Extensive Documentation**: Well-documented with tutorials, examples, and community guides

6. **Simple User Experience**: End users run one command:
   ```bash
   cookiecutter gh:your-org/project-starter
   ```
   Interactive prompts collect variable values

7. **Copy Without Render**: Exclude specific files from Jinja2 processing via `_copy_without_render` list (useful for files containing `{{` that aren't templates)

### Negative

1. **No Built-in Update Mechanism**: Once a project is generated, there's no native way to pull in template updates. Projects diverge from the template over time

2. **Limited Prompt Types**: Interactive prompts are basic text input. No rich UI, multi-select, or validation during prompts (validation must happen in hooks)

3. **No Partial Generation**: Cannot regenerate a single file or component. It's all-or-nothing project generation

4. **Static Defaults**: Default values in `cookiecutter.json` are static. Dynamic defaults (e.g., based on git config) require hooks

5. **Flat Variable Namespace**: All variables share one namespace. Complex templates may have many top-level variables

### Neutral

1. **Jinja2 in Non-Python Files**: Using Jinja2 syntax in YAML, JSON, and SQL files may confuse editors/linters expecting native syntax. The `_copy_without_render` option mitigates this

2. **Hook Execution Context**: Hooks run in the generated project directory, not the template directory. Understanding this context is important for hook authors

## Alternatives Considered

### Copier

**Approach**: Modern Python template engine with update support and YAML configuration.

**Why Not Chosen**:
- Smaller community and fewer existing templates
- Update mechanism, while valuable, adds complexity
- Less battle-tested than Cookiecutter
- Could be adopted in future if update support becomes critical

**Strengths Acknowledged**:
- Native template update/sync support
- YAML-based configuration (cleaner than JSON)
- Answer file for reproducible generation

### Yeoman

**Approach**: JavaScript-based scaffolding tool with extensive generator ecosystem.

**Why Not Chosen**:
- JavaScript ecosystem misalignment (our projects are Python-primary)
- Requires Node.js installation
- Generator development more complex than Cookiecutter
- Overkill for our use case

### GitHub Template Repositories

**Approach**: Use GitHub's "Use this template" feature.

**Why Not Chosen**:
- No variable substitution (project name, ports, etc. must be manually changed)
- No conditional content (can't exclude observability stack)
- No post-generation hooks
- Essentially a glorified git clone

### Custom Solution

**Approach**: Build a bespoke template engine tailored to our needs.

**Why Not Chosen**:
- Significant development and maintenance burden
- Reinventing well-solved problems
- No community, documentation, or ecosystem
- Time better spent on template content than tooling

### Jinja2 CLI / Rendering Scripts

**Approach**: Use Jinja2 directly with custom rendering scripts.

**Why Not Chosen**:
- Requires building project generation logic from scratch
- No standardized configuration format
- No community conventions or shared knowledge
- Cookiecutter already does this well

---

## Related ADRs

- [ADR-010: Docker Compose for Development](./010-docker-compose-development.md) - Compose file uses Cookiecutter templating
- [ADR-012: uv as Python Package Manager](./012-uv-package-manager.md) - Lock file generated in post-generation hook
- [ADR-018: Always-On Multi-Tenancy](./018-always-on-multitenancy.md) - Simplifies template by removing conditional

## Implementation References

- `template/cookiecutter.json` - Variable definitions, defaults, and choices
- `template/{{cookiecutter.project_slug}}/` - Template directory with all project files
- `hooks/post_gen_project.py` - Post-generation setup script
- `README.md` - Usage instructions for template consumers
