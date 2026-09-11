"""Resolve the default ``date_updated`` for a technote build.

When ``[technote] date_updated`` is not declared in ``technote.toml``, the
technote's "updated" date describes the publication event. For a technote
published by CI, that event is the commit that was pushed, so the default is
the committer date of the checked-out commit rather than the build clock.
"""

from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from ..sources.tomlsettings import normalize_datetime

__all__ = [
    "get_git_head_committer_date",
    "get_source_date_epoch",
    "resolve_date_updated",
]


def get_source_date_epoch() -> datetime | None:
    """Read the ``SOURCE_DATE_EPOCH`` environment variable as a datetime.

    ``SOURCE_DATE_EPOCH`` is the reproducible-builds convention for pinning a
    build's timestamp; Sphinx honours it as well. Its value is an integer
    number of seconds since the Unix epoch.

    Returns
    -------
    datetime.datetime or None
        The pinned timestamp, in UTC, or `None` if the variable is unset,
        does not hold an integer, or holds a value that is out of range for
        a `~datetime.datetime`.
    """
    try:
        epoch = int(os.environ["SOURCE_DATE_EPOCH"])
        return datetime.fromtimestamp(epoch, tz=UTC)
    except (KeyError, ValueError, OverflowError, OSError):
        return None


def get_git_head_committer_date(source_dir: Path) -> datetime | None:
    """Get the committer date of the checked-out commit.

    Parameters
    ----------
    source_dir
        A directory inside the git repository (typically the technote's
        source directory).

    Returns
    -------
    datetime.datetime or None
        The committer date of ``HEAD``, in UTC, or `None` if ``git`` is not
        installed, ``source_dir`` is not inside a git repository, or the
        repository has no commits.

    Notes
    -----
    The committer date of ``HEAD`` is available on a depth-1 checkout, so
    this works in CI without fetching history.

    ``--no-show-signature`` is required because a user's git configuration
    may set ``log.showSignature = true``. With that setting, ``git log`` on a
    signed commit (every merge commit made through the GitHub UI is signed)
    prints ``gpg:`` verification lines to stdout ahead of the date, which
    would defeat the date parsing and silently fall back to the build clock.
    """
    try:
        result = subprocess.run(
            [  # noqa: S603, S607
                "git",
                "log",
                "-1",
                "--no-show-signature",
                "--format=%cI",
            ],
            cwd=source_dir,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    try:
        return normalize_datetime(raw)
    except ValueError:
        return None


def resolve_date_updated(
    declared: datetime | None, source_dir: Path
) -> datetime:
    """Resolve the ``date_updated`` for a technote build.

    Parameters
    ----------
    declared
        The ``date_updated`` declared in ``technote.toml``, or `None` if
        it is not declared.
    source_dir
        The technote's source directory, used to look up the git commit.

    Returns
    -------
    datetime.datetime
        The first available of, in order:

        1. The declared ``date_updated``.
        2. The ``SOURCE_DATE_EPOCH`` environment variable.
        3. The committer date of the checked-out git commit.
        4. The current time, as a last resort when the source directory is
           not inside a git repository.
    """
    if declared is not None:
        return declared
    if (pinned := get_source_date_epoch()) is not None:
        return pinned
    if (commit_date := get_git_head_committer_date(source_dir)) is not None:
        return commit_date
    return datetime.now(tz=UTC)
