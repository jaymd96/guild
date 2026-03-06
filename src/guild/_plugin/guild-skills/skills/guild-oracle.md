# guild oracle

Use this skill when the user asks about guild conventions, commands, structure,
or how something should be done in a guild marketplace. Also consult this when
you need to check conventions before creating or modifying marketplace content.

## What guild is

Guild is an opinionated CLI that scaffolds and manages Claude Code plugin
marketplaces. It produces `marketplace.json` (the artifact Claude Code consumes)
from structured source files (`guild.toml` + `plugin.toml` + skill files).

Guild produces marketplaces. `psclaude` consumes them. They share a contract
(the marketplace.json schema) but are otherwise independent.

## The 10 opinions and why they matter

### 1. marketplace.json is generated, never hand-edited
`guild.toml` and `plugin.toml` are the source of truth. `marketplace.json` is
a build artifact produced by `guild build`. This prevents drift between what you
think is published and what actually is. If you need to change the output, change
the source and rebuild.

### 2. Local-first
New plugins scaffold as directories under `plugins/`. External sources (GitHub,
npm, pip) are the escape hatch for plugins you don't own. When in doubt, keep
the plugin local — it's easier to version, test, and review.

### 3. One plugin, one directory, one concern
No nesting plugins. No sharing skills between plugins. If two plugins need the
same skill content, that's either one plugin or two copies. This keeps plugins
independently deployable and reviewable.

### 4. Kebab-case names, enforced
Plugin names come from directory names. `plugins/code-review/` → plugin name
`code-review`. No configuration divergence is possible. Validation enforces
kebab-case on marketplace names, plugin names, and external source names.

### 5. Every plugin has a CLAUDE.md
A plugin without instructions is just files. `CLAUDE.md` tells Claude what the
plugin does, when to use it, and what constraints apply. It's the interface
contract between the plugin and Claude. Validation fails without it.

### 6. Skills are markdown files, nothing else
The `skills/` directory contains `.md` files only. No subdirectories. No YAML
front matter. No templating. A skill is a prompt — plain text that Claude reads
and follows.

### 7. Versions are explicit and monotonic
Every `plugin.toml` has a `version` field. Use semver. Bump the version when
content changes meaningfully. This lets consumers know when to re-install.

### 8. External sources live in guild.toml
When referencing plugins from GitHub/npm/pip, the source definition lives in
`guild.toml` under `[external.<name>]`. One place to audit all dependencies.

### 9. Validation is structural, not semantic
`guild validate` checks directory structure, file presence, naming conventions,
and TOML parsing. It does NOT evaluate whether your skills are well-written.
Content quality is your responsibility (see the `review-marketplace` skill).

### 10. CI templates ship by default
`guild init` includes GitHub Actions for validation (PR gate) and release
(tag-triggered). Start with quality gates; remove them consciously if needed.

## Commands

| Command | When to use |
|---------|-------------|
| `guild init [path]` | Creating a new marketplace. Use `--name`, `--owner`, `--email`, `--description`. |
| `guild add <name>` | Adding a new local plugin. Use `--description`. Always follow with writing CLAUDE.md and skills. |
| `guild remove <name>` | Removing a local plugin. For externals, edit guild.toml and rebuild. |
| `guild build` | After any change to guild.toml, plugin.toml, or plugin structure. Regenerates marketplace.json and README.md. |
| `guild validate` | Before committing, before PRs, as a sanity check. Exit code 1 means errors exist. |
| `guild list` | Quick inventory of what's in the marketplace. |
| `guild version <plugin> <ver>` | Bumping a plugin version after content changes. |

## Directory structure

```
my-marketplace/
├── guild.toml                    # Marketplace config + external sources
├── marketplace.json              # GENERATED — never edit
├── README.md                     # GENERATED — plugin catalogue
├── .github/workflows/
│   ├── validate.yml              # PR gate: guild validate
│   └── release.yml               # Tag → GitHub release
└── plugins/
    └── <plugin-name>/
        ├── plugin.toml           # name, version, description
        ├── CLAUDE.md             # Instructions for Claude (MANDATORY)
        └── skills/
            ├── skill-one.md
            └── skill-two.md
```

## guild.toml structure

```toml
[marketplace]
name = "my-tools"
owner = "Your Name"
owner_email = "you@example.com"     # optional
description = "What this marketplace provides"  # optional

[external.some-plugin]
source = "github"                   # or: url, git-subdir, npm, pip
repo = "owner/repo"                 # source-specific fields
ref = "v1.0"                        # optional: pin to ref
```

## Common patterns

**Adding a plugin and writing content:**
```bash
guild add review --description "Code review assistance"
# Then write: plugins/review/CLAUDE.md
# Then write: plugins/review/skills/review-checklist.md
guild build
guild validate
```

**Referencing an external plugin:**
Edit `guild.toml` to add `[external.<name>]` section, then:
```bash
guild build
guild validate
```

**Releasing a new version:**
```bash
guild version review 1.1.0
guild build
git add -A && git commit -m "Bump review to 1.1.0"
git tag v1.1.0
git push --tags
```

## Anti-patterns

- Editing `marketplace.json` directly — it will be overwritten by `guild build`
- Plugin directories without `CLAUDE.md` — validation will fail
- Non-`.md` files in `skills/` — validation will fail
- Generic plugin names like `helper` or `utils` — names should describe the concern
- Mega-plugins with 10+ skills — split into focused plugins instead
