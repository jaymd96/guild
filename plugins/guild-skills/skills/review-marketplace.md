# review marketplace

Use this skill when the user wants a quality assessment of a marketplace,
plugin, or individual skill. This goes beyond structural validation (`guild
validate`) into content quality, coverage, and actionability.

## Trigger

The user says something like:
- "Review this marketplace / plugin / skill"
- "Is this plugin any good?"
- "What's missing from this marketplace?"
- "How can I improve these skills?"
- "Give me feedback on this plugin"

## Review levels

### Level 1: Marketplace review

Assess the marketplace as a whole:

**Structural health** (start here — get the obvious stuff out of the way):
```bash
guild validate
```
If validation fails, fix structural issues before reviewing content.

**Plugin cohesion:** Do the plugins in this marketplace belong together? A
marketplace named `python-dev-tools` shouldn't contain a Kubernetes deployment
plugin. Each marketplace should have a clear theme.

**Coverage gaps:** Given the marketplace's stated purpose, are there obvious
missing plugins? Ask: "If I installed this marketplace, what would I still
need that I'd expect to be included?"

**Naming consistency:** Are plugin names at the same level of specificity?
Mixing `code-review` with `r` or `python-code-quality-checker` is inconsistent.

**External source hygiene:**
- Are refs pinned? Unpinned external sources can break without warning.
- Are all external sources still accessible?
- Is the external/local split sensible? (If you own the code, it should be local.)

### Level 2: Plugin review

Assess a single plugin:

**CLAUDE.md quality:**
- Does it have specific trigger conditions for each skill? ("When the user
  asks about X" not "when relevant")
- Does it have key principles? (The 3-5 non-obvious rules)
- Are constraints stated explicitly?
- Is it written for Claude (imperative instructions) or for humans (descriptive
  documentation)?

**Skill inventory:**
- Does each skill correspond to a distinct user task?
- Are there overlapping skills that should be merged?
- Are there mega-skills that should be split?
- Are there missing skills for obvious workflows?

**Scope assessment:**
- Is the plugin trying to do too much? (> 6 skills is a smell)
- Is the plugin too narrow? (1 skill might be a section in another plugin)
- Does the description accurately reflect what the skills cover?

### Level 3: Skill review

Assess a single skill file:

**Structure check:**
- Has a clear trigger section? (When does this activate?)
- Has concrete examples? (Not pseudo-code)
- Has a common mistakes section? (Preventing errors)
- Is between 30-200 lines? (Meaningful but focused)

**Content quality:**

Ask these questions about each major section:

1. **Is it imperative?** Every paragraph should tell Claude what to DO.
   Flag any sentence that starts with "[X] is a..." or "There are several
   ways to..." — these are documentation patterns, not skill patterns.

2. **Is it specific?** "Use appropriate error handling" is useless.
   "Catch `ConnectionError` and retry with exponential backoff, max 3 attempts"
   is actionable.

3. **Is it opinionated?** "You could use X or Y" helps nobody. "Use X.
   Use Y only when Z" helps Claude make decisions.

4. **Is it correct?** Do the examples compile/run? Are API references current?
   Are version numbers accurate?

5. **Does it add value?** Would Claude do something different after reading
   this skill? If Claude would produce the same output without the skill,
   the skill is redundant.

**The "remove it" test:** Imagine removing this skill from the plugin entirely.
What would go worse? If you can't name a specific scenario where outcomes
degrade, the skill might not be pulling its weight.

## The review output

Structure your review as:

```
## Summary

<1-2 sentences: overall quality assessment>

## Critical issues (must fix)

<Things that are wrong, misleading, or would cause Claude to give bad guidance>

## Improvements (should fix)

<Things that would make the plugin meaningfully better>

## Suggestions (nice to have)

<Polish and refinements>

## What's working well

<Specific things done right — reinforcement is as important as critique>
```

Always include "what's working well." A review that's all criticism discourages
iteration.

## Scoring rubric

Rate each dimension 1-5:

| Dimension | 1 (Poor) | 3 (Adequate) | 5 (Excellent) |
|-----------|----------|--------------|---------------|
| **Trigger clarity** | Vague or missing triggers | Triggers exist but broad | Specific, unambiguous triggers |
| **Actionability** | Descriptive / documentation-style | Mix of descriptive and imperative | Every sentence is an instruction |
| **Specificity** | Generic advice anyone could give | Some concrete guidance | Specific patterns, values, and examples |
| **Examples** | No examples or pseudo-code | Some examples, partially complete | Complete, annotated, copy-pasteable |
| **Error prevention** | No common mistakes section | Lists mistakes without fixes | Mistakes with symptoms, causes, and fixes |
| **Scope** | Too broad or too narrow | Mostly focused, some drift | One concern, fully covered |

A plugin scoring 3+ on all dimensions is ready for use. Below 3 on any
dimension means that dimension needs rework.

## Common issues found in reviews

**The "About" plugin:** CLAUDE.md reads like an About page. "Our plugin
provides..." — rewrite as instructions.

**The orphan skill:** A skill file that isn't mentioned in CLAUDE.md. Claude
may not know when to use it.

**The assumption skill:** Assumes Claude knows project-specific context that
isn't stated. "Use the standard config" — standard according to what?

**The copy-paste skill:** Content copied from the source repo's README with
minimal adaptation. Skills need to be rewritten for Claude as the audience.

**The conflicting skill:** Two skills give contradictory advice for the same
scenario. Common when skills are written by different people or at different
times.
