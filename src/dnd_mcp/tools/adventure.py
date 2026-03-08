"""Tool handlers: adventure CRUD."""

_VALID_STATUSES = {"draft", "in-progress", "complete"}


# ── Validation helpers ─────────────────────────────────────────────────────────

def _require_str(value, field):
    """Return error dict if *value* is not a non-empty, non-whitespace string."""
    if not isinstance(value, str):
        return {"error": f"INVALID_PARAM: '{field}' must be a string, got {type(value).__name__}."}
    if not value.strip():
        return {"error": f"INVALID_PARAM: '{field}' must be non-empty."}
    return None


def _require_list(value, field):
    """Return error dict if *value* is not a list."""
    if not isinstance(value, list):
        return {"error": f"INVALID_PARAM: '{field}' must be a list, got {type(value).__name__}."}
    return None


# ── Tool functions ─────────────────────────────────────────────────────────────

def create_adventure(driver, uid=None, name=None, status=None,
                     setting=None, tags=None, summary=None, **kwargs):
    """Create or update an Adventure node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(name, "name")
    if err:
        return err
    if not isinstance(status, str):
        return {"error": f"INVALID_PARAM: 'status' must be a string, got {type(status).__name__}."}
    if status not in _VALID_STATUSES:
        return {"error": f"INVALID_PARAM: 'status' must be one of {sorted(_VALID_STATUSES)}, got '{status}'."}
    if tags is not None:
        err = _require_list(tags, "tags")
        if err:
            return err

    with driver.session() as session:
        result = session.run(
            "MERGE (a:Adventure {uid: $uid}) "
            "SET a.name = $name, a.status = $status, a.setting = $setting, "
            "a.tags = $tags, a.summary = $summary "
            "RETURN a.uid AS uid",
            uid=uid, name=name, status=status,
            setting=setting, tags=tags, summary=summary,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: creation of adventure '{uid}' returned no result."}
    return dict(result)


def get_adventure(driver, uid=None, **kwargs):
    """Return an Adventure node by uid, or an error dict if not found."""
    err = _require_str(uid, "uid")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MATCH (a:Adventure {uid: $uid}) RETURN a.uid AS uid, a.name AS name, "
            "a.status AS status, a.setting AS setting, a.tags AS tags, a.summary AS summary",
            uid=uid,
        ).single()

    if result is None:
        return {"error": f"NOT_FOUND: no adventure with uid '{uid}'."}
    return dict(result)
