#!/usr/bin/env bash
# Runs the test suite and tears down all containers when done,
# preserving the original exit code from the test runner.

COMPOSE_FILE=docker-compose.test.yml

docker compose -f "$COMPOSE_FILE" up --abort-on-container-exit
EXIT_CODE=$?

docker compose -f "$COMPOSE_FILE" down

exit $EXIT_CODE
