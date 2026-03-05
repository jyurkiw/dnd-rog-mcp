# test/

This directory contains test data and fixtures for `dnd-rog-mcp`.

## Contents

### `test_data_adventure.md`

The canonical test fixture for the project: *The Troubles of Shadowdale*, a complete Tier 1 D&D adventure decomposed into every node, relationship, encounter, boxed text sequence, rumor, fact, and timeline entry required to populate the database.

The document has two parts:

- **Part One — Narrative Description.** A plain-English writeup of the adventure. Sufficient to regenerate all node and entity data from scratch, and usable as a prompt to an agent to do so.
- **Part Two — Node & Entity Catalogue.** The full structured data for every node and relationship in the adventure, with uids, properties, and relationship definitions laid out explicitly.

This adventure is specifically designed to exercise every requirement category defined in `DESIGN.md`. The requirement coverage table at the end of the document maps each category to the specific nodes and relationships that test it.

## Test Strategy

Tests are written against the requirements defined in `DESIGN.md` following TDD principles. The adventure fixture drives both:

- **Unit tests** — tool handlers tested in isolation with a mocked Neo4j driver, using node data from the fixture as inputs and expected outputs.
- **Integration tests** — full tool call → DB write → DB read → assertion cycles against a live Neo4j test container, using the fixture as the seed dataset.

A correctly loaded fixture should produce a `get_narrative_flow` result that renders as a flowchart with a clear branch at the first player choice, two independent combat paths each with their own internal branches and merges, and a grand re-merge before the final pipe-dependent resolution. If that renders correctly, the graph engine is working.
