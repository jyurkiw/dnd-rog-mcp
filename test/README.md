# test/

This directory contains test data and fixtures for `dnd-rog-mcp`.

## Contents

### [test_data_adventure.md](test_data_adventure.md)

The canonical test fixture for the project: *The Troubles of Shadowdale*, a complete Tier 1 D&D adventure decomposed into every node, relationship, encounter, boxed text sequence, rumor, fact, and timeline entry required to populate the database.

The document has two parts:

- **Part One — Narrative Description.** A plain-English writeup of the adventure. Sufficient to regenerate all node and entity data from scratch, and usable as a prompt to an agent to do so.
- **Part Two — Node & Entity Catalogue.** The full structured data for every node and relationship in the adventure, with uids, properties, and relationship definitions laid out explicitly.

This adventure is specifically designed to exercise every requirement category defined in `DESIGN.md`. The requirement coverage table at the end of the document maps each category to the specific nodes and relationships that test it.

### [test_architecture.md](test_architecture.md)

Full specification of the testing architecture: dependency rationale, pytest configuration, custom report design, test naming conventions, marker definitions, six-phase execution order strategy, Neo4j fixture scopes, and Docker environment setup. Read this before writing new tests.

### `fixtures/shadowdale.py`

Builder functions that return raw dicts for every node and relationship in the Shadowdale adventure. Used directly in unit tests and assembled into the full NDJSON import payload for integration tests.

---

## Architecture Summary

Full details are in `test_architecture.md`. This is the short version.

### How the library is structured for testing

All business logic lives in `src/dnd_mcp/tools/` as plain functions that accept a Neo4j driver and arguments and return structured results. `server.py` does nothing but register those functions as MCP tools. Tests import from `tools/` directly — no MCP server is ever started.

### Dependencies

`pytest` for running and discovery, `unittest.mock` for mocking the Neo4j driver in unit tests, `assertpy` for fluent assertions, `testcontainers[neo4j]` for spinning up real Neo4j instances for integration tests, `pytest-timeout` for bounding container-dependent tests, and `pytest-order` for enforcing execution phases.

### Running the tests

```bash
docker compose -f docker-compose.test.yml up
```

That's it. The compose file waits for Neo4j to be healthy, runs the full suite with `--verbosity=3`, prints the report, and tears everything down. Exit code matches pytest's exit code.

### Six-phase execution order

| Phase | What runs | DB scope |
|---|---|---|
| 1 | Unit tests — all mocked, no DB | None |
| 2 | Integration: core CRUD | Fresh DB per module |
| 3 | Integration: import — loads the Shadowdale fixture | Fresh DB (session-scoped, persists for Phase 4 & 6) |
| 4 | Integration: read & query — narrative flow, NPC profiles, timeline, knowledge | Seeded DB from Phase 3 |
| 5 | Integration: soft delete — disable, undelete, true_delete, cascade | Fresh DB per test function |
| 6 | Integration: export & round-trip — export seeded DB, re-import, compare byte-for-byte | Seeded DB from Phase 3 |

Phase 3 does double duty: it tests the `import_database` function *and* seeds the database for Phases 4 and 6. If Phase 3 fails, those phases are skipped automatically.

### Test naming

All test functions are named `test_{CATEGORY}_{NUMBER}_{description}` where category and number match the requirement IDs in `DESIGN.md` — for example `test_GI_01_uid_uniqueness` or `test_SD_07_disable_respects_shared_node_protection`. This drives the custom report.

### Custom report

After the run, a `pytest_terminal_summary` hook prints a structured report grouped by requirement category showing pass rate as a progress bar and count. Categories with no tests written yet show as `0 / N` so coverage gaps are visible throughout TDD. Failures are listed individually below the summary table.
