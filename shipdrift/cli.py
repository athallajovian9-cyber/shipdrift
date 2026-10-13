"""shipdrift command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Sequence

from .checks import CHECK_DOCS, CHECKS
from .engine import lint

__version__ = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="shipdrift",
        description="Did you release what you merged? Finds merges with no "
        "tag, version bumps with no release, and docs pinning old builds.",
    )
    p.add_argument("repo", nargs="?", default=".",
                   help="path to a git repository (default: .)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.add_argument("--disable", default="",
                   help="comma-separated check ids to disable")
    p.add_argument("--fail-on", choices=("error", "warning", "never"),
                   default="error")
    p.add_argument("--list-checks", action="store_true")
    p.add_argument("--version", action="version",
                   version=f"shipdrift {__version__}")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_checks:
        for check_id, doc in CHECK_DOCS.items():
            print(f"{check_id:18} [{CHECKS[check_id][1]:7}] {doc}")
        return 0

    disabled = [c for c in args.disable.split(",") if c]
    findings = lint(args.repo, disabled)

    if args.format == "json":
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    else:
        for f in findings:
            print(f.as_text())
        if findings:
            errors = sum(1 for f in findings if f.severity == "error")
            print(f"shipdrift: {errors} error(s), "
                  f"{len(findings) - errors} warning(s)", file=sys.stderr)

    if args.fail_on == "never" or not findings:
        return 0
    if args.fail_on == "warning":
        return 1
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
