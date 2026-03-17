"""Low-level Cypher helpers. All DB I/O flows through here."""

from datetime import datetime, timezone
from typing import Optional
from neo4j import Driver

from dnd_mcp.db.connection import get_database


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _strip_empty(props: dict) -> dict:
    """Remove None values and empty lists before storing."""
    return {k: v for k, v in props.items() if v is not None and v != []}


# ── Node operations ───────────────────────────────────────────────────────────

def create_node(driver: Driver, label: str, props: dict) -> dict:
    """
    Create a node with the given label and properties.
    Returns the created node's properties.
    """
    db = get_database()
    clean = _strip_empty(props)
    clean.setdefault("created_at", _now())
    clean.setdefault("updated_at", _now())
    clean.setdefault("disabled", False)
    clean.setdefault("disabled_by", [])

    with driver.session(database=db) as session:
        result = session.run(
            f"CREATE (n:{label} $props) RETURN properties(n) AS p",
            props=clean,
        )
        record = result.single()
        if record is None:
            raise RuntimeError(f"Failed to create {label} node with uid={props.get('uid')}")
        return dict(record["p"])


def get_node(driver: Driver, uid: str, include_disabled: bool = False) -> Optional[dict]:
    """Fetch a single node by uid. Returns None if not found."""
    db = get_database()
    where = "" if include_disabled else "AND n.disabled = false"
    with driver.session(database=db) as session:
        result = session.run(
            f"MATCH (n {{uid: $uid}}) WHERE n.uid = $uid {where} RETURN properties(n) AS p",
            uid=uid,
        )
        record = result.single()
        return dict(record["p"]) if record else None


def get_node_by_label(
    driver: Driver, label: str, uid: str, include_disabled: bool = False
) -> Optional[dict]:
    """Fetch a node by label + uid."""
    db = get_database()
    where = "" if include_disabled else "AND n.disabled = false"
    with driver.session(database=db) as session:
        result = session.run(
            f"MATCH (n:{label} {{uid: $uid}}) WHERE true {where} RETURN properties(n) AS p",
            uid=uid,
        )
        record = result.single()
        return dict(record["p"]) if record else None


def update_node(driver: Driver, uid: str, updates: dict) -> Optional[dict]:
    """
    Merge property updates onto an existing node.
    Returns updated node properties, or None if not found.
    """
    db = get_database()
    clean = _strip_empty(updates)
    clean["updated_at"] = _now()
    with driver.session(database=db) as session:
        result = session.run(
            "MATCH (n {uid: $uid}) SET n += $updates RETURN properties(n) AS p",
            uid=uid,
            updates=clean,
        )
        record = result.single()
        return dict(record["p"]) if record else None


def list_nodes(
    driver: Driver,
    label: str,
    filters: Optional[dict] = None,
    include_disabled: bool = False,
    verbose: bool = False,
) -> list:
    """
    List nodes of a given label.
    filters: extra equality conditions (e.g. {"source_adventure": "uid-123"}).
    Returns list of uids by default; full property dicts when verbose=True.
    """
    db = get_database()
    where_parts = ["true"]
    if not include_disabled:
        where_parts.append("n.disabled = false")
    params: dict = {}
    if filters:
        for k, v in filters.items():
            where_parts.append(f"n.{k} = ${k}")
            params[k] = v

    where_clause = " AND ".join(where_parts)
    return_clause = "properties(n) AS p" if verbose else "n.uid AS uid"

    with driver.session(database=db) as session:
        result = session.run(
            f"MATCH (n:{label}) WHERE {where_clause} RETURN {return_clause} ORDER BY n.created_at",
            **params,
        )
        if verbose:
            return [dict(r["p"]) for r in result]
        else:
            return [r["uid"] for r in result]


def node_exists(driver: Driver, uid: str) -> bool:
    """Return True if any node with this uid exists (active or disabled)."""
    db = get_database()
    with driver.session(database=db) as session:
        result = session.run(
            "MATCH (n {uid: $uid}) RETURN count(n) AS c",
            uid=uid,
        )
        record = result.single()
        return record["c"] > 0 if record else False


# ── Relationship operations ───────────────────────────────────────────────────

def create_relationship(
    driver: Driver,
    from_uid: str,
    to_uid: str,
    rel_type: str,
    props: Optional[dict] = None,
) -> bool:
    """
    Create a relationship between two nodes.
    Returns True on success, False if either node is not found.
    """
    db = get_database()
    props = _strip_empty(props or {})
    with driver.session(database=db) as session:
        result = session.run(
            f"""
            MATCH (a {{uid: $from_uid}}), (b {{uid: $to_uid}})
            CREATE (a)-[r:{rel_type} $props]->(b)
            RETURN count(r) AS c
            """,
            from_uid=from_uid,
            to_uid=to_uid,
            props=props,
        )
        record = result.single()
        return record["c"] > 0 if record else False


def relationship_exists(
    driver: Driver, from_uid: str, to_uid: str, rel_type: str
) -> bool:
    """Return True if a specific relationship already exists."""
    db = get_database()
    with driver.session(database=db) as session:
        result = session.run(
            f"""
            MATCH (a {{uid: $from_uid}})-[r:{rel_type}]->(b {{uid: $to_uid}})
            RETURN count(r) AS c
            """,
            from_uid=from_uid,
            to_uid=to_uid,
        )
        record = result.single()
        return record["c"] > 0 if record else False


# ── Count / preflight ─────────────────────────────────────────────────────────

def count_all_nodes(driver: Driver) -> int:
    """Return total node count. Used for import pre-flight."""
    db = get_database()
    with driver.session(database=db) as session:
        result = session.run("MATCH (n) RETURN count(n) AS c")
        record = result.single()
        return record["c"] if record else 0
