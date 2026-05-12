# hermes-gemini

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Spec%20Compliant-blue)](https://agentskills.io)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An [Agent Skills](https://agentskills.io)-compatible skill that teaches AI agents how to delegate coding tasks to [Gemini CLI](https://github.com/google-gemini/gemini-cli) -- Google's open-source terminal AI coding environment.

## Why This Skill?

Gemini CLI is a powerful coding agent, but it has non-obvious conventions that trip up automated orchestration:

- It's a **TUI app** -- running `gemini` without `-p` opens interactive REPL and blocks the shell
- **Plan mode** is read-only but CAN write `.md` plan files -- not all file writes are blocked
- **Free tier has hard limits** -- 60 req/min, 1000 req/day with Google OAuth
- **Approval modes** replace separate agents -- `plan` mode handles both research and planning
- **`--worktree` is experimental** -- requires enabling in settings.json first
- **Sandbox is container-based** -- Docker/Podman/Seatbelt, not git worktrees like other tools
- **`yolo` mode is CLI-only** -- cannot be set in settings.json for safety

This skill packages all of that knowledge so any Agent Skills-compatible AI can delegate to Gemini CLI effectively.

## What You Get

| Capability | Description |
|---|---|
| **One-shot execution** | `gemini -p "..."` for non-interactive, scriptable tasks |
| **Interactive TUI sessions** | tmux-based multi-turn conversation when needed |
| **JSON output** | `--output-format json` for programmatic parsing |
| **Stream JSON** | `--output-format stream-json` for real-time event monitoring |
| **Plan mode** | `--approval-mode=plan` for read-only research + planning |
| **Approval modes** | `default`, `auto_edit`, `plan`, `yolo` for different trust levels |
| **Parallel work** | `--worktree` flag or git worktree patterns for concurrent tasks |
| **Sandboxed experiments** | `--sandbox` for container-based isolation |
| **Free tier** | Google OAuth gives 60 req/min, 1000 req/day -- no API key needed |

## Quick Start

```bash
# Install the skill
git clone https://github.com/luandro/hermes-gemini ~/hermes/skills/hermes-gemini

# Or for Gemini CLI itself
git clone https://github.com/luandro/hermes-gemini .gemini/skills/hermes-gemini

# Or for Claude Code
git clone https://github.com/luandro/hermes-gemini ~/.claude/skills/hermes-gemini
```

**Requirements:**

- [Gemini CLI](https://github.com/google-gemini/gemini-cli) -- `npm install -g @google/gemini-cli` (also: `brew install gemini-cli`, `npx @google/gemini-cli`)
- `tmux` (optional) -- for interactive multi-turn sessions
- `git` (optional) -- for worktree-based parallel patterns
- Docker or Podman (optional) -- for sandbox isolation

## Usage Examples

### Build a Feature

```python
result = computer(
    action="bash",
    command='gemini -p "Add rate limiting on /api/login using a Redis sliding window."',
    workdir="/path/to/repo"
)
```

### Plan, Then Implement

The recommended pipeline for non-trivial tasks:

```python
# 1. Research + Plan (read-only, writes plan .md)
plan = computer(
    action="bash",
    command='gemini --approval-mode=plan -p "Research the session management system and design an OAuth2 integration plan."',
    workdir="/path/to/repo"
)

# 2. Implement (executes the plan)
result = computer(
    action="bash",
    command='gemini -p "Execute the plan from the plans directory."',
    workdir="/path/to/repo"
)
```

### Run Parallel Tasks

```python
import subprocess

# Using --worktree flag (requires experimental.worktrees in settings.json)
p1 = subprocess.Popen(['gemini', '-w', '-p', 'Implement OAuth2 authentication'], cwd='/repo')
p2 = subprocess.Popen(['gemini', '-w', '-p', 'Design REST API endpoints'], cwd='/repo')
p1.wait(); p2.wait()
```

### AI Git Commit

```python
# No built-in commit command -- use the pipe pattern
result = computer(
    action="bash",
    command='git diff --staged | gemini -p "Write a conventional commit message for these changes."',
    workdir="/path/to/repo"
)
```

## Files

```
hermes-gemini/
├── SKILL.md                    # Core skill -- execution modes, approval modes, workflows, rules
└── references/
    ├── cli-reference.md        # Full CLI flags, slash commands, settings.json, env vars, auth
    └── agent-patterns.md       # plan→implement pipeline, parallel workers, validation loops
```

The skill uses [progressive disclosure](https://agentskills.io/specification#progressive-disclosure): agents load `SKILL.md` on activation, then read reference files only when the task calls for them.

## Approval Modes

| Mode | CLI Flag | Purpose | Modifies Files? |
|---|---|---|---|
| `default` | *(default)* | Implementation with confirmation prompts | Yes (with approval) |
| `auto_edit` | `--approval-mode=auto_edit` | Auto-approve edits, confirm shell commands | Yes |
| `plan` | `--approval-mode=plan` | Read-only research + planning. Writes `.md` plans | plans/ only |
| `yolo` | `--yolo` | Auto-approve ALL actions. CLI flag only | Yes |

## Configuration

**`settings.json`** (at `~/.gemini/settings.json` or `.gemini/settings.json`):

```json
{
  "model": {
    "name": "auto"
  },
  "general": {
    "defaultApprovalMode": "default",
    "plan": {
      "enabled": true,
      "directory": ".gemini/plans",
      "modelRouting": true
    },
    "checkpointing": {
      "enabled": true
    }
  },
  "tools": {
    "sandbox": true
  },
  "experimental": {
    "worktrees": true
  }
}
```

**Key environment variables:**

```bash
GEMINI_API_KEY=your-key           # API key auth
GOOGLE_API_KEY=your-key           # Alternative API key env var
GEMINI_SANDBOX=docker             # Force sandbox method
GOOGLE_GENAI_USE_VERTEXAI=true    # Use Vertex AI
DEBUG=true                        # Debug logging
```

## Related Skills

- [forgecode](https://github.com/luandro/hermes-forgecode) -- delegate to Forge CLI
- [claude-code](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/claude-code) -- delegate to Claude Code CLI
- [codex](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/codex) -- delegate to OpenAI Codex CLI
- [opencode](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/opencode) -- delegate to OpenCode CLI

## License

Apache 2.0
