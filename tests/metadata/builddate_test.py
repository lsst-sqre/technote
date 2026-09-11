"""Tests for resolving the default ``date_updated`` of a technote build."""

from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from technote.metadata.builddate import (
    get_git_head_committer_date,
    get_source_date_epoch,
    resolve_date_updated,
)

COMMIT_DATE = "2024-03-05T14:15:16+02:00"
COMMIT_DATE_UTC = datetime(2024, 3, 5, 12, 15, 16, tzinfo=UTC)


def git(*args: str, cwd: Path) -> None:
    subprocess.run(
        ["git", *args],  # noqa: S603, S607
        cwd=cwd,
        check=True,
        capture_output=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_AUTHOR_DATE": COMMIT_DATE,
            "GIT_COMMITTER_DATE": COMMIT_DATE,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
        },
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a git repository with one commit at ``COMMIT_DATE``."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git("init", "-q", cwd=repo)
    (repo / "index.rst").write_text("Hello\n")
    git("add", "index.rst", cwd=repo)
    git("commit", "-q", "-m", "Initial", cwd=repo)
    return repo


@pytest.fixture
def no_repo(tmp_path: Path) -> Path:
    """Create a directory that is not inside a git repository."""
    path = tmp_path / "plain"
    path.mkdir()
    return path


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep the tests independent of the developer's environment.

    ``GIT_CEILING_DIRECTORIES`` stops git from discovering a parent
    repository if the pytest temp dir happens to live inside one.
    """
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))


def test_git_head_committer_date(git_repo: Path) -> None:
    assert get_git_head_committer_date(git_repo) == COMMIT_DATE_UTC


def test_git_head_committer_date_in_subdirectory(git_repo: Path) -> None:
    subdir = git_repo / "docs"
    subdir.mkdir()
    assert get_git_head_committer_date(subdir) == COMMIT_DATE_UTC


def test_git_head_committer_date_outside_repo(no_repo: Path) -> None:
    assert get_git_head_committer_date(no_repo) is None


def test_git_head_committer_date_empty_repo(tmp_path: Path) -> None:
    repo = tmp_path / "empty"
    repo.mkdir()
    git("init", "-q", cwd=repo)
    assert get_git_head_committer_date(repo) is None


def test_git_head_committer_date_no_git(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", "")
    assert get_git_head_committer_date(git_repo) is None


def test_source_date_epoch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
    assert get_source_date_epoch() == datetime(
        2023, 11, 14, 22, 13, 20, tzinfo=UTC
    )


@pytest.mark.parametrize("value", ["", "  ", "not-a-number", "1.5"])
def test_source_date_epoch_invalid(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", value)
    assert get_source_date_epoch() is None


def test_source_date_epoch_unset() -> None:
    assert get_source_date_epoch() is None


def test_resolve_declared_wins(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
    declared = datetime(2015, 11, 23, 15, tzinfo=UTC)
    assert resolve_date_updated(declared, git_repo) == declared


def test_resolve_source_date_epoch_before_git(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
    assert resolve_date_updated(None, git_repo) == datetime(
        2023, 11, 14, 22, 13, 20, tzinfo=UTC
    )


def test_resolve_git_commit(git_repo: Path) -> None:
    assert resolve_date_updated(None, git_repo) == COMMIT_DATE_UTC


def test_resolve_is_reproducible(git_repo: Path) -> None:
    first = resolve_date_updated(None, git_repo)
    second = resolve_date_updated(None, git_repo)
    assert first == second


def test_resolve_falls_back_to_now(no_repo: Path) -> None:
    before = datetime.now(tz=UTC)
    resolved = resolve_date_updated(None, no_repo)
    after = datetime.now(tz=UTC)
    assert resolved.tzinfo is not None
    assert (
        before - timedelta(seconds=1)
        <= resolved
        <= after + timedelta(seconds=1)
    )
