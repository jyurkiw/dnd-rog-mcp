"""Neo4j driver setup and connection management."""

import os
from neo4j import GraphDatabase, Driver


def get_driver() -> Driver:
    uri = os.environ["NEO4J_URI"]
    user = os.environ["NEO4J_USER"]
    password = os.environ["NEO4J_PASSWORD"]
    return GraphDatabase.driver(uri, auth=(user, password))


def get_database() -> str:
    return os.environ.get("NEO4J_DATABASE", "neo4j")
