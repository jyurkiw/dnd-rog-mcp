# dnd-mcp

A purpose-specific MCP (Model Context Protocol) server for developing D&D adventures and supplements, backed by a Neo4j graph database.

## Overview

`dnd-mcp` provides a structured knowledgebase for adventure writing, designed to be used with tool-enabled AI agents as part of a RAG (Retrieval-Augmented Generation) workflow. The database stores the *relationships* between narrative elements — NPCs, locations, plotlines, events, choices, and more — so that an agent can help brainstorm, plan, and validate prose.

The intended workflow is:

```
Brainstorm/Plan → Human writes prose → Agent validates prose against knowledgebase
```

The database drives prose creation. Prose files are outputs, not inputs.

## Stack

- **MCP Server**: Python (stdio transport)
- **Database**: Neo4j (Bolt protocol)
- **Runtime**: Docker / Docker Compose
- **Configuration**: Environment variables

## Features

- Three-tier entity hierarchy: Global → Context → Adventure
- Full narrative flow graph: Events, Choices, Outcomes with branching and merging
- Boxed text sequencing with conditional, stateful multi-part narrative moments
- Soft delete with cascade, undelete, and optional hard delete
- Self-contained import/export (NDJSON with inlined file content)
- Low-verbosity tool outputs designed for small context-window agents

## Design

Full design documentation is in [DESIGN.md](./DESIGN.md).

## Quick Start

```bash
cp .env.example .env
# edit .env with your credentials
docker compose up
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEO4J_URI` | `bolt://neo4j:7687` | Neo4j Bolt connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | — | Neo4j password (required) |
| `NEO4J_DATABASE` | `dnd` | Neo4j database name |
| `MCP_LOG_LEVEL` | `INFO` | Server log level |
| `ALLOW_TRUE_DELETE` | `false` | Enable permanent destructive deletes |

## Project Status

🚧 In design phase. Implementation has not begun.
