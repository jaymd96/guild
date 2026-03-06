# create plugin

Use this skill when the user wants to create a new Claude Code plugin from a
repository, codebase, library, or concept. This is the full workflow from
analysis through to a validated, buildable plugin.

## Trigger

The user says something like:
- "Create a plugin for <repo/library/tool>"
- "Package this as a Claude plugin"
- "I want Claude to be good at working with <X>"
- "Turn this repo into a guild plugin"

## The workflow

### Step 1: Analyse the source

Before writing anything, understand what you're packaging. Read the source
repository or documentation and answer:

1. **What does it do?** — One sentence. If you need two, the plugin might need
   to be two plugins.
2. **Who uses it and when?** — What task triggers someone to reach for this?
3. **What are the key concepts?** — The 3-7 ideas someone needs to use it well.
4. **What are the common mistakes?** — What do people get wrong? What's surprising?
5. **What are the patterns?** — Recurring code shapes, workflows, or conventions.

Do NOT proceed until you can answer all five. If you can't answer #2, the
plugin may not be worth creating — a plugin for something nobody reaches for
is a plugin nobody installs.

### Step 2: Determine plugin scope

A plugin is NOT a mirror of the source repo. It's a curated extraction of the
parts that make Claude better at a specific task. Ask:

- What would a competent developer wish Claude knew about this?
- What knowledge is hard to infer from the code alone?
- What conventions exist that aren't obvious from the API?

**Scope down aggressively.** A plugin with 3 excellent skills beats one with
10 mediocre skills. Each skill should represent a distinct workflow or concern
that a user would actually trigger.

### Step 3: Choose a name

- Kebab-case, always
- Descriptive of the concern, not the source (prefer `code-review` over
  `eslint-wrapper`)
- Specific enough to be meaningful, short enough to type
- Avoid generic names: `helper`, `utils`, `tools`, `misc`

### Step 4: Scaffold

```bash
guild add <plugin-name> --description "<one-line description>"
```

This creates `plugin.toml`, `CLAUDE.md`, and `skills/`. Now fill them in.

### Step 5: Write CLAUDE.md

This is the most important file. It's Claude's orientation document — read
before any skill is consulted. Structure it as:

```markdown
# <plugin-name>

One paragraph: what this plugin makes Claude good at.

## When to use these skills

Bullet list mapping each skill to its trigger condition. Be specific:
- Good: "user asks to write a database migration with zero downtime"
- Bad: "user needs help with databases"

## Key principles

The 3-5 non-obvious rules Claude must follow when this plugin is active.
These are the things that prevent common mistakes. Write them as imperatives:
- Good: "Always use frozen dataclasses for rule outputs"
- Bad: "Pants prefers frozen dataclasses"

## Constraints

Anything Claude must NOT do. Hard boundaries, not suggestions.
```

**Critical rule:** CLAUDE.md is instructions for Claude, not documentation for
humans. Every sentence should be actionable. If a sentence starts with
"<X> is a..." rewrite it as "When working with <X>, always..."

### Step 6: Write skills

One skill per file. One concern per skill. Use the `write-skill` skill for
detailed guidance on writing individual skill files.

For each skill, ask: "If someone triggers this skill, what specific task are
they trying to accomplish, and what does Claude need to know to do it well?"

Typical skill breakdown for a library/framework:
- **Getting started** — Project setup, dependencies, initial configuration
- **Core workflow** — The primary thing users do with this tool, step by step
- **Common patterns** — Recurring shapes that come up repeatedly
- **Debugging** — How to diagnose and fix common problems
- **Testing** — How to test code that uses this tool

Not every plugin needs all of these. Most need 2-4. Pick the ones where
Claude's knowledge adds the most value.

### Step 7: Validate and build

```bash
guild validate
guild build
```

Fix any errors. Review the generated `marketplace.json` to confirm it looks
right.

## Quality checklist

Before considering the plugin done:

- [ ] CLAUDE.md has specific trigger conditions for each skill
- [ ] CLAUDE.md has key principles that prevent common mistakes
- [ ] Each skill answers a clear "when would someone need this?"
- [ ] Skills are imperative ("do X") not descriptive ("X is a thing")
- [ ] Skills include concrete examples (code, commands, file structures)
- [ ] No skill exceeds ~200 lines — if longer, split it
- [ ] Plugin name describes the concern, not the source tool
- [ ] `guild validate` passes with no errors
- [ ] You've read each skill and asked "would this actually help me?"

## Example

Given a task like "create a plugin for the Ruff linter":

**Analysis:** Ruff is a fast Python linter/formatter. Developers use it when
writing Python code. Key concepts: rule selection, configuration in
pyproject.toml, per-file ignores, fixable vs. unfixable rules.

**Scope:** Don't document every rule. Focus on configuration patterns,
integration with editors/CI, and common fix workflows.

**Name:** `python-linting` (describes the concern, not the tool)

**Skills:**
1. `configure-ruff.md` — Setting up ruff in a project (pyproject.toml, rule selection, target version)
2. `fix-violations.md` — Workflow for fixing lint errors (auto-fix, manual fixes, suppression)
3. `ci-integration.md` — Adding ruff to CI pipelines (GitHub Actions, pre-commit)
