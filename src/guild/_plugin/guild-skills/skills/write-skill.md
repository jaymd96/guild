# write skill

Use this skill when the user wants to write, rewrite, or improve a single skill
file. This is the atomic unit of plugin content — one markdown file, one concern,
one clear purpose.

## Trigger

The user says something like:
- "Write a skill for <topic>"
- "Add a skill about <workflow>"
- "This skill isn't good enough, improve it"
- "How should I structure this skill?"

## What a skill IS

A skill is an instruction set that makes Claude better at a specific task. When
activated, Claude reads the skill and follows its guidance. The audience is
Claude, not a human reading documentation.

A good skill answers: "When someone needs to do X, what does Claude need to
know to do it excellently?"

## What a skill is NOT

- **Not documentation.** Don't explain what a library is. Explain how to use it
  correctly when performing a specific task.
- **Not a reference manual.** Don't list every API method. Cover the patterns
  and decisions that matter for the skill's specific concern.
- **Not a tutorial.** Don't walk through from zero knowledge. Assume Claude has
  general knowledge and focus on the specific, non-obvious, opinionated guidance.

## Structure

Every skill file should follow this structure:

```markdown
# <skill name>

<1-2 sentences: when to use this skill and what it helps with.>

## Trigger

<Specific conditions that activate this skill. What does the user say or ask?>

## <Main content sections>

<The actual guidance, organized by workflow step or concern.>

## Examples

<Concrete, copy-pasteable examples showing the skill applied correctly.>

## Common mistakes

<What goes wrong and how to avoid it.>
```

### The trigger section

Be specific about when this skill applies. Good triggers:
- "The user asks to add authentication to a CherryPy service"
- "The user wants to write a database migration that supports rollback"
- "A test is failing due to async timing issues"

Bad triggers:
- "The user needs help with authentication" (too broad)
- "The user is working with databases" (not a task)

### The main content

Organise by what the user needs to DO, not by what the technology IS. If you're
writing a skill about testing, organise by test type (unit, integration, e2e)
not by framework API (assertions, fixtures, runners).

Write imperatively:
- Good: "Always mock external services at the HTTP boundary, not at the client level"
- Bad: "External services can be mocked at various levels"

Be specific and concrete:
- Good: "Set `timeout_seconds = 30` in the client config. The default (120s) causes
  CI to hang when the service is unreachable."
- Bad: "Consider adjusting timeout settings as needed"

Include the WHY when it's not obvious:
- Good: "Use `frozen=True` on all dataclasses — Pants hashes rule inputs, and
  mutable objects break the cache"
- Bad: "Use `frozen=True` on all dataclasses"

### Examples section

Every skill should have at least one concrete example. Examples should be:
- **Complete** — Copy-pasteable, not pseudo-code
- **Realistic** — Based on actual use cases, not toy problems
- **Annotated** — Inline comments explaining non-obvious choices

```python
# Good example: shows a real pattern with explanation
@rule
async def compile_sources(request: CompileRequest) -> CompiledSources:
    # Use MultiGet for parallel execution — N+1 is the most common
    # performance mistake in Pants plugins
    results = await MultiGet(
        Get(CompiledFile, SourceFile(f)) for f in request.sources
    )
    return CompiledSources(files=results)
```

### Common mistakes section

List 3-5 mistakes with:
1. What goes wrong (the symptom)
2. Why it happens (the cause)
3. What to do instead (the fix)

This section has disproportionate value — preventing one mistake saves more
time than any amount of positive guidance.

## Length guidelines

- **Target: 80-150 lines.** Enough to be thorough, short enough to be read.
- **Maximum: ~200 lines.** If longer, the skill covers too many concerns. Split it.
- **Minimum: 30 lines.** If shorter, the skill might be too shallow to be useful
  — consider whether it belongs as a section in another skill instead.

## Quality signals

A skill is ready when:
- You can state its purpose in one sentence without using "and"
- Every section answers "what should Claude DO?" not "what does X mean?"
- Examples are concrete and copy-pasteable
- Someone reading it would change their behaviour (not just nod along)
- Removing any section would make the skill worse (no filler)

## Anti-patterns

**The documentation dump:** Copying API docs into a skill file. Skills should
curate and opine, not enumerate. If the user wants API docs, they can read them.

**The hedge skill:** "Consider using X. You might also want Y. It depends on
your use case." This helps nobody. Take a position. "Use X. Use Y only when Z."

**The mega-skill:** 300+ lines covering setup, configuration, usage patterns,
testing, debugging, and deployment. That's 5 skills wearing a trench coat.

**The obvious skill:** "Write clean code. Use meaningful variable names." If
Claude already knows this without the skill, the skill adds no value.

**The stale skill:** References version 2.x when the current version is 4.x.
If you're writing about something with versions, pin the version and note it.
