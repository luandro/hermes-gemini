# Multi-Step Orchestration Patterns with Gemini CLI

## Overview

Gemini CLI uses approval modes instead of separate agents. Plan mode (`--approval-mode=plan`) combines research and planning into a single read-only phase:

| Mode | Role | Writes code? | Use when |
|------|------|--------------|----------|
| `plan` | Researcher + Planner | plans/ only | Understanding architecture, designing solutions, auditing |
| `default` / `auto_edit` | Implementer | Yes | Building, fixing, refactoring, testing |

---

## Pattern 1: Plan → Implement (Research-Plan-Implement)

The safest pattern for significant changes. Plan mode handles both research and planning; implementation follows.

```python
import subprocess

repo = "/path/to/repo"

# Phase 1: Research + Plan (read-only, writes plan .md)
print("=== Phase 1: Research + Plan ===")
plan = subprocess.run(
    ['gemini', '--approval-mode=plan', '-p',
     'How does the current authentication system work? '
     'What are the main components, data flows, and pain points? '
     'Design a plan to add OAuth2 support. '
     'Consider backward compatibility and migration path.'],
    cwd=repo, capture_output=True, text=True
)
print(plan.stdout)

# Review plan file before proceeding (optional human checkpoint)
# Plan files stored in ~/.gemini/tmp/<project>/<session>/plans/ by default
# Or in .gemini/plans/ if general.plan.directory is configured

# Phase 2: Implement
print("=== Phase 2: Implement ===")
result = subprocess.run(
    ['gemini', '-p', 'Execute the plan from the plans directory step by step. '
     'Run tests after each major change.'],
    cwd=repo, capture_output=True, text=True
)
print(result.stdout)
```

---

## Pattern 2: Parallel Workers (Independent Tasks)

Use `--worktree` flag (experimental) or manual git worktrees to run multiple gemini agents in parallel.

### With `--worktree` flag

Requires `"experimental": {"worktrees": true}` in settings.json.

```python
import subprocess

repo = "/path/to/repo"

tasks = [
    ("Implement OAuth2 authentication using the passport.js library"),
    ("Add cursor-based pagination to all list endpoints"),
    ("Fix the memory leak in the WebSocket connection handler"),
]

# Launch parallel agents with worktrees
processes = []
for i, prompt in enumerate(tasks):
    p = subprocess.Popen(
        ['gemini', '-w', '-p', prompt],
        cwd=repo,
        stdout=open(f"/tmp/gemini-log-task-{i}.txt", 'w'),
        stderr=subprocess.STDOUT
    )
    processes.append((f"task-{i}", p))
    print(f"Started: task-{i}")

# Wait for all to complete (with timeout)
for name, p in processes:
    try:
        returncode = p.wait(timeout=1800)  # 30 min max per task
        print(f"Completed: {name} (exit={returncode})")
    except subprocess.TimeoutExpired:
        p.kill()
        print(f"Timed out: {name} — manual review needed")

# Worktrees persist in .gemini/worktrees/ — clean up manually when done
```

### With manual git worktrees (fallback)

```python
import subprocess

repo = "/path/to/repo"

tasks = [
    ("feat/auth-oauth", "Implement OAuth2 authentication using the passport.js library"),
    ("feat/api-pagination", "Add cursor-based pagination to all list endpoints"),
    ("fix/memory-leak", "Fix the memory leak in the WebSocket connection handler"),
]

worktrees = []

# Create worktrees
for branch, _ in tasks:
    wt_path = f"/tmp/gemini-{branch.replace('/', '-')}"
    subprocess.run(['git', 'worktree', 'add', wt_path, '-b', branch], cwd=repo)
    worktrees.append(wt_path)

# WARNING: Free tier rate limits: 60 req/min, 1000 req/day.
# With >2 workers, use --model flash to stay within limits.
# Always log stderr (stderr=subprocess.STDOUT) — lost stderr hides failures.
# Use timeout= on wait() to prevent zombie worktrees if a task hangs.

# Launch parallel gemini agents
processes = []
for (branch, prompt), wt_path in zip(tasks, worktrees):
    p = subprocess.Popen(
        ['gemini', '-p', prompt],
        cwd=wt_path,
        stdout=open(f"/tmp/gemini-log-{branch.replace('/', '-')}.txt", 'w'),
        stderr=subprocess.STDOUT
    )
    processes.append((branch, p, wt_path))
    print(f"Started: {branch}")

# Wait for all to complete (with timeout to avoid hanging indefinitely)
for branch, p, wt_path in processes:
    try:
        returncode = p.wait(timeout=1800)  # 30 min max per task
        print(f"Completed: {branch} (exit={returncode})")
    except subprocess.TimeoutExpired:
        p.kill()
        print(f"Timed out: {branch} — manual review needed")

# Review and clean up
for _, _, wt_path in processes:
    subprocess.run(['git', 'worktree', 'remove', wt_path, '--force'])
```

---

## Pattern 3: Orchestrator-Workers (Dynamic Task Decomposition)

Use plan mode to decompose a complex task, then dispatch parallel workers.

