# Phase 3: Enum Expansion and Documentation

## Goal
`ImgUIEventTypes` and `make_event_types()` are available, mkdocs site is live, and v0.2.0 is ready to release.

## Deliverables

### Backend
- [ ] Add `ImgUIEventTypes` IntEnum to `enums.py` (values starting at 100)
- [ ] Implement `make_event_types(name, spec)` factory function in `enums.py`
- [ ] Add tests for `ImgUIEventTypes` values and membership
- [ ] Add tests for `make_event_types` (generates correct enum members and values)

### Frontend
- [ ] Export `ImgUIEventTypes` and `make_event_types` from `__init__.py`
- [ ] Write mkdocs content: Getting Started, API Reference, Integration Guide, Changelog
- [ ] Add `mkdocs.yml` configuration

### Infrastructure
- [ ] Verify `docs.yml` deploys mkdocs site to GitHub Pages
- [ ] Verify `release.yml` publishes to PyPI on `v0.2.0` tag
- [ ] Run `cz bump` to create v0.2.0 tag and changelog

## Done Definition
- `from champi_signals import ImgUIEventTypes, make_event_types` works
- `ImgUIEventTypes.TOOL_CALL_START == 100`
- `make_event_types("X", {"A": ["B"]})` returns an IntEnum with member `A_B`
- mkdocs site builds without warnings and includes all public API symbols
- v0.2.0 tag triggers successful PyPI publish (or dry-run passes)
- Overall test coverage >= 90%

## Parallel work
- BE: enum implementation can run alongside FE: mkdocs content writing

## Phase dependencies
- Requires: Phase 1 (SignalBridgeABC must be documented), Phase 2 (EventProcessor enhancements must be documented)

## Complexity
- Backend: S
- Frontend: M
- Infra: S

## Risks
- mkdocs-material + mkdocstrings-python version compatibility
- PyPI trusted publisher OIDC first-time setup may require manual intervention
