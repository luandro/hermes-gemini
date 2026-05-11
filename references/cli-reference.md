# Gemini CLI Reference

## Global Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--prompt <TEXT>` | `-p` | One-shot prompt, exits after completion |
| `--model <MODEL>` | `-m` | Model selection: `auto`, `auto-2.5`, or specific model name |
| `--sandbox` | `-s` | Enable container-based sandbox isolation |
| `--approval-mode <MODE>` | — | Set approval mode: `default`, `auto_edit`, `plan`, `yolo` |
| `--yolo` | — | Shortcut for `--approval-mode=yolo` (CLI only) |
| `--output-format <FMT>` | — | Output format: `text` (default), `json`, `stream-json` |
| `--resume <ID>` | — | Resume session: `"latest"` or session ID |
| `--worktree` | `-w` | Run in a git worktree (experimental, requires settings) |
| `--include-directories <DIR>` | — | Additional directories to include in context |
| `--debug` | — | Enable debug logging |
| `--version` | — | Print version and exit |
| `--help` | — | Print help and exit |

## Slash Commands

Comprehensive list of in-REPL slash commands:

| Command | Description |
|---------|-------------|
| `/about` | Show Gemini CLI version and info |
| `/agents` | List and manage subagents (built-in: `codebase_investigator`, `cli_help`) |
| `/auth` | Manage authentication (OAuth, API key, Vertex AI) |
| `/bug` | Report a bug |
| `/chat` | Start a new chat session |
| `/clear` | Clear conversation history |
| `/commands` | List and run custom commands (`.toml` files in `~/.gemini/commands/` or `.gemini/commands/`) |
| `/compress` | Compress conversation context |
| `/copy` | Copy last response to clipboard |
| `/dir` | Show current working directory |
| `/extensions` | Manage extensions (`gemini extensions install/list/enable/disable`) |
| `/help` | Show help |
| `/hooks` | Manage BeforeTool/AfterTool hooks |
| `/ide` | IDE integration settings |
| `/init` | Initialize GEMINI.md in current project |
| `/mcp` | Manage MCP servers (configured in settings.json `mcpServers`) |
| `/memory` | View and manage GEMINI.md memory files |
| `/model` | Show or switch model (`/model auto`, `/model flash`, etc.) |
| `/permissions` | Manage tool permissions |
| `/plan` | Toggle plan mode (read-only research + planning) |
| `/policies` | Manage TOML policy files in `~/.gemini/policies/` |
| `/privacy` | Privacy settings |
| `/quit` | Exit Gemini CLI |
| `/restore` | Restore to a checkpoint (requires `general.checkpointing.enabled: true`) |
| `/rewind` | Rewind conversation (or double-press Esc) |
| `/resume` | Resume a previous session |
| `/settings` | View and edit settings.json |
| `/shells` | Manage shell sessions |
| `/skills` | List and manage skills (`.gemini/skills/`) |
| `/stats` | Show session statistics |
| `/theme` | Change UI theme |
| `/tools` | List available tools |
| `/upgrade` | Check for and install updates |
| `/vim` | Toggle vim keybindings |

## @ Commands

Reference files and paths inline in prompts:

| Syntax | Description |
|--------|-------------|
| `@file.py` | Include file content in prompt |
| `@src/dir/` | Include directory listing |
| `@./path/to/file` | Relative path reference |

## Shell Passthrough

Prefix with `!` to run shell commands without leaving the REPL:

```
!git status
!npm test
!python -m pytest
```

## Model Selection

| Value | Description |
|-------|-------------|
| `auto` | Gemini 3 — automatic routing (Pro for planning, Flash for implementation) |
| `auto-2.5` | Gemini 2.5 — same routing logic with 2.5 models |
| `gemini-2.5-pro` | Manual — Gemini 2.5 Pro |
| `gemini-2.5-flash` | Manual — Gemini 2.5 Flash (faster, cheaper) |
| `gemini-2.5-flash-lite` | Manual — Gemini 2.5 Flash Lite (fastest, cheapest) |

