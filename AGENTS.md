# Project: hermes-gemini

Agent Skills-compatible skill for delegating coding tasks to the Gemini CLI.

## Architecture

- `SKILL.md` -- Agent-facing instructions (execution modes, approval modes, workflows, rules, gotchas). Loaded on skill activation.
- `references/cli-reference.md` -- Full CLI flags, slash commands, settings.json reference. Loaded on demand.
- `references/agent-patterns.md` -- Multi-step orchestration patterns (plan→implement pipeline, parallel workers, validation loops). Loaded on demand.
- `hermes-gemini.skill` -- Zip package bundling SKILL.md + references for distribution.
- `README.md` -- Human-facing overview (not loaded by agents).

## Conventions

- Frontmatter in SKILL.md follows the [Agent Skills specification](https://agentskills.io/specification): `name`, `description`, `license`, `compatibility`, `metadata` in YAML.
- Description includes trigger keywords for agent discovery (gemini, gemini-cli, coding agent, google, terminal ai, plan mode).
- Code examples use Python `computer(action="bash", ...)` syntax for hermes-agent compatibility.
- Gotchas section is the highest-value content -- every non-obvious behavior gemini exhibits in non-interactive mode.

## Key Commands

```bash
# Validate skill against spec
skills-ref validate ./hermes-gemini

# Rebuild .skill package
cd hermes-gemini && zip -r ../hermes-gemini.skill SKILL.md references/

# Check package contents
unzip -l hermes-gemini.skill
```

## Skill Writing Best Practices (from agentskills.io)

These apply to this and all sibling skills:

1. **Frontmatter in YAML, not body** -- `license`, `compatibility`, `metadata` belong in frontmatter per spec.
2. **Description triggers discovery** -- Include specific keywords agents use to match tasks to skills.
3. **Gotchas are highest-value** -- Environment-specific facts that defy reasonable assumptions.
4. **Procedures over declarations** -- Teach *how to approach* a class of problems, not *what to produce* for one instance.
5. **Defaults, not menus** -- Pick a default tool/approach; mention alternatives briefly.
6. **Aim for moderate detail** -- SKILL.md under 500 lines / 5000 tokens. Move deep reference to `references/`.
7. **Progressive disclosure** -- Tell the agent *when* to load each reference file, not just "see references/".
8. **Add what the agent lacks, omit what it knows** -- Skip generic knowledge; focus on project-specific conventions and non-obvious edge cases.
9. **Refine with real execution** -- Run the skill against real tasks, feed results back, iterate.
10. **Match specificity to fragility** -- Be prescriptive for fragile operations; give freedom where multiple approaches work.

<!-- caveman-directive -->

Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles, filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift.
Code/commits/PRs: normal. Off: "stop caveman" @[/] "normal mode".
