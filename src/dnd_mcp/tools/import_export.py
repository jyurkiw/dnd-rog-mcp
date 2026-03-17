"""Tool handlers: import and export."""

import json
import base64
import os
from datetime import datetime, timezone
from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.db.connection import get_database

SCHEMA_VERSION = 1


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _err(code, reason):
    return {"error": f"{code}: {reason}"}


# ── Export ────────────────────────────────────────────────────────────────────

def export_full_database(driver, include_files=True):
    """
    IE-01..IE-04, IE-09: serialize all nodes, relationships, and files to NDJSON lines.
    Returns a list of dicts (one per NDJSON line).
    """
    db = get_database()
    lines = []

    with driver.session(database=db) as session:
        # Nodes
        nodes_result = session.run("MATCH (n) RETURN properties(n) AS props, labels(n) AS labels")
        nodes = []
        for r in nodes_result:
            props = dict(r["props"])
            labels = [l for l in r["labels"] if l not in ("BaseNode",)]
            label = labels[0] if labels else "Unknown"
            nodes.append({"type": "node", "label": label, "uid": props["uid"],
                          "tier": props.get("tier", "unknown"), "properties": props})

        # Relationships
        rels_result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN a.uid AS from_uid, b.uid AS to_uid,
                   type(r) AS rel_type, properties(r) AS props
        """)
        rels = []
        for r in rels_result:
            rels.append({"type": "relationship", "rel_type": r["rel_type"],
                          "from_uid": r["from_uid"], "to_uid": r["to_uid"],
                          "properties": dict(r["props"])})

        # FileRefs with inlined content
        file_lines = []
        if include_files:
            filerefs = session.run("MATCH (f:FileRef) RETURN properties(f) AS props")
            for r in filerefs:
                props = dict(r["props"])
                path = props.get("path", "")
                if path and os.path.exists(path):
                    try:
                        raw = open(path, "rb").read()
                        try:
                            content = raw.decode("utf-8")
                            encoding = "utf-8"
                        except UnicodeDecodeError:
                            content = base64.b64encode(raw).decode("ascii")
                            encoding = "base64"
                        file_lines.append({"type": "file", "path": path,
                                            "content": content, "encoding": encoding})
                    except Exception:
                        pass

    meta = {
        "type": "meta",
        "schema_version": SCHEMA_VERSION,
        "exported_at": _now(),
        "node_count": len(nodes),
        "rel_count": len(rels),
    }
    lines = [meta] + nodes + rels + file_lines
    return lines


def export_adventure(driver, adventure_uid, include_files=True):
    """
    IE-08: include the Adventure node, all adventure-scoped nodes, all Context nodes,
    all referenced Global nodes (flagged read_only=True), and all FileRefs.
    """
    if not queries.node_exists(driver, adventure_uid):
        return _err("NOT_FOUND", f"adventure '{adventure_uid}' not found")

    db = get_database()
    with driver.session(database=db) as session:
        # Adventure node + all BELONGS_TO / WITHIN_ADVENTURE nodes
        scoped_result = session.run("""
            MATCH (adv {uid: $uid})
            OPTIONAL MATCH (n)-[:BELONGS_TO|WITHIN_ADVENTURE]->(adv)
            WITH collect(adv) + collect(n) AS all_nodes
            UNWIND all_nodes AS node
            RETURN DISTINCT properties(node) AS props, labels(node) AS labels
        """, uid=adventure_uid)

        nodes = []
        scoped_uids = set()
        for r in scoped_result:
            props = dict(r["props"])
            labels = [l for l in r["labels"] if l not in ("BaseNode",)]
            label = labels[0] if labels else "Unknown"
            nodes.append({"type": "node", "label": label, "uid": props["uid"],
                          "tier": props.get("tier"), "properties": props})
            scoped_uids.add(props["uid"])

        # Global nodes referenced by Context nodes in this adventure
        global_result = session.run("""
            MATCH (ctx:NPCContext)-[:WITHIN_ADVENTURE]->(adv {uid: $uid})
            MATCH (g)-[:REPRESENTED_BY]->(ctx)
            RETURN DISTINCT properties(g) AS props, labels(g) AS labels
        """, uid=adventure_uid)
        for r in global_result:
            props = dict(r["props"])
            if props["uid"] not in scoped_uids:
                labels = [l for l in r["labels"] if l not in ("BaseNode",)]
                label = labels[0] if labels else "Unknown"
                nodes.append({"type": "node", "label": label, "uid": props["uid"],
                              "tier": props.get("tier"), "read_only": True, "properties": props})
                scoped_uids.add(props["uid"])

        all_uids = list(scoped_uids)

        # Relationships between nodes in this export
        rels_result = session.run("""
            MATCH (a)-[r]->(b)
            WHERE a.uid IN $uids AND b.uid IN $uids
            RETURN a.uid AS from_uid, b.uid AS to_uid,
                   type(r) AS rel_type, properties(r) AS props
        """, uids=all_uids)
        rels = [{"type": "relationship", "rel_type": r["rel_type"],
                  "from_uid": r["from_uid"], "to_uid": r["to_uid"],
                  "properties": dict(r["props"])} for r in rels_result]

        # Files
        file_lines = []
        if include_files:
            filerefs_result = session.run("""
                MATCH (f:FileRef) WHERE f.uid IN $uids
                RETURN properties(f) AS props
            """, uids=all_uids)
            for r in filerefs_result:
                props = dict(r["props"])
                path = props.get("path", "")
                if path and os.path.exists(path):
                    try:
                        raw = open(path, "rb").read()
                        try:
                            content = raw.decode("utf-8")
                            encoding = "utf-8"
                        except UnicodeDecodeError:
                            content = base64.b64encode(raw).decode("ascii")
                            encoding = "base64"
                        file_lines.append({"type": "file", "path": path,
                                            "content": content, "encoding": encoding})
                    except Exception:
                        pass

    meta = {"type": "meta", "schema_version": SCHEMA_VERSION, "exported_at": _now(),
            "node_count": len(nodes), "rel_count": len(rels)}
    return [meta] + nodes + rels + file_lines


# ── Import ────────────────────────────────────────────────────────────────────

def import_database(driver, lines):
    """
    IE-05..IE-07: import from NDJSON line list.
    Pre-flight: hard-fail if DB is not empty.
    Transactional: all or nothing.
    """
    # IE-07: validate schema version
    if not lines:
        return _err("EMPTY_IMPORT", "import data is empty")

    meta = lines[0]
    if meta.get("type") != "meta":
        return _err("MISSING_META", "first line must be a meta record")
    if meta.get("schema_version") != SCHEMA_VERSION:
        return _err("SCHEMA_MISMATCH",
                    f"expected schema_version {SCHEMA_VERSION}, got {meta.get('schema_version')}")

    # IE-05: pre-flight node count check
    count = queries.count_all_nodes(driver)
    if count > 0:
        return _err("DB_NOT_EMPTY",
                    f"database contains {count} nodes; import only allowed on an empty database")

    nodes = [l for l in lines if l.get("type") == "node"]
    rels = [l for l in lines if l.get("type") == "relationship"]
    files = [l for l in lines if l.get("type") == "file"]

    db = get_database()
    try:
        with driver.session(database=db) as session:
            with session.begin_transaction() as tx:
                # Import nodes
                for node in nodes:
                    label = node["label"]
                    props = node["properties"]
                    tx.run(f"CREATE (n:{label} $props)", props=props)

                # Import relationships
                for rel in rels:
                    rel_type = rel["rel_type"]
                    tx.run(f"""
                        MATCH (a {{uid: $from_uid}}), (b {{uid: $to_uid}})
                        CREATE (a)-[r:{rel_type} $props]->(b)
                    """, from_uid=rel["from_uid"], to_uid=rel["to_uid"],
                           props=rel.get("properties", {}))

                tx.commit()

        # Write files to disk
        for file_entry in files:
            path = file_entry["path"]
            content = file_entry["content"]
            encoding = file_entry.get("encoding", "utf-8")
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            if encoding == "base64":
                open(path, "wb").write(base64.b64decode(content))
            else:
                open(path, "w", encoding="utf-8").write(content)

    except Exception as e:
        return _err("IMPORT_FAILED", str(e))

    return {
        "status": "ok",
        "nodes_imported": len(nodes),
        "relationships_imported": len(rels),
        "files_written": len(files),
    }


def list_files_in_export(lines):
    """
    IE-10: list files in an export without importing.
    Operates on raw NDJSON line list.
    """
    return [
        {"path": l["path"], "encoding": l.get("encoding", "utf-8")}
        for l in lines if l.get("type") == "file"
    ]
