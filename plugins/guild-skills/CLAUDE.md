# guild-skills

You have skills for building and managing Claude Code plugin marketplaces using
the `guild` CLI tool.

## When to use these skills

- **guild-oracle** — The user asks about guild conventions, commands, structure,
  or opinions. Also use when you need to check how guild works before taking action.
- **create-plugin** — The user wants to package a repository, codebase, or concept
  as a Claude Code plugin. This is the full workflow: analyse → scaffold → write.
- **write-skill** — The user wants to add or rewrite a single skill file. Use this
  for the atomic operation of writing one well-crafted skill.
- **update-plugin** — The user says a source repository has changed, released a new
  version, or added features. The existing plugin needs to reflect those changes.
- **review-marketplace** — The user wants a quality assessment of a marketplace,
  plugin, or skill. Not just structural validation (that's `guild validate`) but
  content quality, coverage, and actionability.

## Key principles

1. A plugin is NOT documentation. It's an instruction set that makes Claude better
   at a specific task. If you find yourself writing "X is a library that..." you've
   slipped into documentation mode. Rewrite as "When working with X, always..."

2. Skills are imperative, not descriptive. They tell Claude what to DO, not what
   something IS. The audience is Claude, not a human reading docs.

3. One skill, one concern. A skill about "testing and deployment" is two skills.
   Split aggressively.

4. The guild CLI handles mechanics (scaffold, build, validate). You handle craft
   (what to put in the files, how to structure content, quality judgment).

5. Always run `guild validate` after making structural changes. Always run
   `guild build` after modifying plugin.toml or guild.toml.
