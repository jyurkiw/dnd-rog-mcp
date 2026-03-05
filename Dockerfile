FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir -e .

ENV NEO4J_URI=bolt://neo4j:7687
ENV NEO4J_USER=neo4j
ENV NEO4J_PASSWORD=""
ENV NEO4J_DATABASE=dnd
ENV MCP_LOG_LEVEL=INFO
ENV ALLOW_TRUE_DELETE=false

CMD ["dnd-rog-mcp"]
