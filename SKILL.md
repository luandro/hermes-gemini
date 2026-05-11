---
name: hermes-gemini
description: "Delegate coding tasks to Gemini CLI agent. Use when you need to build features, fix bugs, refactor code, perform code reviews, or do architecture research. Triggers: gemini, gemini-cli, coding agent, google, terminal ai, plan mode, approval mode. Requires gemini CLI installed."
license: Apache-2.0
compatibility: "Requires Gemini CLI (npm install -g @google/gemini-cli). Designed for hermes-agent; compatible with any agent skills implementation. Optional: tmux for interactive sessions, git for worktree patterns, Docker/Podman for sandbox."
metadata:
  author: luandro
  version: "2.0.0"
  tags: [Coding-Agent, Gemini, Google, Code-Review, Refactoring, Plan-Mode, Approval-Mode, Autonomous]
  related_skills: [claude-code, codex, hermes-agent, opencode]
allowed-tools: Bash(gemini:*) Bash(tmux:*) Bash(git:*) Bash(python3:*) Read Write
---

# Gemini CLI Agent

Gemini CLI is Google's open-source terminal AI coding environment. It reads files, writes patches, executes shell commands, runs tests, and performs semantic code search. Supports free tier via Google OAuth (60 req/min, 1000 req/day).

## Execution Modes

### Mode 1: One-Shot (Preferred)

Non-interactive, no PTY required — ideal for automation and scripting:

```python
result = computer(action="bash", command='gemini -p "Add error handling to src/auth.rs"', workdir="/path/to/repo")
```

Pipe context in:
```python
result = computer(action="bash", command='cat src/auth.rs | gemini -p "Review this for security issues"', workdir="/path/to/repo")
```

Resume a session:
```python
result = computer(action="bash", command='gemini --resume "latest" -p "Continue the auth module implementation"', workdir="/path/to/repo")
```

### Mode 2: Interactive TUI via tmux

Use when multi-turn conversation or real-time monitoring is needed.

**Start session:**
```python
computer(action="bash", command="tmux new-session -d -s gemini_session -x 220 -y 50")
computer(action="bash", command="tmux send-keys -t gemini_session 'cd /path/to/repo && gemini' Enter")
import time; time.sleep(3)
```

**Send prompts:**
```python
computer(action="bash", command="tmux send-keys -t gemini_session 'Fix the authentication bug in auth.rs' Enter")
time.sleep(2)
output = computer(action="bash", command="tmux capture-pane -t gemini_session -p")
```

**Clean up:**
```python
computer(action="bash", command="tmux kill-session -t gemini_session")
```

### Mode 3: JSON Output

For programmatic parsing — returns a single JSON object after completion:

```python
result = computer(action="bash", command='gemini -p "List all TODO comments" --output-format json', workdir="/path/to/repo")
# Returns: {"response": "...", "stats": {...}, "error": null}
```

### Mode 4: Stream JSON

For real-time event monitoring — emits JSONL events during execution:

```python
result = computer(action="bash", command='gemini -p "Refactor the API layer" --output-format stream-json', workdir="/path/to/repo")
# Events: init, message, tool_use, tool_result, error, result
```

## Approval Modes

Gemini CLI uses approval modes instead of separate agents:

| Mode | CLI flag | Behavior | Modifies files? |
|------|----------|----------|-----------------|
| `default` | *(default)* | Implementation with confirmation prompts | Yes (with approval) |
| `auto_edit` | `--approval-mode=auto_edit` | Auto-approve file edits, confirm shell commands | Yes |
| `plan` | `--approval-mode=plan` | Read-only research + planning. Can write `.md` to plans dir | plans/ only |
| `yolo` | `--yolo` or `--approval-mode=yolo` | Auto-approve ALL actions. CLI flag only, NOT in settings.json | Yes |

**Plan mode tools available:** `read_file`, `list_directory`, `glob`, `grep_search`, `web_fetch`, `web_search`, subagents, `ask_user`, `write_file` (`.md` plans only).

**Plan mode tools blocked:** All file writes except `.md` plans, shell commands, edit tools.

**Use plan mode for research:**
```python
# Read-only research — safe, no source code modifications
result = computer(action="bash", command='gemini --approval-mode=plan -p "Explain the auth flow in src/"', workdir="/path/to/repo")
```

**Use plan mode for planning:**
```python
# Planning — writes plan .md, no source code changes
result = computer(action="bash", command='gemini --approval-mode=plan -p "Design a caching strategy for the API"', workdir="/path/to/repo")
```

