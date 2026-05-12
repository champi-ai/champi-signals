# Phase 2: Enhanced EventProcessor

## Goal
`EventProcessor` supports class-level decoration and async context manager for imperative event emission.

## Deliverables

### Backend
- [ ] Implement `EventProcessor.emits_all_events(data=[...])` class decorator in `processors.py`
- [ ] Implement `EventProcessor.context(signal_manager, event_type, data)` async context manager
- [ ] Add tests for class-level decoration (happy path, skips dunders/private, respects Meta)
- [ ] Add tests for context manager (happy path, error path with re-raise)

### Frontend
- [ ] No new exports needed (methods added to existing `EventProcessor` class)
- [ ] Update docstrings for new methods

### Infrastructure
- [ ] None

## Done Definition
- `@EventProcessor.emits_all_events(data=['status'])` decorates all public methods of a class
- Private and dunder methods are skipped
- `async with EventProcessor.context(mgr, "reading", data={...})` emits START/FINISH or START/ERROR
- Error path re-raises the original exception
- Existing `@EventProcessor.emits_event` tests still pass (no regressions)

## Parallel work
- BE: class decorator and context manager can be developed in parallel by two developers

## Phase dependencies
- Requires: Phase 0 (CI pipeline)

## Complexity
- Backend: M
- Frontend: S
- Infra: S

## Risks
- `inspect.getmembers` behavior with async methods, properties, and classmethods needs careful testing
- Class decorator interaction with `__init_subclass__` in downstream inheritance chains
