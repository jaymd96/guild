# guild

Scaffold and manage Claude Code plugin marketplaces.

**guild** is an opinionated CLI that creates, validates, and builds plugin marketplace
repositories for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). It
pairs with [psclaude](https://pypi.org/project/jaymd96-psclaude/) which consumes
the marketplaces guild produces.

## Install

```bash
pip install jaymd96-guild
```

## Quick Start

```bash
# Create a new marketplace
guild init my-marketplace --owner "Your Name"
cd my-marketplace

# Add plugins
guild add code-review --description "Automated code review"
guild add test-generator --description "Generate test cases"

# Edit the generated files
$EDITOR plugins/code-review/CLAUDE.md
$EDITOR plugins/code-review/skills/

# Build marketplace.json (regenerated from source)
guild build

# Validate everything
guild validate
```

## Commands

| Command | Description |
|---------|-------------|
| `guild init [path]` | Scaffold a new marketplace repo |
| `guild add <name>` | Create a new local plugin |
| `guild remove <name>` | Remove a local plugin |
| `guild build` | Regenerate marketplace.json and README |
| `guild validate` | Check structure and conventions |
| `guild list` | Show all plugins (local + external) |
| `guild version <plugin> <ver>` | Set a plugin's version |

## Marketplace Structure

```
my-marketplace/
├── guild.toml                    # Source of truth for config
├── marketplace.json              # Generated — never hand-edit
├── README.md                     # Generated — plugin catalogue
├── .github/workflows/
│   ├── validate.yml              # PR gate
│   └── release.yml               # Tag → GitHub release
└── plugins/
    └── code-review/
        ├── plugin.toml           # Name, version, description
        ├── CLAUDE.md             # Instructions for Claude
        └── skills/
            └── review.md         # Skill prompt
```

## Opinions

1. **`marketplace.json` is generated** — edit `guild.toml` and `plugin.toml`, not the output
2. **Local-first** — plugins live in the repo by default; external sources are the escape hatch
3. **One plugin, one directory** — no nesting, no sharing skills between plugins
4. **Kebab-case names** — derived from directory name, enforced by validation
5. **Every plugin has a CLAUDE.md** — instructions are mandatory, not optional
6. **Skills are markdown** — `.md` files only, no subdirectories
7. **Versions are explicit** — every plugin declares a version in `plugin.toml`
8. **External sources in `guild.toml`** — one place to audit dependencies
9. **Validation is structural** — checks conventions, not content quality
10. **CI included** — GitHub Actions workflows ship with every new marketplace

## External Plugins

Register plugins from GitHub, npm, pip, or any git URL in `guild.toml`:

```toml
[marketplace]
name = "my-tools"
owner = "James"

[external.deploy-helper]
source = "github"
repo = "acme/deploy-helper"
ref = "v2.1.0"

[external.linter]
source = "npm"
package = "@acme/claude-linter"
version = "^1.0"
```

## Consuming with psclaude

```python
from psclaude import PsClaude

client = PsClaude(
    marketplaces=["jaymd96/my-marketplace"],
    install=["code-review@my-marketplace"],
)
```

## License

MIT