Use `--model` flag or `/model` command to switch. `auto` recommended for most use cases.

## settings.json Reference

Located at `~/.gemini/settings.json` (user-level) or `.gemini/settings.json` (project-level).

### General Section

```json
{
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
  }
}
```

### Model Section

```json
{
  "model": {
    "name": "auto"
  }
}
```

### Tools Section

```json
{
  "tools": {
    "sandbox": true
  }
}
```

### Experimental Section

```json
{
  "experimental": {
    "worktrees": true
  }
}
```

### Hooks Section

```json
{
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "edit_file",
        "hooks": [{"type": "command", "command": "echo 'Editing file'"}]
      }
    ],
    "AfterTool": [
      {
        "matcher": "run_shell_command",
        "hooks": [{"type": "command", "command": "notify-send 'Shell command executed'"}]
      }
    ]
  }
}
```

### UI Section

```json
{
  "ui": {
    "theme": "dark"
  }
}
```

### Output Section

```json
{
  "output": {
    "format": "text"
  }
}
```

### Privacy Section

```json
{
  "privacy": {
    "analytics": false
  }
}
```

### Billing Section

```json
{
  "billing": {
    "enabled": true
  }
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Gemini API key for authentication |
| `GOOGLE_API_KEY` | Alternative API key env var |
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `true` to use Vertex AI instead of Gemini API |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID (required for Vertex AI) |
| `GEMINI_SANDBOX` | Force sandbox method: `docker`, `podman`, `seatbelt`, `gvisor`, `lxc` |
| `GEMINI_SANDBOX_IMAGE` | Custom container image for sandbox |
| `SANDBOX_MOUNTS` | Additional mount paths for sandbox |
| `SANDBOX_FLAGS` | Additional flags for sandbox runtime |
| `DEBUG` | Set to `true` for debug logging |
| `GEMINI_CLI_SYSTEM_DEFAULTS_PATH` | Custom path for system defaults |
| `GEMINI_CLI_SYSTEM_SETTINGS_PATH` | Custom path for system settings |

## MCP Configuration

Configured in settings.json under the `mcpServers` key:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_..." }
    },
    "http_service": {
      "url": "http://localhost:3000/events"
    }
  }
}
```

Manage via `/mcp` command in REPL.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error |
| `42` | Input error |
| `53` | Turn limit exceeded |

## Authentication Methods

### 1. Google OAuth (Free Tier)

Run `gemini` to trigger OAuth flow. Uses Google account. Rate limits: 60 req/min, 1000 req/day.

### 2. Gemini API Key

Set `GEMINI_API_KEY` environment variable. Get key from [Google AI Studio](https://aistudio.google.com/). Rate limit: 1000 req/day.

### 3. Vertex AI

Set environment variables:
```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=your-project-id
```

Requires Google Cloud authentication (`gcloud auth application-default login`).

## Subagents

Built-in subagents:
- `codebase_investigator` — deep codebase exploration
- `cli_help` — CLI usage help

Custom subagents: `.gemini/agents/` directory. Manage via `/agents` command.

## Skills

Skills are reusable workflows the AI can invoke as tools.

**Skill locations:**
1. `.gemini/skills/<name>/SKILL.md` — project-local
2. `~/.gemini/skills/<name>/SKILL.md` — global

Manage via `/skills` command or `gemini skills` subcommands.

## Custom Commands

`.toml` files in `~/.gemini/commands/` or `.gemini/commands/`. Manage via `/commands` command.

## Extensions

Install and manage extensions:
```bash
gemini extensions install <name>
gemini extensions list
gemini extensions enable <name>
gemini extensions disable <name>
```

Manage via `/extensions` command in REPL.

## Policy Engine

TOML policy files in `~/.gemini/policies/`. Manage via `/policies` command. Controls tool permissions and restrictions.
