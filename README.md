# shipdrift

**Did you release what you merged?**

Commits pile up on `main` while the registry keeps serving the last tag.
The README on `main` describes features the released package does not
have. Someone bumps the version and forgets the tag, or tags and forgets
the bump. shipdrift reads the git history and the manifests and tells you
which of those happened — before a user finds out for you.

```console
$ shipdrift
README.md:12: warning: [stale-version-doc] README pins 1.0.0 but the latest release is 1.2.3: fresh installs get an old build.
pyproject.toml:3: error: [version-tag-drift] manifest is at 1.3.0 but the latest release tag is v1.2.3: the bump (and everything merged with it) is unreleased.
.: warning: [unreleased-commits] 7 commit(s) on main since tag v1.2.3 (newest: "fix: proxy reconnect loop") have no release.
shipdrift: 1 error(s), 2 warning(s)
```

## Why

Every check exists because it happened to a real project:

| check | real incident |
|---|---|
| `version-tag-drift` | a fix sat merged on `main` for months because the version was never released — the README on `main` documented behavior the installed package did not have (bttf #19) |
| `unreleased-commits` | merges land daily; the tag does not. Users on the registry never see them. |
| `stale-version-doc` | install examples pin `==x.y.z` forever; readers get an old build with a smile |

Pure git + file reads. **No network, no dependencies, Python 3.9+.**

## Install

```console
$ pip install shipdrift        # PyPI
$ npm install -g shipdrift     # npm (same Python core via a Node launcher)
```

From source:

```console
$ pip install git+https://github.com/athallajovian9-cyber/shipdrift
$ python -m shipdrift path/to/repo
```

## Usage

```console
$ shipdrift --list-checks
version-tag-drift    [error  ] manifest version vs latest git tag
unreleased-commits   [warning] commits on the branch with no tag cut since
stale-version-doc    [warning] README install examples pinning old versions

$ shipdrift . --format json      # machine-readable
$ shipdrift --fail-on warning .  # CI-strict: warnings fail too
$ shipdrift --disable stale-version-doc .
```

Exit code `1` when findings reach `--fail-on` (default `error`).

## Contributing

Issue first, then one check function + one test. See
[CONTRIBUTORS.md](CONTRIBUTORS.md) for the credit policy and
[CONTRIBUTING.md](CONTRIBUTING.md) for the flow. Checks must stay hermetic:
temp git repos only, no network.

## License

MIT
