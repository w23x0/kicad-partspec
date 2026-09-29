# Releasing to PyPI

The release workflow (`.github/workflows/release.yml`) uses PyPI Trusted Publishing, so no API token is stored. It is
inert until the steps below are done. A published version cannot be replaced or re-uploaded, only superseded, so try
TestPyPI first.

## One-time setup (needs your PyPI and GitHub accounts)

1. **PyPI**: sign in, then Account settings, Publishing, "Add a new pending publisher":
   - PyPI project name: `kicad-partspec`
   - Owner: `w23x0`, repository: `kicad-partspec`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
2. **TestPyPI** (separate account and site, `test.pypi.org`): the same, with environment name `testpypi`.
3. **GitHub**: repository Settings, Environments, create `pypi` and `testpypi`. Adding yourself as a required reviewer on
   `pypi` gives a manual approval step before anything is published.

Only `kicad-partspec` is registered. `kicad-partspec-mcp` is a command inside it, not a separate project.

## Each release

1. Set `version` in `pyproject.toml` and `__version__` in `src/kicad_partspec/__init__.py` (a test keeps them equal).
2. Merge to `main` with CI green.
3. Rehearse: Actions, Release, "Run workflow", target `testpypi`. Check the project page on test.pypi.org and install it:
   `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kicad-partspec`
4. Publish: `git tag vX.Y.Z && git push origin vX.Y.Z`. The workflow refuses a tag that differs from the package version.

The first successful publish creates the project and claims the name.

## What the wheel does not contain

The skill and plugin manifests are distributed through the repository, not the wheel.