## Common Workflows

### Feature Implementation

```python
result = computer(action="bash", command='gemini -p "Implement rate limiting on /api/login using a Redis sliding window."', workdir="/path/to/repo")
```

### Plan → Implement Pipeline

```python
# 1. Research + Plan (read-only, writes plan .md)
plan = computer(action="bash", command='gemini --approval-mode=plan -p "Research the session management system and design an OAuth2 integration plan."', workdir="/path/to/repo")

# 2. Implement (executes the plan)
result = computer(action="bash", command='gemini -p "Execute the plan in the plans directory."', workdir="/path/to/repo")
```

### AI Git Commit

No built-in commit command — use the pipe pattern:

```python
# Generate commit message from diff
result = computer(action="bash", command='git diff --staged | gemini -p "Write a conventional commit message for these changes. Output only the commit message text."', workdir="/path/to/repo")
# Then commit with the generated message
```

### Sandboxed Experimentation

Container-based isolation (Docker, Podman, Seatbelt, gVisor, or LXC):

```python
result = computer(action="bash", command='gemini --sandbox -p "Refactor the database layer to use the repository pattern"', workdir="/path/to/repo")
```

Five sandbox methods: Seatbelt (macOS default), Docker/Podman (Linux default), Windows Native, gVisor/runsc, LXC/LXD.

## Parallel Work

### Using `--worktree` flag (experimental)

Requires `"experimental": {"worktrees": true}` in settings.json first. Worktrees created in `.gemini/worktrees/`, not auto-deleted on exit.

```python
import subprocess

repo = "/path/to/repo"

# Launch parallel agents with worktrees
p1 = subprocess.Popen(['gemini', '-w', '-p', 'Implement OAuth2 authentication'], cwd=repo)
p2 = subprocess.Popen(['gemini', '-w', '-p', 'Add API pagination'], cwd=repo)
p1.wait(); p2.wait()
```

### Manual git worktrees (fallback)

When worktrees are disabled or unavailable:

```python
import subprocess

subprocess.run(['git', 'worktree', 'add', '/tmp/feat-auth', '-b', 'feat/auth'], cwd='/repo')
p1 = subprocess.Popen(['gemini', '-p', 'Implement OAuth2 authentication'], cwd='/tmp/feat-auth')
p1.wait()
subprocess.run(['git', 'worktree', 'remove', '/tmp/feat-auth'])
```

**Note**: Free tier rate limits: 60 req/min, 1000 req/day. With >2 parallel workers, use `--model flash` to stay within limits.

Load [agent-patterns.md](references/agent-patterns.md) (Pattern 2) for the full parallel workers pattern with timeout handling and cleanup.

## Configuration

**`settings.json`** (at `~/.gemini/settings.json` for user-level, `.gemini/settings.json` for project-level):

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

**Key settings:**
- `model.name` — `auto` (Gemini 3), `auto-2.5` (Gemini 2.5), or manual model name
- `general.defaultApprovalMode` — `default`, `auto_edit`, or `plan` (NOT `yolo`)
- `general.plan.directory` — where plans are stored (default: `~/.gemini/tmp/<project>/<session-id>/plans/`)
- `general.plan.modelRouting` — auto-routes Pro for planning, Flash for implementation
- `general.checkpointing.enabled` — enables `/restore` command for rollback
- `experimental.worktrees` — enables `--worktree` / `-w` flag

**`GEMINI.md`** — hierarchical persistent instructions loaded from `~/.gemini/GEMINI.md`, project root, and subdirectories. Use for project conventions, commit style, constraints.

**Authentication methods:**
1. **Google OAuth** (free tier) — 60 req/min, 1000 req/day. Run `gemini` to trigger auth.
2. **Gemini API key** — set `GEMINI_API_KEY` env var. 1000 req/day.
3. **Vertex AI** — set `GOOGLE_GENAI_USE_VERTEXAI=true` + `GOOGLE_CLOUD_PROJECT`.

**Key env vars** (load [cli-reference.md](references/cli-reference.md) for the full list):
```bash
GEMINI_API_KEY=your-key           # API key auth
GOOGLE_API_KEY=your-key           # Alternative API key env var
GEMINI_SANDBOX=docker             # Force sandbox method (docker, podman, seatbelt, etc.)
DEBUG=true                        # Debug logging
```

## Reference Files

Load these on demand — do not read them unless the task calls for them:

