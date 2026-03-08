"""Tool handlers: entity CRUD (global and adventure-scoped)."""


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


# ── Global entity create ───────────────────────────────────────────────────────

def create_global_npc(driver, uid=None, canonical_name=None, summary=None,
                      aliases=None, source=None, is_canonical=None, **kwargs):
    """Create or update a GlobalNPC node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(canonical_name, "canonical_name")
    if err:
        return err
    err = _require_str(summary, "summary")
    if err:
        return err
    if aliases is not None:
        err = _require_list(aliases, "aliases")
        if err:
            return err

    with driver.session() as session:
        result = session.run(
            "MERGE (n:GlobalNPC {uid: $uid}) "
            "SET n.canonical_name = $canonical_name, n.summary = $summary, "
            "n.aliases = $aliases, n.source = $source, n.is_canonical = $is_canonical "
            "RETURN n.uid AS uid",
            uid=uid, canonical_name=canonical_name, summary=summary,
            aliases=aliases, source=source, is_canonical=is_canonical,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: creation of GlobalNPC '{uid}' returned no result."}
    return dict(result)


def create_global_location(driver, uid=None, canonical_name=None, summary=None,
                            source=None, region=None, is_canonical=None, **kwargs):
    """Create or update a GlobalLocation node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(canonical_name, "canonical_name")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MERGE (l:GlobalLocation {uid: $uid}) "
            "SET l.canonical_name = $canonical_name, l.summary = $summary, "
            "l.source = $source, l.region = $region, l.is_canonical = $is_canonical "
            "RETURN l.uid AS uid",
            uid=uid, canonical_name=canonical_name, summary=summary,
            source=source, region=region, is_canonical=is_canonical,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: creation of GlobalLocation '{uid}' returned no result."}
    return dict(result)


def create_global_item(driver, uid=None, canonical_name=None, summary=None,
                       source=None, rarity=None, is_canonical=None, **kwargs):
    """Create or update a GlobalItem node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(canonical_name, "canonical_name")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MERGE (i:GlobalItem {uid: $uid}) "
            "SET i.canonical_name = $canonical_name, i.summary = $summary, "
            "i.source = $source, i.rarity = $rarity, i.is_canonical = $is_canonical "
            "RETURN i.uid AS uid",
            uid=uid, canonical_name=canonical_name, summary=summary,
            source=source, rarity=rarity, is_canonical=is_canonical,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: creation of GlobalItem '{uid}' returned no result."}
    return dict(result)


def create_global_faction(driver, uid=None, canonical_name=None, summary=None,
                           source=None, alignment=None, is_canonical=None, **kwargs):
    """Create or update a GlobalFaction node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(canonical_name, "canonical_name")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MERGE (f:GlobalFaction {uid: $uid}) "
            "SET f.canonical_name = $canonical_name, f.summary = $summary, "
            "f.source = $source, f.alignment = $alignment, f.is_canonical = $is_canonical "
            "RETURN f.uid AS uid",
            uid=uid, canonical_name=canonical_name, summary=summary,
            source=source, alignment=alignment, is_canonical=is_canonical,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: creation of GlobalFaction '{uid}' returned no result."}
    return dict(result)


# ── Global entity read ─────────────────────────────────────────────────────────

def get_global_entity(driver, uid=None, **kwargs):
    """Return any global entity node by uid, or an error dict if not found."""
    err = _require_str(uid, "uid")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MATCH (n) WHERE n.uid = $uid AND (n:GlobalNPC OR n:GlobalLocation "
            "OR n:GlobalItem OR n:GlobalFaction) RETURN n.uid AS uid",
            uid=uid,
        ).single()

    if result is None:
        return {"error": f"NOT_FOUND: no global entity with uid '{uid}'."}
    return dict(result)


# ── Adventure-scoped entity upsert ─────────────────────────────────────────────

def upsert_npc(driver, uid=None, name=None, summary=None,
               source_adventure=None, **kwargs):
    """Create or update an adventure-scoped NPC node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(name, "name")
    if err:
        return err
    err = _require_str(source_adventure, "source_adventure")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MERGE (n:NPC {uid: $uid}) "
            "SET n.name = $name, n.summary = $summary, n.source_adventure = $source_adventure "
            "RETURN n.uid AS uid",
            uid=uid, name=name, summary=summary, source_adventure=source_adventure,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: upsert of NPC '{uid}' returned no result."}
    return dict(result)


def upsert_location(driver, uid=None, name=None, summary=None,
                    source_adventure=None, **kwargs):
    """Create or update an adventure-scoped Location node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(name, "name")
    if err:
        return err
    err = _require_str(source_adventure, "source_adventure")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MERGE (l:Location {uid: $uid}) "
            "SET l.name = $name, l.summary = $summary, l.source_adventure = $source_adventure "
            "RETURN l.uid AS uid",
            uid=uid, name=name, summary=summary, source_adventure=source_adventure,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: upsert of Location '{uid}' returned no result."}
    return dict(result)


def upsert_item(driver, uid=None, name=None, summary=None,
                source_adventure=None, **kwargs):
    """Create or update an adventure-scoped Item node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(name, "name")
    if err:
        return err
    err = _require_str(source_adventure, "source_adventure")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MERGE (i:Item {uid: $uid}) "
            "SET i.name = $name, i.summary = $summary, i.source_adventure = $source_adventure "
            "RETURN i.uid AS uid",
            uid=uid, name=name, summary=summary, source_adventure=source_adventure,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: upsert of Item '{uid}' returned no result."}
    return dict(result)


def upsert_faction(driver, uid=None, name=None, summary=None,
                   source_adventure=None, **kwargs):
    """Create or update an adventure-scoped Faction node.  Returns {'uid': ...} on success."""
    err = _require_str(uid, "uid")
    if err:
        return err
    err = _require_str(name, "name")
    if err:
        return err
    err = _require_str(source_adventure, "source_adventure")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MERGE (f:Faction {uid: $uid}) "
            "SET f.name = $name, f.summary = $summary, f.source_adventure = $source_adventure "
            "RETURN f.uid AS uid",
            uid=uid, name=name, summary=summary, source_adventure=source_adventure,
        ).single()

    if result is None:
        return {"error": f"INTERNAL: upsert of Faction '{uid}' returned no result."}
    return dict(result)


# ── Adventure-scoped entity read ───────────────────────────────────────────────

def get_entity(driver, uid=None, **kwargs):
    """Return any adventure-scoped entity node by uid, or an error dict if not found."""
    err = _require_str(uid, "uid")
    if err:
        return err

    with driver.session() as session:
        result = session.run(
            "MATCH (n) WHERE n.uid = $uid AND (n:NPC OR n:Location OR n:Item OR n:Faction) "
            "RETURN n.uid AS uid",
            uid=uid,
        ).single()

    if result is None:
        return {"error": f"NOT_FOUND: no adventure-scoped entity with uid '{uid}'."}
    return dict(result)
