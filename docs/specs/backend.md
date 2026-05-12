# champi-signals v0.2.0 — Implementation Spec

## Overview

This spec defines the **internal implementation** for champi-signals v0.2.0: module structure, class internals, signal dispatch model, async patterns, packaging automation, and CI/CD.

Current version: **0.1.0** (stable, released on PyPI).  
Target version: **0.2.0** (this spec).

---

## Section 1 — Module Structure

### Current (v0.1.0)
```
src/champi_signals/
├── __init__.py
├── managers.py      # SignalManagerABC, BaseSignalManager
├── processors.py    # EventProcessor
├── enums.py         # STTEventTypes, TTSEventTypes, EnumSetup
└── py.typed
```

### Target (v0.2.0) — additions only
```
src/champi_signals/
├── __init__.py          # add new exports
├── managers.py          # unchanged
├── processors.py        # add class-level decorator + context manager
├── enums.py             # add ImgUIEventTypes, make_event_types()
├── bridges.py           # NEW: SignalBridgeABC
└── py.typed
```

---

## Section 2 — `SignalBridgeABC` Implementation (bridges.py)

```python
from abc import ABC, abstractmethod
from champi_signals.managers import BaseSignalManager

class SignalBridgeABC(ABC):
    _manager: BaseSignalManager | None = None

    @abstractmethod
    def connect(self, signal_manager: BaseSignalManager) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @property
    def is_connected(self) -> bool:
        return self._manager is not None
```

**Testing**: Unit tests in `tests/test_bridges.py` using a concrete stub that records calls.

---

## Section 3 — Enhanced `EventProcessor` (processors.py)

### 3.1 Class-level decorator `emits_all_events`

Implementation strategy:
1. In `__init_subclass__` or via a class decorator, iterate `inspect.getmembers(cls, predicate=inspect.isfunction)`
2. Skip dunder methods, `Meta`, and private names
3. Apply `emits_event` to each remaining method using the class-level `data` param

```python
@classmethod
def emits_all_events(cls, data: list[str] | None = None):
    def decorator(klass):
        for name, method in inspect.getmembers(klass, predicate=inspect.isfunction):
            if not name.startswith('_') and name != 'Meta':
                setattr(klass, name, cls.emits_event(data=data or [])(method))
        return klass
    return decorator
```

### 3.2 Context manager `EventProcessor.context`

```python
from contextlib import asynccontextmanager

@staticmethod
@asynccontextmanager
async def context(signal_manager, event_type: str, data: dict | None = None):
    signal_manager.emit(f"{event_type}_START", data=data)
    try:
        yield
        signal_manager.emit(f"{event_type}_FINISH", data=data)
    except Exception as e:
        signal_manager.emit(f"{event_type}_ERROR", error=str(e), data=data)
        raise
```

**Testing**: Add tests to `tests/test_processors.py` covering class decoration and context manager happy + error paths.

---

## Section 4 — Enum Additions (enums.py)

### 4.1 `ImgUIEventTypes`
Add alongside existing `STTEventTypes` and `TTSEventTypes`. Values start at 100 to avoid collision.

### 4.2 `make_event_types(name, spec)` factory
Replacement for `EnumSetup.setup_service_enums` with a cleaner functional interface:

```python
def make_event_types(name: str, spec: dict[str, list[str]]) -> type[IntEnum]:
    members: dict[str, int] = {}
    counter = 0
    for group, suffixes in spec.items():
        for suffix in suffixes:
            members[f"{group}_{suffix}"] = counter
            counter += 1
    return IntEnum(name, members)  # type: ignore[return-value]
```

`EnumSetup` kept for backward compatibility; `make_event_types` is the recommended API going forward.

---

## Section 5 — PyPI Publishing Automation

### 5.1 Trusted Publisher setup
- Register champi-signals on PyPI as a trusted publisher (GitHub Actions OIDC)
- Workflow: `.github/workflows/release.yml` — triggers on `v*.*.*` tags
- Steps: `uv build` → `uv publish` (no API token stored in secrets)

### 5.2 Version bump workflow
- `cz bump` creates tag + updates CHANGELOG
- CI picks up tag, builds wheel + sdist, publishes to PyPI

---

## Section 6 — Documentation Site

### Stack
- mkdocs-material ≥ 9.5
- mkdocstrings-python (griffe backend)
- Deployed to GitHub Pages via `.github/workflows/docs.yml` on push to main

### `mkdocs.yml` outline
```yaml
site_name: champi-signals
theme:
  name: material
plugins:
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
nav:
  - Home: index.md
  - API Reference: api/
  - Integration Guide: integration.md
  - Changelog: changelog.md
```

---

## Section 7 — Test Coverage Requirements

| Module | Current | Target |
|---|---|---|
| managers.py | ✅ covered | maintain |
| processors.py | ✅ covered | add class-deco + context tests |
| enums.py | ✅ covered | add ImgUIEventTypes + make_event_types |
| bridges.py | ❌ new | 100% lines |

Minimum overall coverage: **90%** (enforced in CI via `--cov-fail-under=90`).

---

## Section 8 — CI/CD

Existing: `ci.yml` (lint + test on push/PR).

Add:
- `release.yml`: builds + publishes to PyPI on version tag
- `docs.yml`: builds + deploys mkdocs site on push to main

---

## Section 9 — Dependencies

No new runtime dependencies. Dev dependencies to add:

```toml
[dependency-groups]
docs = [
    "mkdocs-material>=9.5",
    "mkdocstrings-python>=1.8",
]
```

---

## Section 10 — Milestones / Phase Breakdown (input for plan-mvp)

| Phase | Deliverable |
|---|---|
| Phase 1: IPC Bridge Interface | `SignalBridgeABC` in bridges.py, full tests, exported in __init__ |
| Phase 2: Enhanced EventProcessor | class-level decorator + async context manager, full tests |
| Phase 3: Enum Expansion | `ImgUIEventTypes`, `make_event_types()`, full tests |
| Phase 4: Packaging & Docs | PyPI trusted-publisher workflow, mkdocs site, docs CI |
