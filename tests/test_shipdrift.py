"""Tests against real temporary git repositories."""

from __future__ import annotations

import os
import subprocess

import pytest

from shipdrift.checks import latest_tag, package_version, unreleased_commits
from shipdrift.engine import lint


def git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t",
        },
    )


def make_repo(tmp_path, manifest='[project]\nname = "demo"\nversion = "1.2.3"\n',
              tag="v1.2.3", readme=None):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text(manifest, encoding="utf-8")
    if readme is not None:
        (repo / "README.md").write_text(readme, encoding="utf-8")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "initial")
    if tag:
        git(repo, "tag", tag)
    return repo


class TestHelpers:
    def test_latest_tag(self, tmp_path):
        repo = make_repo(tmp_path, tag="v9.9.9")
        assert latest_tag(str(repo)) == "v9.9.9"

    def test_package_version(self, tmp_path):
        repo = make_repo(tmp_path)
        version, manifest, line = package_version(str(repo))
        assert (version, manifest, line) == ("1.2.3", "pyproject.toml", 3)

    def test_unreleased_commits(self, tmp_path):
        repo = make_repo(tmp_path)
        (repo / "x.py").write_text("x = 1\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "merge the feature")
        assert unreleased_commits(str(repo), "v1.2.3", "main") == [
            "merge the feature"
        ]


class TestVersionTagDrift:
    def test_in_sync_is_quiet(self, tmp_path):
        repo = make_repo(tmp_path)
        assert lint(str(repo)) == []

    def test_unreleased_bump_is_an_error(self, tmp_path):
        repo = make_repo(
            tmp_path,
            manifest='[project]\nname = "demo"\nversion = "1.3.0"\n',
        )
        findings = lint(str(repo))
        drift = [f for f in findings if f.rule == "version-tag-drift"]
        assert len(drift) == 1
        assert "unreleased" in drift[0].message
        assert drift[0].severity == "error"

    def test_tag_without_bump(self, tmp_path):
        repo = make_repo(
            tmp_path,
            manifest='[project]\nname = "demo"\nversion = "1.2.0"\n',
            tag="v1.2.3",
        )
        findings = lint(str(repo))
        assert any(f.rule == "version-tag-drift" and "without bumping" in f.message
                   for f in findings)

    def test_never_released(self, tmp_path):
        repo = make_repo(tmp_path, tag=None)
        findings = lint(str(repo))
        assert len(findings) == 1
        assert "no tags" in findings[0].message


class TestUnreleasedCommits:
    def test_commits_since_tag_warn(self, tmp_path):
        repo = make_repo(tmp_path)
        (repo / "a.py").write_text("a = 1\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "fix the bug")
        findings = lint(str(repo))
        unreleased = [f for f in findings if f.rule == "unreleased-commits"]
        assert len(unreleased) == 1
        assert "fix the bug" in unreleased[0].message
        assert unreleased[0].severity == "warning"


class TestStaleDocs:
    def test_readme_pin_older_than_tag(self, tmp_path):
        repo = make_repo(
            tmp_path,
            readme="$ pip install demo==1.0.0\n",
        )
        findings = lint(str(repo))
        stale = [f for f in findings if f.rule == "stale-version-doc"]
        assert len(stale) == 1
        assert stale[0].line == 1

    def test_readme_pin_current_is_quiet(self, tmp_path):
        repo = make_repo(
            tmp_path,
            readme="$ pip install demo==1.2.3\n",
        )
        assert lint(str(repo)) == []

    def test_disable(self, tmp_path):
        repo = make_repo(
            tmp_path,
            manifest='[project]\nname = "demo"\nversion = "1.3.0"\n',
        )
        assert lint(str(repo), disabled=["version-tag-drift"]) == []


class TestCli:
    def run_cli(self, *args):
        import sys
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return subprocess.run(
            [sys.executable, "-m", "shipdrift", *args],
            capture_output=True, text=True, cwd=root,
        )

    def test_failing_repo_exits_one(self, tmp_path):
        repo = make_repo(
            tmp_path,
            manifest='[project]\nname = "demo"\nversion = "1.3.0"\n',
        )
        r = self.run_cli(str(repo))
        assert r.returncode == 1
        assert "version-tag-drift" in r.stdout

    def test_json_output(self, tmp_path):
        import json
        repo = make_repo(
            tmp_path,
            manifest='[project]\nname = "demo"\nversion = "1.3.0"\n',
        )
        r = self.run_cli(str(repo), "--format", "json")
        data = json.loads(r.stdout)
        assert data[0]["rule"] == "version-tag-drift"

    def test_list_checks(self):
        r = self.run_cli("--list-checks")
        assert r.returncode == 0
        assert "unreleased-commits" in r.stdout
