# Phase 1: IPC Bridge Interface

## Goal
`SignalBridgeABC` is implemented, tested, and exported so champi-ipc can depend on it.

## Deliverables

### Backend
- [ ] Implement `SignalBridgeABC` in `bridges.py` with `connect`, `disconnect`, `start`, `stop`, and `is_connected` property
- [ ] Write `tests/test_bridges.py` with concrete stub that records calls
- [ ] Test async `start`/`stop` lifecycle
- [ ] Test `is_connected` property behavior

### Frontend
- [ ] Export `SignalBridgeABC` from `__init__.py`
- [ ] Add type stub coverage in `py.typed`

### Infrastructure
- [ ] None

## Done Definition
- `from champi_signals import SignalBridgeABC` works
- A concrete subclass can be instantiated, connected to a `BaseSignalManager`, started, and stopped
- `is_connected` returns correct state before/after connect/disconnect
- 100% line coverage on `bridges.py`

## Parallel work
- BE: bridges implementation can run alongside FE: __init__.py export updates (merge at end)

## Phase dependencies
- Requires: Phase 0 (CI pipeline with coverage gate)

## Complexity
- Backend: S
- Frontend: S
- Infra: S

## Risks
- ABC design may need revision once champi-ipc starts implementing it; keep interface minimal