```python
import subprocess
import json
import os

repo = "/path/to/repo"

# IMPORTANT: Do not parse gemini's stdout for structured data.
# Gemini output mixes reasoning traces, ANSI codes, and chat text —
# stdout parsing is brittle and breaks across versions.
# Instead: instruct gemini to write structured output to a file, then read that file.
# Alternatively, use --output-format json for structured output.

os.makedirs(f"{repo}/.gemini/plans", exist_ok=True)

# Orchestrator: decompose task into subtasks — write output to a file
subprocess.run(
    ['gemini', '--approval-mode=plan', '-p',
     'Analyze the codebase and decompose this task into 3-5 independent subtasks: '
     '"Migrate from REST to GraphQL". '
     'Write your result as JSON to .gemini/plans/subtasks.json with format: '
     '{"subtasks": [{"id": "...", "description": "...", "files": [...]}]}'],
    cwd=repo
)

# Read structured output from file — reliable, no stdout parsing needed
with open(f"{repo}/.gemini/plans/subtasks.json") as f:
    subtasks_data = json.load(f)
subtasks = subtasks_data['subtasks']

# WARNING: Free tier rate limits: 60 req/min, 1000 req/day.
# With >2 workers, use --model flash.

# Dispatch workers in parallel
processes = []
for task in subtasks:
    wt_path = f"/tmp/gemini-{task['id']}"
    subprocess.run(['git', 'worktree', 'add', wt_path, '-b', f"graphql/{task['id']}"], cwd=repo)

    p = subprocess.Popen(
        ['gemini', '-p', task['description']],
        cwd=wt_path,
        stdout=open(f"/tmp/gemini-log-{task['id']}.txt", 'w'),
        stderr=subprocess.STDOUT
    )
    processes.append((task['id'], p, wt_path))

# Collect results
for task_id, p, wt_path in processes:
    try:
        p.wait(timeout=1800)
    except subprocess.TimeoutExpired:
        p.kill()
        print(f"Timed out: {task_id}")
        continue
    with open(f"/tmp/gemini-log-{task_id}.txt") as f:
        print(f"=== {task_id} ===")
        print(f.read()[-2000:])  # Last 2000 chars

# Clean up
for _, _, wt_path in processes:
    subprocess.run(['git', 'worktree', 'remove', wt_path, '--force'])
```

---

## Pattern 4: Validation Loop (Iterative Improvement)

Use gemini to implement, then plan mode to validate, repeating until criteria are met.

```python
import subprocess
import json

repo = "/path/to/repo"
max_iterations = 3

for i in range(max_iterations):
    print(f"=== Iteration {i+1} ===")

    # Implement / fix
    impl = subprocess.run(
        ['gemini', '-p', 'Fix all failing tests. Run pytest and fix any failures.'],
        cwd=repo, capture_output=True, text=True
    )

    # Validate with plan mode (read-only — cannot accidentally modify source files)
    subprocess.run(
        ['gemini', '--approval-mode=plan', '-p',
         'Run the test suite and report results. Do not modify any source files. '
         'Write results to .gemini/plans/validation.json: '
         '{"passed": N, "failed": N, "issues": [...], "done": true/false}'],
        cwd=repo
    )

    with open(f"{repo}/.gemini/plans/validation.json") as f:
        report = json.load(f)
    if report.get("done"):
        print("All tests passing. Done.")
        break

    print(f"Still failing, iterating...")
else:
    print("Max iterations reached. Manual review needed.")
```

---

## Pattern 5: Staged Review Pipeline

Use plan mode for security/quality audit before merge.

```python
import subprocess

repo = "/path/to/repo"

checks = [
    ("security", "Audit the staged changes for security vulnerabilities. "
                 "Check for: injection risks, auth bypasses, sensitive data exposure, "
                 "insecure dependencies. Rate severity: critical/high/medium/low."),
    ("performance", "Review staged changes for performance issues: "
                    "N+1 queries, missing indexes, blocking I/O, memory leaks, unnecessary computation."),
    ("correctness", "Review staged changes for logical errors, missing edge cases, "
                    "incorrect error handling, and race conditions."),
]

results = {}
for check_name, prompt in checks:
    result = subprocess.run(
        ['gemini', '--approval-mode=plan', '-p', prompt],
        cwd=repo, capture_output=True, text=True
    )
    results[check_name] = result.stdout

# Summarize
summary = subprocess.run(
    ['gemini', '--approval-mode=plan', '-p',
     f'Summarize these code review findings and give a go/no-go recommendation:\n\n'
     f'Security: {results["security"][:500]}\n\n'
     f'Performance: {results["performance"][:500]}\n\n'
     f'Correctness: {results["correctness"][:500]}'],
    cwd=repo, capture_output=True, text=True
)
print(summary.stdout)
```

---

## Choosing a Pattern

| Scenario | Pattern |
|----------|---------|
| Significant feature with unknown scope | Plan → Implement |
| Multiple unrelated tasks that can run in parallel | Parallel Workers |
| Large refactor needing decomposition | Orchestrator-Workers |
| Flaky tests or iterative quality improvement | Validation Loop |
| Pre-merge review | Staged Review Pipeline |
| Quick one-off task | Direct `gemini -p "..."` |

---

## Coordination Tips

- **Pass context between phases** by reading plan files or capturing stdout and passing as context in the next prompt.
- **Use `--resume`** to maintain state across multiple gemini invocations for the same logical task.
- **Limit scope per invocation** — smaller, well-defined prompts produce better results than broad open-ended ones.
- **Set stopping conditions** in your orchestration loop (`max_iterations`, timeout, explicit "done" signal in output).
- **Use `--sandbox` or `-s`** for risky experiments — container-based isolation with automatic cleanup.
- **Use `--output-format json`** for structured output when orchestrating programmatically — returns `{response, stats, error}`.
- **Use `--model flash`** for high-volume parallel tasks to stay within free tier rate limits (60/min, 1000/day).
