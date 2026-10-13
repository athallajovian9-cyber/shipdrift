"""Run the release-drift checks against one repository."""

from __future__ import annotations

import os
from typing import List, Sequence

from .checks import CHECKS, latest_tag
from .finding import Finding


def lint(repo: str = ".", disabled: Sequence[str] = ()) -> List[Finding]:
    findings: List[Finding] = []
    readme = None
    for candidate in ("README.md", "readme.md"):
        if os.path.isfile(os.path.join(repo, candidate)):
            readme = os.path.join(repo, candidate)
            break
    readme_lines = []
    if readme:
        with open(readme, encoding="utf-8", errors="replace") as fh:
            readme_lines = fh.read().splitlines()

    if not latest_tag(repo):
        # A repository with no tags: only the manifest check can speak.
        if "version-tag-drift" not in disabled:
            findings.extend(
                CHECKS["version-tag-drift"][0](readme_lines, readme or repo, repo=repo)
            )
        return findings

    for rule_id, (fn, _severity) in CHECKS.items():
        if rule_id in disabled:
            continue
        path = readme or repo
        findings.extend(fn(readme_lines, path, repo=repo))
    findings.sort(key=lambda f: (f.rule, f.path, f.line))
    return findings
