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

from sphinx.util import logging

from ..sources.tomlsettings import normalize_datetime

__all__ = [
    "get_git_head_committer_date",
    "get_source_date_epoch",
    "resolve_date_updated",
]

logger = logging.getLogger(__name__)
"""Sphinx logger.

Sphinx configures its logging before ``conf.py`` is evaluated, so warnings
emitted from here reach the Sphinx warning stream and fail a build run with
``-W``.
"""

EXPECTED_GIT_ERRORS = (
    # The directory is not inside a git repository. Authoring a technote in
    # a directory that has not been made into a repository yet is normal.
    "not a git repository",
    # The repository exists but nothing has been committed yet, so HEAD does
    # not resolve. This is the state of a technote created from the template
    # but not yet committed.
    "does not have any commits yet",
    # Older versions of git report the empty repository above as an unknown
    # revision instead. Matching is case-insensitive, so this also covers
    # git's uppercase ``HEAD``.
    "ambiguous argument 'head'",
)
"""Fragments of git's stderr that mean the commit date is legitimately
unavailable, rather than that something went wrong reading it.
"""


def _warn_date_updated_fallback(reason: str) -> None:
    """Warn that ``date_updated`` is falling back to the build clock.

    Parameters
    ----------
    reason
        Why the commit date could not be read. Whitespace is collapsed so
        that multi-line output from git stays on one line.
    """
    detail = " ".join(reason.split()) or "no further detail available"
    logger.warning(
        "technote could not read the commit date for date_updated and is "
        f"falling back to the current time: {detail}",
        type="technote",
        subtype="date_updated",
    )


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
        The committer date of ``HEAD``, in UTC, or `None` if that date
        cannot be read.

    Notes
    -----
    Two outcomes are ordinary states of a technote that is being authored
    locally, so they return `None` silently: ``source_dir`` is not inside a
    git repository, and the repository has no commits yet.

    Every other failure returns `None` *and* emits a Sphinx warning, because
    the caller is about to substitute the build clock and the resulting
    technote is neither reproducible nor dated by its publication event.
    Those failures are: ``git`` is not installed, the subprocess times out,
    git exits non-zero for any other reason (for example refusing a
    repository with dubious ownership, which is what git does to a checkout
    owned by another user in a CI container), git prints nothing, and git's
    output cannot be parsed as a date. The warning carries the ``technote``
    type and ``date_updated`` subtype, so a build that genuinely cannot
    reach git can silence it with
    ``suppress_warnings = ["technote.date_updated"]`` in ``conf.py``.

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
    except (OSError, subprocess.TimeoutExpired) as e:
        _warn_date_updated_fallback(str(e) or type(e).__name__)
        return None
    if result.returncode != 0:
        stderr = result.stderr.strip()
        lowered = stderr.lower()
        if not any(
            fragment.lower() in lowered for fragment in EXPECTED_GIT_ERRORS
        ):
            _warn_date_updated_fallback(
                stderr or f"git exited with status {result.returncode}"
            )
        return None
    raw = result.stdout.strip()
    if not raw:
        _warn_date_updated_fallback("git printed nothing")
        return None
    try:
        return normalize_datetime(raw)
    except ValueError:
        _warn_date_updated_fallback(f"could not parse git's output: {raw}")
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
        4. The current time, when the commit date cannot be read: the
           source directory is not inside a git repository, the repository
           has no commits yet, or reading the commit date failed. Only the
           last of those emits a Sphinx warning; see
           `get_git_head_committer_date`.
    """
    if declared is not None:
        return declared
    if (pinned := get_source_date_epoch()) is not None:
        return pinned
    if (commit_date := get_git_head_committer_date(source_dir)) is not None:
        return commit_date
    return datetime.now(tz=UTC)
