"""Tests for resolving the default ``date_updated`` of a technote build."""

from __future__ import annotations

import logging
import os
import subprocess
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, NoReturn

import pytest

from technote.metadata.builddate import (
    get_git_head_committer_date,
    get_source_date_epoch,
    resolve_date_updated,
)

COMMIT_DATE = "2024-03-05T14:15:16+02:00"
COMMIT_DATE_UTC = datetime(2024, 3, 5, 12, 15, 16, tzinfo=UTC)

SPHINX_LOGGER = "sphinx.technote.metadata.builddate"
"""Name of the standard library logger that backs the module's Sphinx
logger, for capturing its warnings with ``caplog``.
"""


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


def test_git_head_committer_date_outside_repo(
    no_repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A directory outside a repository is an ordinary authoring state, so
    it falls back silently.
    """
    with caplog.at_level(logging.WARNING, logger=SPHINX_LOGGER):
        assert get_git_head_committer_date(no_repo) is None
    assert caplog.records == []


def test_git_head_committer_date_empty_repo(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A repository without any commits yet falls back silently."""
    repo = tmp_path / "empty"
    repo.mkdir()
    git("init", "-q", cwd=repo)
    with caplog.at_level(logging.WARNING, logger=SPHINX_LOGGER):
        assert get_git_head_committer_date(repo) is None
    assert caplog.records == []


def test_git_head_committer_date_no_git(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", "")
    assert get_git_head_committer_date(git_repo) is None


def test_git_head_committer_date_no_show_signature(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``git log`` must not print signature verification lines.

    A user's ``log.showSignature = true`` would otherwise prefix the date
    with ``gpg:`` lines on a signed commit.
    """
    recorded: list[str] = []

    def fake_run(
        args: Sequence[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        recorded.extend(args)
        return subprocess.CompletedProcess(
            args=list(args),
            returncode=0,
            stdout=f"{COMMIT_DATE}\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert get_git_head_committer_date(tmp_path) == COMMIT_DATE_UTC
    assert "--no-show-signature" in recorded


def test_git_head_committer_date_unparsable_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Unparsable output falls back, with a warning, rather than raising."""

    def fake_run(
        args: Sequence[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=list(args),
            returncode=0,
            stdout=(
                "gpg: Signature made Tue Mar  5 14:15:16 2024\n"
                f"{COMMIT_DATE}\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    with caplog.at_level(logging.WARNING, logger=SPHINX_LOGGER):
        assert get_git_head_committer_date(tmp_path) is None
    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    assert "date_updated" in message
    assert "gpg:" in message
    # The warning stays on one line so that it is readable in a build log.
    assert "\n" not in message


def test_git_head_committer_date_missing_git_warns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A missing git binary is unexpected, so it warns."""

    def fake_run(args: Sequence[str], **kwargs: Any) -> NoReturn:
        raise FileNotFoundError(2, "No such file or directory", "git")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with caplog.at_level(logging.WARNING, logger=SPHINX_LOGGER):
        assert get_git_head_committer_date(tmp_path) is None
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "date_updated" in record.getMessage()
    # The type and subtype let a build opt out with suppress_warnings.
    assert record.__dict__["type"] == "technote"
    assert record.__dict__["subtype"] == "date_updated"


def test_git_head_committer_date_timeout_warns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A git invocation that times out warns."""

    def fake_run(args: Sequence[str], **kwargs: Any) -> NoReturn:
        raise subprocess.TimeoutExpired(cmd=list(args), timeout=10)

    monkeypatch.setattr(subprocess, "run", fake_run)
    with caplog.at_level(logging.WARNING, logger=SPHINX_LOGGER):
        assert get_git_head_committer_date(tmp_path) is None
    assert len(caplog.records) == 1
    assert "date_updated" in caplog.records[0].getMessage()


def test_git_head_committer_date_dubious_ownership_warns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Git refusing the repository warns; CI would otherwise silently get
    the build clock.
    """

    def fake_run(
        args: Sequence[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=list(args),
            returncode=128,
            stdout="",
            stderr=(
                "fatal: detected dubious ownership in repository at '/x'\n"
            ),
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    with caplog.at_level(logging.WARNING, logger=SPHINX_LOGGER):
        assert get_git_head_committer_date(tmp_path) is None
    assert len(caplog.records) == 1
    assert "dubious ownership" in caplog.records[0].getMessage()


def test_git_head_committer_date_empty_output_warns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A successful git that prints nothing warns."""

    def fake_run(
        args: Sequence[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=list(args), returncode=0, stdout="\n", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    with caplog.at_level(logging.WARNING, logger=SPHINX_LOGGER):
        assert get_git_head_committer_date(tmp_path) is None
    assert len(caplog.records) == 1
    assert "date_updated" in caplog.records[0].getMessage()


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


@pytest.mark.parametrize("value", ["99999999999999", "-99999999999999"])
def test_source_date_epoch_out_of_range(
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
