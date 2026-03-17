"""Tool handlers: file references and content serving."""

import os
from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.models.nodes import FileRef


def _err(code, reason):
    return {"error": f"{code}: {reason}"}

def _ok(uid):
    return {"uid": uid, "status": "ok"}

def _response(props):
    return {k: v for k, v in props.items() if v is not None and v != []}


def add_file_reference(driver, uid, path, entity_uid, source_adventure=None,
                        file_type=None, description=None):
    """
    Create a FileRef node and link it to an entity via HAS_FILE.
    GI-10: a FileRef path must be unique within the database.
    """
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")
    if not queries.node_exists(driver, entity_uid):
        return _err("NOT_FOUND", f"entity '{entity_uid}' not found")

    # GI-10: enforce unique path
    from dnd_mcp.db.connection import get_database
    db = get_database()
    with driver.session(database=db) as session:
        result = session.run(
            "MATCH (f:FileRef {path: $path}) RETURN count(f) AS c", path=path
        )
        if result.single()["c"] > 0:
            return _err("DUPLICATE_PATH", f"a FileRef with path '{path}' already exists")

    node = FileRef(uid=uid, path=path, file_type=file_type, description=description,
                    associated_entity_uid=entity_uid, source_adventure=source_adventure)
    queries.create_node(driver, "FileRef", node.to_props())
    queries.create_relationship(driver, entity_uid, uid, "HAS_FILE")
    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")
    return _ok(uid)


def serve_file_content(driver, uid):
    """
    Return the content of a file referenced by a FileRef node.
    MP-06: must return a plaintext content block.
    """
    props = queries.get_node_by_label(driver, "FileRef", uid)
    if props is None:
        return _err("NOT_FOUND", f"FileRef '{uid}' not found")

    path = props.get("path")
    if not path:
        return _err("NO_PATH", "FileRef has no path property")

    if not os.path.exists(path):
        return _err("FILE_NOT_FOUND", f"file '{path}' does not exist on disk")

    try:
        content = open(path, encoding="utf-8").read()
    except Exception as e:
        return _err("READ_ERROR", str(e))

    return {"uid": uid, "path": path, "content": content}
