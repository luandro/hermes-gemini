"""Tests that all executables referenced by the skill are available and functional.

The skill references these executables in SKILL.md and AGENTS.md:
- gemini (required)
- tmux (optional, for interactive sessions)
- git (optional, for worktree patterns)
- zip / unzip (for building the .skill package)
- python3 (for subprocess examples)
"""

import shutil
import subprocess

import pytest

# --- Required executables (skill won't work without these) ---

REQUIRED_EXECUTABLES = ["gemini", "git", "zip", "unzip"]

# --- Optional executables (used for specific features) ---

OPTIONAL_EXECUTABLES = ["tmux", "python3"]


class TestRequiredExecutables:
    """Verify every executable the skill depends on is on PATH."""

    @pytest.mark.parametrize("exe", REQUIRED_EXECUTABLES)
    def test_executable_on_path(self, exe: str) -> None:
        path = shutil.which(exe)
        assert path is not None, f"Required executable '{exe}' not found on PATH"

    @pytest.mark.parametrize("exe", OPTIONAL_EXECUTABLES)
    def test_optional_executable_on_path(self, exe: str) -> None:
        path = shutil.which(exe)
        # Soft check — we record availability but don't fail
        if path is None:
            pytest.skip(f"Optional executable '{exe}' not found on PATH")


class TestGeminiBinary:
    """Basic smoke tests for the gemini binary itself."""

    def test_gemini_version_runs(self) -> None:
        result = subprocess.run(
            ["gemini", "--version"], capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"gemini --version failed: {result.stderr}"
        assert result.stdout.strip(), "gemini --version produced no output"

    def test_gemini_help_runs(self) -> None:
        result = subprocess.run(
            ["gemini", "--help"], capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"gemini --help failed: {result.stderr}"
        assert "Usage:" in result.stdout or "usage" in result.stdout.lower(), "gemini --help output missing usage info"


class TestTmuxBinary:
    """Verify tmux is functional for interactive session support."""

    @pytest.fixture
    def tmux_available(self) -> None:
        if shutil.which("tmux") is None:
            pytest.skip("tmux not installed")

    def test_tmux_version(self, tmux_available) -> None:
        result = subprocess.run(
            ["tmux", "-V"], capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"tmux -V failed: {result.stderr}"
        assert "tmux" in result.stdout.lower()

    def test_tmux_create_and_kill_session(self, tmux_available) -> None:
        session_name = "test_hermes_gemini"
        try:
            # Create a detached session
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", session_name, "-x", "80", "-y", "24"],
                capture_output=True, text=True, timeout=10,
            )
            # List sessions and verify it exists
            result = subprocess.run(
                ["tmux", "list-sessions"], capture_output=True, text=True, timeout=10
            )
            assert session_name in result.stdout, f"Session '{session_name}' not found"
            # Capture pane output
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", session_name, "-p"],
                capture_output=True, text=True, timeout=10,
            )
            assert result.returncode == 0
        finally:
            # Always clean up, even if assertions fail
            subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                capture_output=True, text=True, timeout=10,
            )


class TestGitBinary:
    """Verify git is functional for worktree patterns."""

    @pytest.fixture
    def git_available(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not installed")

    def test_git_version(self, git_available) -> None:
        result = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert "git version" in result.stdout.lower()

    def test_git_worktree_support(self, git_available) -> None:
        """Verify git supports worktree commands (used in parallel patterns)."""
        result = subprocess.run(
            ["git", "worktree", "--help"], capture_output=True, text=True, timeout=10
        )
        # git worktree --help may return 0 or just print usage
        assert "worktree" in result.stdout.lower() or result.returncode == 0
