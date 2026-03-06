# update plugin

Use this skill when a source repository has changed and an existing plugin needs
to reflect those changes. This covers new versions, new features, breaking
changes, deprecations, and bug fixes in the upstream source.

## Trigger

The user says something like:
- "The repo released a new version, update the plugin"
- "This library added feature X, add it to the plugin"
- "There are breaking changes in v3, update our skills"
- "This skill is outdated"
- "Refresh this plugin from the latest source"

## Before you change anything

### 1. Understand what changed

Read the source repo's changelog, release notes, or diff. Categorise each
change as:

- **New feature** — May need a new skill or additions to existing skills
- **Breaking change** — Existing skills may give incorrect guidance
- **Deprecation** — Skills referencing deprecated APIs need updating
- **Bug fix** — Skills may have been working around the bug
- **Internal change** — May not affect the plugin at all

Focus on changes that affect HOW someone uses the tool. Internal refactors
that don't change the user-facing behaviour rarely need plugin updates.

### 2. Assess impact on each skill

For each skill in the plugin, ask:
- Does this skill reference anything that changed?
- Does this skill work around a bug that's now fixed?
- Does this skill miss a new capability that its users would want?
- Is this skill's advice still correct?

### 3. Assess impact on CLAUDE.md

- Do the trigger conditions still make sense?
- Do the key principles still hold?
- Do any constraints need updating?
- Does a new skill need to be listed?

## Making the changes

### Updating existing skills

When modifying a skill:

1. **Don't patch — rewrite the section.** Appending "Note: in v3, this changed
   to..." creates confusing layers. Rewrite the guidance as if the old version
   never existed.

2. **Update examples.** Examples with outdated syntax are worse than no examples.
   If a code pattern changed, replace the example entirely.

3. **Update the common mistakes section.** New versions create new mistakes.
   Remove mistakes that are no longer possible. Add new ones.

4. **Version pin if relevant.** If the skill is version-specific, state which
   version at the top: "This skill applies to Ruff 0.8+."

### Adding new skills

If a new feature warrants its own skill:
1. Write it using the `write-skill` skill's guidelines
2. Add it to the skill list in CLAUDE.md with a trigger condition
3. Ensure it doesn't overlap with existing skills — if it does, refactor

### Removing outdated skills

If a feature was removed from the source:
1. Delete the skill file
2. Remove it from CLAUDE.md's skill list
3. Check if other skills reference the deleted one

### Updating CLAUDE.md

CLAUDE.md changes less frequently than skills. Update it when:
- A new skill is added or removed
- Key principles change due to breaking changes
- The plugin's scope expands or contracts

## Version bumping

After making changes, bump the plugin version:

```bash
guild version <plugin-name> <new-version>
```

Use semver thinking:
- **Patch** (0.1.0 → 0.1.1): Fixed incorrect advice, minor wording improvements
- **Minor** (0.1.0 → 0.2.0): New skills added, significant content updates
- **Major** (0.1.0 → 1.0.0): Breaking changes in source require fundamentally
  different guidance (rare for plugins)

## Rebuild and validate

After all changes:

```bash
guild validate
guild build
```

## The update commit

Structure the commit message to explain what changed upstream and how the
plugin responds:

```
Update <plugin> for <source> v<version>

- Updated <skill> to reflect new <API/pattern>
- Added <new-skill> for <new feature>
- Removed <old-skill> (deprecated in v<X>)
- Bumped plugin version to <Y>
```

## Common mistakes when updating

**Over-updating:** Not every upstream change needs a plugin change. Internal
refactors, performance improvements, and changes to features the plugin doesn't
cover can be ignored.

**Under-updating:** Leaving outdated examples in skills. Stale examples that
don't compile or produce errors actively harm users. Check every code block.

**Forgetting CLAUDE.md:** Adding a new skill file but not listing it in
CLAUDE.md means Claude won't know when to use it.

**Not bumping the version:** Consumers use the version to know whether to
re-install. If content changed meaningfully, bump the version.

**Patching instead of rewriting:** Adding "Note: as of v3..." to existing
paragraphs creates confusing, layered text. Rewrite cleanly for the current
version.
