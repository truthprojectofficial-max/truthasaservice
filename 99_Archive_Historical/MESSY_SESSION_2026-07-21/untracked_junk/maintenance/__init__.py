"""
Order Get It Right -- Deterministic Maintenance Layer
====================================================

A pure-Python, no-LLM, no-network maintenance subsystem that runs the
operator's routine checks on a schedule: chain integrity, journal-tail
durability, vault growth, disk usage, Squeal backlog, and the full
MonitorAgent briefing.

Design rules (inherited from the rest of the engine):

* **Deterministic.** Every routine is a pure function. Same state on
  disk -> same report, every time. No LLM, no network, no randomness.
* **Read-only on history.** Routines only READ the vault / journals /
  logs. They never edit a verdict, never delete a block, never mutate
  the vault. The only write they perform is a single sealed
  ``MAINTENANCE_*`` block per run (and, on a fault, a fault file in the
  Squeal directory). The chain is the source of truth; this layer
  observes it.
* **Idempotent within a cadence.** Running the same cadence twice in a
  row produces the same deltas (the state file is the comparison
  anchor), so a crashed-and-restarted run does not double-seal.
* **Sealed.** Every run seals a block, so an auditor can prove the
  maintenance actually fired and see what it found.

Public entry points
-------------------
* ``health.run_routine(name)`` -- run one routine by name.
* ``reporter.run_suite(cadence)`` -- run a cadence's routines, write the
  report, seal the block, return the report dict.
* ``scheduler.main()`` -- CLI driver (``--once`` / ``--loop``).

Usage
-----
::

    # one-off (run the daily set right now)
    python -m src.maintenance.scheduler --once --cadence daily

    # loop forever, firing the hourly set every 3600 s
    python -m src.maintenance.scheduler --loop --interval 3600 --cadence hourly
"""