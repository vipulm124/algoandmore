# Two-Phase Commit (2PC) in Python

A minimal, readable implementation of the Two-Phase Commit distributed transaction protocol in Python.

## What is Two-Phase Commit?

Two-Phase Commit (2PC) is a distributed transaction protocol that guarantees **atomicity** across multiple nodes — every participant either commits or every participant aborts. No partial updates.

```
Coordinator
    │
    ├──► Participant A  (DB-A)
    ├──► Participant B  (DB-B)
    └──► Participant C  (DB-C)
```

## Project Structure

```
.
├── coordinator.py            # Drives both phases, collects votes
├── participant.py            # Validates, prepares, commits, and aborts
├── unreliableparticipant.py  # Participant that always votes NO (for testing)
└── main.py                   # Demo: success, all-fail, and mixed-vote scenarios
```

## How It Works

### Phase 1 — Prepare

The coordinator sends `prepare(txn_id, data)` to every participant. Each participant:
1. Runs its validation logic (`_validate`)
2. If valid, writes `"prepared"` to its local transaction log and returns `True` (YES vote)
3. If invalid, returns `False` (NO vote) without writing anything

### Phase 2 — Commit or Abort

The coordinator checks all votes:
- **All YES** → sends `commit(txn_id)` to every participant → each flips status to `"committed"`
- **Any NO** → sends `abort(txn_id)` to every participant → each flips status to `"aborted"` (participants that successfully prepared must also roll back)

## Running the Demo

```bash
python main.py
```

The demo runs three scenarios:

**Scenario 1 — All participants agree (success)**
```python
coordinator.execute({"amount": 1000})
# DB-A, DB-B, DB-C all prepare and commit
```

**Scenario 2 — All participants reject (all-fail)**
```python
coordinator.execute({"amount": 0})
# amount=0 fails validation on all nodes → abort
```

**Scenario 3 — Mixed votes (partial prepare, then abort)**
```python
coordinator.register(Participant("DB-A"))            # votes YES
coordinator.register(Participant("DB-B"))            # votes YES
coordinator.register(UnreliableParticipant("DB-C"))  # votes NO

coordinator.execute({"amount": 100})
# DB-A and DB-B prepare successfully, DB-C rejects
# → coordinator aborts DB-A and DB-B (they had locked resources)
```

Scenario 3 is the most important one — it shows that a participant which already said YES and wrote to its log can still be rolled back by a NO vote from another node.

## Key Classes

### `Coordinator`

| Method | Description |
|---|---|
| `register(participant)` | Add a participant to the transaction group |
| `execute(data)` | Run a full 2PC transaction; returns `True` on commit, `False` on abort |

### `Participant`

| Method | Description |
|---|---|
| `prepare(txn_id, data)` | Validate and lock; write `"prepared"` to log if successful |
| `commit(txn_id)` | Apply the transaction; set status to `"committed"` |
| `abort(txn_id)` | Roll back; set status to `"aborted"` |
| `_validate(data)` | Override this with your own business logic |

### `UnreliableParticipant`

Subclass of `Participant` that overrides `_validate` to always return `False`. Useful for testing the abort path without depending on specific input data.

## Limitations

This implementation is intentionally minimal for learning purposes. Production 2PC systems also need:

- **Persistent write-ahead logging** — each node must survive crashes between phases
- **Coordinator recovery** — if the coordinator crashes after Phase 1, participants are blocked indefinitely
- **Timeouts** — participants waiting on a crashed coordinator need a way to unblock
- **Idempotent commit/abort** — retried messages must be safe to process multiple times

For production distributed transactions consider battle-tested systems built on Raft or Paxos (etcd, ZooKeeper), or the Saga pattern for long-running workflows.

