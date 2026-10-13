"""Release-drift checks: what is merged vs what is shipped.

Three rules, each a real incident:

- version-tag-drift : a project's fix sat on main for months because the
                      version bump was never released (bttf issue #19: the
                      README on main described locale-by-default while the
                      latest tag and crates.io still shipped the old
                      feature set).
- unreleased-commits: merges on the default branch with no tag cut since.
- stale-version-doc: README install examples pinning an old version.

Pure git + file reads. No network.
"""

from __future__ import annotations

import re
import subprocess
from typing import List, Optional, Sequence

from .finding import Finding


def _git(repo: str, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if out.returncode != 0:
        return ""
    return out.stdout.strip()


def _semver(text: str):
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if not m:
        return None
    return tuple(int(g) for g in m.groups())


def latest_tag(repo: str) -> Optional[str]:
    return _git(repo, "describe", "--tags", "--abbrev=0") or None


def default_branch(repo: str) -> str:
    head = _git(repo, "symbolic-ref", "--short", "HEAD")
    return head or "main"


def package_version(repo: str):
    """First version found in common manifests, with its file/line."""
    for name, pattern in (
        ("pyproject.toml", r'^version\s*=\s*"([^"]+)"'),
        ("package.json", r'^\s*"version"\s*:\s*"([^"]+)",?\s*$'),
        ("Cargo.toml", r'^version\s*=\s*"([^"]+)"'),
    ):
        try:
            with open(f"{repo}/{name}", encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    m = re.match(pattern, line)
                    if m:
                        return m.group(1), name, i
        except OSError:
            continue
    return None, None, None


def unreleased_commits(repo: str, tag: str, branch: str) -> List[str]:
    out = _git(repo, "log", "--format=%s", f"{tag}..{branch}")
    return [l for l in out.splitlines() if l.strip()]


def version_tag_drift(lines: Sequence[str], path: str, *, repo: str = "."):
    tag = latest_tag(repo)
    version, manifest, line_no = package_version(repo)
    if version is None:
        return
    if tag is None:
        yield Finding(
            "version-tag-drift", "error", manifest, line_no,
            f"manifest declares version {version} but the repository has no "
            "tags: nothing has ever been released.",
        )
        return
    tag_v = _semver(tag)
    if tag_v is None:
        return
    pkg_v = _semver(version)
    if pkg_v is None:
        return
    if pkg_v > tag_v:
        yield Finding(
            "version-tag-drift", "error", manifest, line_no,
            f"manifest is at {version} but the latest release tag is {tag}: "
            "the bump (and everything merged with it) is unreleased. Users "
            "installing from the registry still get the old build.",
        )
    elif tag_v > pkg_v:
        yield Finding(
            "version-tag-drift", "error", manifest, line_no,
            f"latest tag {tag} is newer than manifest version {version}: "
            "the release was cut without bumping the manifest.",
        )


def unreleased_work(lines: Sequence[str], path: str, *, repo: str = "."):
    tag = latest_tag(repo)
    branch = default_branch(repo)
    if tag is None:
        return
    commits = unreleased_commits(repo, tag, branch)
    if not commits:
        return
    newest = commits[0]
    yield Finding(
        "unreleased-commits", "warning", repo, 0,
        f"{len(commits)} commit(s) on {branch} since tag {tag} "
        f"(newest: \"{newest[:70]}\") have no release.",
    )


_STALE_PIN = re.compile(r"(?:==|@)(\d+\.\d+\.\d+)")


def stale_version_docs(lines: Sequence[str], path: str, *, repo: str = "."):
    if not path.endswith(("README.md", "readme.md")):
        return
    tag = latest_tag(repo)
    if tag is None:
        return
    tag_v = _semver(tag)
    for i, line in enumerate(lines, 1):
        for m in _STALE_PIN.finditer(line):
            pinned = _semver(m.group(1))
            if pinned is not None and tag_v is not None and pinned < tag_v:
                yield Finding(
                    "stale-version-doc", "warning", path, i,
                    f"README pins {m.group(1)} but the latest release is "
                    f"{tag}: fresh installs get an old build.",
                    line,
                )


CHECKS = {
    "version-tag-drift": (version_tag_drift, "error"),
    "unreleased-commits": (unreleased_work, "warning"),
    "stale-version-doc": (stale_version_docs, "warning"),
}

CHECK_DOCS = {
    "version-tag-drift": "manifest version vs latest git tag",
    "unreleased-commits": "commits on the branch with no tag cut since",
    "stale-version-doc": "README install examples pinning old versions",
}
