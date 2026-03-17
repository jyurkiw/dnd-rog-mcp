"""Tool handlers: soft delete — disable, undelete, true_delete."""

import os
from datetime import datetime, timezone
from neo4j import Driver

from dnd_mcp.db.connection import get_database


def _err(code, reason):
    return {"error": f"{code}: {reason}"}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Cascade table ─────────────────────────────────────────────────────────────
# Maps a node label to a Cypher snippet that finds all nodes to cascade-disable.
# Each snippet starts from the trigger node (bound as `root`) and returns
# additional nodes bound as `n`.

_CASCADE_QUERIES = {
    "Adventure": """
        MATCH (root {uid: $uid})<-[:BELONGS_TO|WITHIN_ADVENTURE]-(n)
        WHERE n.uid <> $uid
    """,
    "GlobalNPC": """
        MATCH (root {uid: $uid})-[:REPRESENTED_BY]->(n:NPCContext)
    """,
    "GlobalLocation": """
        MATCH (root {uid: $uid})-[:REPRESENTED_BY]->(n:NPCContext)
    """,
    "GlobalItem": """
        MATCH (root {uid: $uid})-[:REPRESENTED_BY]->(n:NPCContext)
    """,
    "GlobalFaction": """
        MATCH (root {uid: $uid})-[:REPRESENTED_BY]->(n:NPCContext)
    """,
    "NPCContext": """
        MATCH (root {uid: $uid})<-[:SPEAKS|HAS_OPINION]-(n)
        WHERE n.uid <> $uid
    """,
    "Plotline": """
        MATCH (root {uid: $uid})<-[:PART_OF_PLOTLINE]-(e:Event)
        OPTIONAL MATCH (e)-[:BRANCHES_INTO]->(c:Choice)-[:HAS_OUTCOME]->(o:Outcome)
        WITH collect(e) + collect(c) + collect(o) AS nodes
        UNWIND nodes AS n WHERE n IS NOT NULL
    """,
    "Event": """
        MATCH (root {uid: $uid})-[:BRANCHES_INTO]->(c:Choice)-[:HAS_OUTCOME]->(o:Outcome)
        WITH collect(c) + collect(o) AS nodes
        UNWIND nodes AS n WHERE n IS NOT NULL
    """,
    "Choice": """
        MATCH (root {uid: $uid})-[:HAS_OUTCOME]->(n:Outcome)
    """,
    "BoxedTextSequence": """
        MATCH (root {uid: $uid})-[:OPENS_WITH|HAS_BOXED_TEXT]->(n:BoxedText)
    """,
    "Location": """
        MATCH (enc)-[:LOCATED_IN]->(root {uid: $uid})
        WHERE (enc:Combat OR enc:SkillChallenge OR enc:Trap)
        WITH enc AS n
        WHERE NOT EXISTS {
            MATCH (n)-[:LOCATED_IN]->(other_loc)
            WHERE other_loc.uid <> $uid AND other_loc.disabled = false
        }
    """,
}


def _get_label(driver, uid):
    db = get_database()
    with driver.session(database=db) as session:
        result = session.run("MATCH (n {uid: $uid}) RETURN labels(n) AS labels", uid=uid)
        record = result.single()
        if record is None:
            return None
        labels = [l for l in record["labels"] if l not in ("BaseNode",)]
        return labels[0] if labels else None


def disable(driver, uid):
    """
    SD-01..SD-08: soft-delete a node and cascade to owned/dependent nodes.
    """
    label = _get_label(driver, uid)
    if label is None:
        return _err("NOT_FOUND", f"node '{uid}' not found")

    db = get_database()
    now = _now()

    with driver.session(database=db) as session:
        # Disable the root node
        session.run("""
            MATCH (n {uid: $uid})
            SET n.disabled = true,
                n.disabled_at = $now,
                n.disabled_by = CASE WHEN $uid IN n.disabled_by THEN n.disabled_by
                                     ELSE coalesce(n.disabled_by, []) + [$uid] END
        """, uid=uid, now=now)

        # Cascade
        cascade_q = _CASCADE_QUERIES.get(label)
        if cascade_q:
            session.run(f"""
                MATCH (root {{uid: $uid}})
                {cascade_q}
                SET n.disabled = true,
                    n.disabled_at = $now,
                    n.disabled_by = CASE WHEN $uid IN n.disabled_by THEN n.disabled_by
                                         ELSE coalesce(n.disabled_by, []) + [$uid] END
            """, uid=uid, now=now)

    return {"uid": uid, "status": "disabled"}


def undelete(driver, uid):
    """
    SD-09..SD-10: remove uid from disabled_by on all cascade-affected nodes.
    Only re-enables a node when disabled_by becomes empty.
    """
    db = get_database()
    with driver.session(database=db) as session:
        result = session.run("""
            MATCH (n)
            WHERE $uid IN n.disabled_by
            SET n.disabled_by = [x IN n.disabled_by WHERE x <> $uid]
            SET n.disabled = size([x IN n.disabled_by WHERE x <> $uid]) > 0
            RETURN count(n) AS affected
        """, uid=uid)
        record = result.single()
        affected = record["affected"] if record else 0

    return {"uid": uid, "status": "undeleted", "nodes_affected": affected}


def true_delete(driver, uid):
    """
    SD-11..SD-14, SD-17..SD-20: permanently delete a node.
    Only allowed when ALLOW_TRUE_DELETE=true AND the node is already disabled.
    """
    allow = os.environ.get("ALLOW_TRUE_DELETE", "false").lower() == "true"
    if not allow:
        return _err(
            "TRUE_DELETE_DISABLED",
            "true_delete is disabled. Set ALLOW_TRUE_DELETE=true to enable permanent deletion.",
        )

    label = _get_label(driver, uid)
    if label is None:
        return _err("NOT_FOUND", f"node '{uid}' not found")

    db = get_database()
    with driver.session(database=db) as session:
        # SD-11: hard-fail if not already disabled
        check = session.run("MATCH (n {uid: $uid}) RETURN n.disabled AS d", uid=uid).single()
        if not check or not check["d"]:
            return _err("NOT_DISABLED", "node must be disabled before calling true_delete")

        # Collect cascade nodes
        cascade_q = _CASCADE_QUERIES.get(label, "")
        if cascade_q:
            cascade_uids_result = session.run(f"""
                MATCH (root {{uid: $uid}})
                {cascade_q}
                WHERE n.disabled = true
                RETURN n.uid AS cascade_uid
            """, uid=uid)
            cascade_uids = [r["cascade_uid"] for r in cascade_uids_result]
        else:
            cascade_uids = []

        all_uids = [uid] + cascade_uids

        # Delete all relationships first, then nodes
        result = session.run("""
            MATCH (n) WHERE n.uid IN $uids
            OPTIONAL MATCH (n)-[r]-()
            DELETE r
            WITH count(r) AS rel_count
            MATCH (n) WHERE n.uid IN $uids
            DELETE n
            RETURN rel_count, count(n) AS node_count
        """, uids=all_uids)
        record = result.single()

    return {
        "uid": uid,
        "status": "deleted",
        "nodes_deleted": len(all_uids),
        "relationships_deleted": record["rel_count"] if record else 0,
    }
