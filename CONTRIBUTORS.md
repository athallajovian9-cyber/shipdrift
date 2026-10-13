# Contributors

shipdrift exists because a group of open-source projects let us learn their
Windows failures the hard way — every rule in this tool is a scar borrowed
from someone else's CI. This file is the ledger.

## Credit policy

- **Your PR, your authorship.** A merged pull request keeps you as the
  commit author. If a change is squashed or re-wrapped, the
  `Co-authored-by:` trailer is preserved — nobody disappears from the
  contributors list because a maintainer pressed merge.
- **Your rule, your name.** Rules carry the story of the incident that
  created them. If you brought the incident, the README table says so.
- No CLA, no assignment, no copyright handover. MIT stays MIT.

## How to land a rule

1. Open an issue describing the incident (what broke, on which platform).
   False positives are worse than missed detections — we discuss first.
2. One function in `shipdrift/rules.py`, registered in `RULES`, one line in
   `RULE_DOCS`, tests for both the triggering and the clean sample.
3. PR against `main`. CI must stay green; `shipdrift` self-lint stays 0/0.

## Ledger

| contributor | what landed |
|---|---|
| [athallajovian9-cyber](https://github.com/athallajovian9-cyber) | initial release: engine, release-drift checks, CLI, docs |

(append yourself with your merged PR — the list is generated from `git log`
by whoever cuts the next release, so being in the commits is enough.)