- **[cli-reference.md](references/cli-reference.md)** — Load when you need full CLI flags, slash commands, settings.json reference, env vars, MCP configuration, or exit codes.
- **[agent-patterns.md](references/agent-patterns.md)** — Load when orchestrating multi-step workflows (plan→implement pipeline, parallel workers, validation loops, staged reviews).

## Recommended Workflow (Plan-First)

For non-trivial tasks, plan before implementing. Gemini's plan mode combines research and planning into one read-only phase.

**1. Research + Plan** — understand the codebase and create a plan without risk:
```python
plan = computer(action="bash", command='gemini --approval-mode=plan -p "Map the auth flow from login to session expiry. Design an OAuth2 integration plan. Include scope, integration points, error handling, and edge cases. Then identify gaps or risks in your own plan."', workdir="/path/to/repo")
```

**2. Implement** — reference the plan, commit frequently:
```python
result = computer(action="bash", command='gemini -p "Execute the plan from the plans directory. Commit after each logical unit of work."', workdir="/path/to/repo")
```

**Key principles:**
- **Automatic model routing** — when using `auto` model, Gemini routes to Pro during plan mode and Flash during implementation. Optimal quality per phase.
- **Self-critique the plan** — explicitly ask plan mode to find flaws in its own output before implementing.
- **Commit frequently** — gemini should commit after each logical unit; makes review and rollback tractable.
- **Treat output as junior dev code** — review diffs before merging; don't blindly trust completeness.
- **Use `--model` flag** to override model selection when needed: `auto` (recommended), `auto-2.5`, or specific model name.

## Rules for Hermes Agents

1. **Prefer one-shot mode** (`gemini -p "..."`) for single tasks — no PTY, cleaner output.
2. **Always set `workdir`** — gemini operates relative to the current directory; wrong directory produces garbage.
3. **Use `--approval-mode=plan`** for research and planning — read-only, safe, can write `.md` plans.
4. **Use `--sandbox` or `-s`** for experimental changes — container-based isolation.
5. **Use `--output-format json`** for programmatic parsing — returns `{response, stats, error}`.
6. **Use `--model` flag** for model selection — `auto` recommended for automatic routing.
7. **Respect free tier limits** — 60 req/min, 1000 req/day. Use `--model flash` for high-volume tasks.
8. **Use `--resume "latest"`** to continue the most recent session, or `--resume <session-id>` for a specific one.
9. **Use tmux only for multi-turn sessions** that genuinely require back-and-forth conversation.
10. **Always clean up tmux sessions** — `tmux kill-session -t gemini_session`.

## Pitfalls & Gotchas

1. **Gemini is a TUI app** — running `gemini` without `-p` opens interactive REPL and blocks the shell. Always use `-p` in scripts.
2. **Plan mode is read-only but CAN write plan `.md` files** — plan mode blocks source code edits and shell commands, but allows writing `.md` files to the plans directory.
3. **Free tier has hard limits** — 60 req/min, 1000 req/day with OAuth. API key has same 1000/day limit. Use `--model flash` for high-volume tasks to stay within limits.
4. **`--worktree` requires experimental flag** — must set `"experimental": {"worktrees": true}` in settings.json before `--worktree`/`-w` flag works.
5. **`--sandbox` uses containers, not git worktrees** — different isolation model. Docker/Podman on Linux, Seatbelt on macOS. Not a branch-based sandbox.
6. **`--output-format json` schema** — returns `{"response": "...", "stats": {...}, "error": null}`. Single JSON object, not streaming.
7. **`--output-format stream-json` events** — emits JSONL: `init`, `message`, `tool_use`, `tool_result`, `error`, `result`.
8. **Exit codes** — 0 = success, 1 = error, 42 = input error, 53 = turn limit exceeded.
9. **`yolo` mode is CLI-only** — `--yolo` or `--approval-mode=yolo` works on CLI but CANNOT be set in settings.json. Safety measure.
10. **Automatic model routing** — with `auto` model, plan mode uses Pro, implementation uses Flash. Controlled by `general.plan.modelRouting` setting.
11. **Plans stored outside project by default** — `~/.gemini/tmp/<project>/<session-id>/plans/`. Customize with `general.plan.directory` setting to use `.gemini/plans` in project.
12. **`--resume` takes session ID or `"latest"`** — not a conversation ID. Use `--resume "latest"` for most recent session.
13. **GEMINI.md is hierarchical** — loaded from `~/.gemini/GEMINI.md` (global), project root `GEMINI.md`, and subdirectory `GEMINI.md` files. All are merged.
