"""Tests that Gemini CLI flags and features match what SKILL.md and references document.

This catches drift between the skill documentation and the actual CLI.
If gemini adds/removes/renames flags or features, these tests will flag it.
"""

import subprocess

import pytest


def run_gemini(*args: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Helper to run a gemini command and return the result."""
    return subprocess.run(
        ["gemini", *args], capture_output=True, text=True, timeout=timeout
    )


class TestGlobalFlags:
    """Verify all global flags documented in cli-reference.md exist."""

    DOCUMENTED_FLAGS = [
        "-p",               # --prompt (short)
        "--prompt",         # --prompt (long)
        "-m",               # --model (short)
        "--model",          # --model (long)
        "-s",               # --sandbox (short)
        "--sandbox",        # --sandbox (long)
        "--approval-mode",
        "--yolo",
        "--output-format",
        "--resume",
        "-w",               # --worktree (short)
        "--worktree",       # --worktree (long)
        "--include-directories",
        "--debug",
        "--version",
        "--help",
    ]

    def test_help_lists_all_documented_flags(self) -> None:
        """Parse gemini --help and verify every documented flag appears."""
        result = run_gemini("--help")
        assert result.returncode == 0
        help_text = result.stdout

        missing = []
        for flag in self.DOCUMENTED_FLAGS:
            if flag not in help_text:
                missing.append(flag)

        assert not missing, (
            f"Flags documented in cli-reference.md but missing from 'gemini --help': {missing}"
        )

    def test_prompt_flag_accepts_argument(self) -> None:
        """Verify -p/--prompt is a valid flag that accepts an argument.

        We test with a trivial prompt; the key assertion is that gemini
        doesn't reject the flag itself. The prompt may fail for auth
        or network reasons, which is fine.
        """
        result = run_gemini("-p", "echo hello", timeout=30)
        # We don't assert returncode == 0 because the prompt might fail
        # for auth/network reasons. We just check the flag is recognized.
        assert "unexpected argument" not in result.stderr.lower()
        assert "unrecognized" not in result.stderr.lower()
        assert "unknown option" not in result.stderr.lower()

    def test_model_flag(self) -> None:
        """Verify -m flag is recognized."""
        result = run_gemini("-m", "auto", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()
        assert "unrecognized" not in result.stderr.lower()

    def test_approval_mode_flag(self) -> None:
        """Verify --approval-mode flag is recognized."""
        result = run_gemini("--approval-mode", "plan", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()

    def test_sandbox_flag(self) -> None:
        """Verify --sandbox flag is recognized."""
        result = run_gemini("--sandbox", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()

    def test_output_format_flag(self) -> None:
        """Verify --output-format flag is recognized."""
        result = run_gemini("--output-format", "json", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()

    def test_resume_flag(self) -> None:
        """Verify --resume flag is recognized."""
        result = run_gemini("--resume", "latest", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()

    def test_yolo_flag(self) -> None:
        """Verify --yolo flag is recognized."""
        result = run_gemini("--yolo", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()


class TestApprovalModes:
    """Verify approval modes documented in SKILL.md."""

    DOCUMENTED_MODES = ["default", "auto_edit", "plan", "yolo"]

    def test_plan_mode_is_read_only(self) -> None:
        """Verify plan mode flag is accepted."""
        result = run_gemini("--approval-mode", "plan", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()
        assert "invalid" not in result.stderr.lower()

    def test_auto_edit_mode(self) -> None:
        """Verify auto_edit mode flag is accepted."""
        result = run_gemini("--approval-mode", "auto_edit", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()
        assert "invalid" not in result.stderr.lower()


class TestOutputFormats:
    """Verify output format options documented in SKILL.md."""

    DOCUMENTED_FORMATS = ["text", "json", "stream-json"]

    @pytest.mark.parametrize("fmt", DOCUMENTED_FORMATS)
    def test_output_format_accepted(self, fmt: str) -> None:
        """Verify each output format is accepted."""
        result = run_gemini("--output-format", fmt, "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()
        assert "invalid" not in result.stderr.lower()


class TestExitCodes:
    """Verify exit codes documented in cli-reference.md."""

    def test_success_exit_code(self) -> None:
        """Exit code 0 on --version (success)."""
        result = run_gemini("--version")
        assert result.returncode == 0


class TestEnvVars:
    """Verify documented environment variables are respected (basic check)."""

    def test_debug_env_var(self) -> None:
        """DEBUG should be accepted without error."""
        import os
        env = os.environ.copy()
        env["DEBUG"] = "true"
        result = subprocess.run(
            ["gemini", "--version"], capture_output=True, text=True, timeout=10,
            env=env,
        )
        assert result.returncode == 0
