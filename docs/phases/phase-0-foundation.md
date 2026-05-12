# Phase 0: Foundation

## Goal
CI pipeline enforces quality gates and the repo is ready for feature development on a dedicated branch.

## Deliverables

### Backend
- [ ] Create `src/champi_signals/bridges.py` module stub (empty file with docstring)
- [ ] Verify existing tests pass on Python 3.12

### Frontend
- [ ] Confirm all existing public exports are tested and documented in `__init__.py`

### Infrastructure
- [ ] Add `release.yml` workflow (trigger on `v*` tag, `uv build` + `uv publish` via trusted publisher)
- [ ] Add `docs.yml` workflow (build mkdocs on push to main, deploy to GitHub Pages)
- [ ] Add docs dev-dependency group to `pyproject.toml`
- [ ] Configure coverage enforcement (`--cov-fail-under=90`) in CI

## Done Definition
- `ci.yml` runs lint + test + coverage gate on every PR
- `release.yml` exists and is syntactically valid (dry-run with `act` or manual inspection)
- `docs.yml` exists and builds mkdocs locally without errors
- All existing tests pass with >= 90% coverage

## Parallel work
- BE: stub bridges.py can run alongside Infra: CI workflow additions

## Phase dependencies
- Requires: none

## Complexity
- Backend: S
- Frontend: S
- Infra: M

## Risks
- PyPI trusted publisher OIDC setup requires manual configuration on pypi.org (cannot be automated in CI alone)
