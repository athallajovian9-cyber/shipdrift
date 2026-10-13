# Contributing to shipdrift

Start with [CONTRIBUTORS.md](CONTRIBUTORS.md) — it holds the credit policy
(your PR keeps your authorship; `Co-authored-by` trailers survive squashes;
no CLA) and the full "how to land a rule" flow.

The short version:

1. **Issue first.** Describe the incident: what broke, on which platform,
   in which project. Rules that fire outside shell/build files need
   discussion before code — false positives are worse than missed
   detections.
2. **One function + one test.** Rules live in `shipdrift/rules.py`,
   register in `RULES`, one line in `RULE_DOCS`, and tests must cover both
   the triggering sample and the clean sample.
3. **Keep the baseline green.** `python -m pytest tests/` must pass and
   `shipdrift .` must stay 0/0 on this repository.

## Development

```console
$ python -m pytest tests/          # run the suite
$ python -m shipdrift .            # self-lint (must stay 0/0)
$ python -m shipdrift --list-rules # what exists today
```

No dependencies to build — Python 3.9+ standard library only. The npm
package (`npm/`) is a launcher over the same Python core; change Python
code, not the shim.

## Releases

PyPI and npm publish the same version from the same commit: `uv build` for
the wheel/sdist, `npm pack` (auto-syncs `lib/`) for the tarball.
