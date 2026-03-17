"""Tool handlers: adventure management."""

from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.models.nodes import Adventure


def _err(code: str, reason: str) -> dict:
    return {"error": f"{code}: {reason}"}


def _ok(uid: str) -> dict:
    return {"uid": uid, "status": "ok"}


def _response(props: dict) -> dict:
    """Strip None and empty lists for MCP response."""
    return {k: v for k, v in props.items() if v is not None and v != []}


# ── create_adventure ──────────────────────────────────────────────────────────

def create_adventure(
    driver: Driver,
    uid: str,
    name: str,
    status: str = "draft",
    setting: Optional[str] = None,
    tags: Optional[list] = None,
    summary: Optional[str] = None,
) -> dict:
    """
    Create a new Adventure node.
    Returns {uid, status} on success.
    """
    if not uid or not name:
        return _err("MISSING_REQUIRED", "uid and name are required")

    if status not in ("draft", "in-progress", "complete"):
        return _err("INVALID_STATUS", "status must be draft, in-progress, or complete")

    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"a node with uid '{uid}' already exists")

    node = Adventure(
        uid=uid,
        name=name,
        status=status,
        setting=setting,
        tags=tags or [],
        summary=summary,
    )
    queries.create_node(driver, "Adventure", node.to_props())
    return _ok(uid)


# ── get_adventure ─────────────────────────────────────────────────────────────

def get_adventure(
    driver: Driver,
    uid: str,
    include_disabled: bool = False,
) -> dict:
    """
    Fetch an Adventure node by uid.
    Returns the node properties or an error dict.
    """
    props = queries.get_node_by_label(driver, "Adventure", uid, include_disabled)
    if props is None:
        return _err("NOT_FOUND", f"adventure '{uid}' not found")
    return _response(props)


# ── list_adventures ───────────────────────────────────────────────────────────

def list_adventures(
    driver: Driver,
    include_disabled: bool = False,
    verbose: bool = False,
) -> list:
    """
    List all Adventure nodes.
    Returns list of uids by default; full property dicts when verbose=True.
    """
    results = queries.list_nodes(
        driver,
        "Adventure",
        include_disabled=include_disabled,
        verbose=verbose,
    )
    if verbose:
        return [_response(p) for p in results]
    return results


# ── update_adventure ──────────────────────────────────────────────────────────

def update_adventure(
    driver: Driver,
    uid: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    setting: Optional[str] = None,
    tags: Optional[list] = None,
    summary: Optional[str] = None,
) -> dict:
    """
    Update mutable fields on an existing Adventure.
    Returns {uid, status} on success.
    """
    if status is not None and status not in ("draft", "in-progress", "complete"):
        return _err("INVALID_STATUS", "status must be draft, in-progress, or complete")

    updates: dict = {}
    if name is not None:
        updates["name"] = name
    if status is not None:
        updates["status"] = status
    if setting is not None:
        updates["setting"] = setting
    if tags is not None:
        updates["tags"] = tags
    if summary is not None:
        updates["summary"] = summary

    if not updates:
        return _err("NO_UPDATES", "no fields provided to update")

    result = queries.update_node(driver, uid, updates)
    if result is None:
        return _err("NOT_FOUND", f"adventure '{uid}' not found")
    return _ok(uid)


# ── link_adventures ───────────────────────────────────────────────────────────

def link_adventures(
    driver: Driver,
    from_uid: str,
    to_uid: str,
    rel_type: str = "RELATED_TO",
    props: Optional[dict] = None,
) -> dict:
    """
    Create a relationship between two Adventure nodes.
    rel_type: relationship label (e.g. SEQUEL_TO, PREQUEL_TO, RELATED_TO).
    Returns {uid, status} on success.
    """
    if not queries.node_exists(driver, from_uid):
        return _err("NOT_FOUND", f"adventure '{from_uid}' not found")
    if not queries.node_exists(driver, to_uid):
        return _err("NOT_FOUND", f"adventure '{to_uid}' not found")

    created = queries.create_relationship(driver, from_uid, to_uid, rel_type, props)
    if not created:
        return _err("REL_FAILED", "could not create relationship")
    return {"from_uid": from_uid, "to_uid": to_uid, "rel_type": rel_type, "status": "ok"}
