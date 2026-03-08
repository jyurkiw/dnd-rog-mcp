"""
Entity CRUD unit tests — Create operations.

Tests input validation and error-response shape for:
    Global entities:      create_global_npc, create_global_location,
                          create_global_item, create_global_faction
    Adventure-scoped:     upsert_npc, upsert_location, upsert_item, upsert_faction

All tests are pure unit tests: the Neo4j driver is fully mocked and the DB is
never touched.

Requirement coverage:
    MP-02  All tool errors must return structured error content blocks, not exceptions.
    MP-03  Every tool must validate input parameters before executing any DB operation.
    MP-04  Tools that write data must return the uid(s) of created or modified nodes.
"""

import pytest
from unittest.mock import MagicMock
from assertpy import assert_that

from dnd_mcp.tools.entities import (
    create_global_npc,
    create_global_location,
    create_global_item,
    create_global_faction,
    get_global_entity,
    upsert_npc,
    upsert_location,
    upsert_item,
    upsert_faction,
    get_entity,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mock_driver():
    """Return a MagicMock representing a connected Neo4j driver."""
    return MagicMock()


def _driver_returning(value):
    """Return a MagicMock driver whose session.run().single() returns *value*."""
    driver = MagicMock()
    session = driver.session.return_value.__enter__.return_value
    session.run.return_value.single.return_value = value
    return driver


# ── Valid fixture dicts ───────────────────────────────────────────────────────

VALID_GLOBAL_NPC = {
    "uid": "global-npc-elminster",
    "canonical_name": "Elminster Aumar",
    "aliases": ["The Old Mage", "El"],
    "summary": "Archmage of Shadowdale, Chosen of Mystra.",
    "source": "Forgotten Realms",
    "is_canonical": True,
}

VALID_GLOBAL_LOCATION = {
    "uid": "global-location-shadowdale",
    "canonical_name": "Shadowdale",
    "summary": "A small, insular dale in the Forgotten Realms.",
    "source": "Forgotten Realms",
    "region": "The Dalelands",
    "is_canonical": True,
}

VALID_GLOBAL_ITEM = {
    "uid": "global-item-pipe-of-elminster",
    "canonical_name": "Pipe of Elminster",
    "summary": "Elminster's beloved pipe, enchanted and unmistakable.",
    "source": "Forgotten Realms",
    "rarity": "rare",
    "is_canonical": True,
}

VALID_GLOBAL_FACTION = {
    "uid": "global-faction-harpers",
    "canonical_name": "The Harpers",
    "summary": "A secret network fighting against tyranny.",
    "source": "Forgotten Realms",
    "alignment": "neutral good",
    "is_canonical": True,
}

VALID_ADVENTURE_UID = "shadowdale-2024"

VALID_NPC = {
    "uid": "npc-jhaele-silvermane",
    "name": "Jhaele Silvermane",
    "summary": "Retired adventurer turned dairy farmer.",
    "source_adventure": VALID_ADVENTURE_UID,
}

VALID_LOCATION = {
    "uid": "location-jhaele-farm",
    "name": "Jhaele's Farm",
    "summary": "A dairy farm on the outskirts of Shadowdale.",
    "source_adventure": VALID_ADVENTURE_UID,
}

VALID_ITEM = {
    "uid": "item-wooden-chest",
    "name": "Locked Wooden Chest",
    "summary": "A battered chest found in the millpond monster's lair.",
    "source_adventure": VALID_ADVENTURE_UID,
}

VALID_FACTION = {
    "uid": "faction-dale-militia",
    "name": "Shadowdale Militia",
    "summary": "Loose band of volunteer defenders.",
    "source_adventure": VALID_ADVENTURE_UID,
}


# ══════════════════════════════════════════════════════════════════════════════
# create_global_npc
# ══════════════════════════════════════════════════════════════════════════════

# ── MP-03: Null / None ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_MP_03_create_global_npc_null_uid_returns_error():
    """create_global_npc with uid=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid=None, canonical_name="Elminster Aumar", summary="Archmage.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_null_canonical_name_returns_error():
    """create_global_npc with canonical_name=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid="global-npc-test", canonical_name=None, summary="A mage.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_null_summary_returns_error():
    """create_global_npc with summary=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid="global-npc-test", canonical_name="Test NPC", summary=None)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


# ── MP-03: Zero / empty-string ────────────────────────────────────────────────

@pytest.mark.unit
def test_MP_03_create_global_npc_empty_uid_returns_error():
    """create_global_npc with uid="" must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid="", canonical_name="Test NPC", summary="A test NPC.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_zero_uid_returns_error():
    """create_global_npc with uid=0 (integer zero) must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid=0, canonical_name="Test NPC", summary="A test NPC.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_empty_canonical_name_returns_error():
    """create_global_npc with canonical_name="" must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid="global-npc-test", canonical_name="", summary="A test NPC.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


# ── MP-03: Wrong type — int / float in string fields ─────────────────────────

@pytest.mark.unit
def test_MP_03_create_global_npc_integer_uid_returns_error():
    """create_global_npc with uid=99 (non-zero integer) must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid=99, canonical_name="Test NPC", summary="A test NPC.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_float_uid_returns_error():
    """create_global_npc with uid=1.5 (float) must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid=1.5, canonical_name="Test NPC", summary="A test NPC.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_integer_canonical_name_returns_error():
    """create_global_npc with canonical_name=42 must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid="global-npc-test", canonical_name=42, summary="A test NPC.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_float_canonical_name_returns_error():
    """create_global_npc with canonical_name=3.14 must return a structured error."""
    driver = _mock_driver()
    result = create_global_npc(driver, uid="global-npc-test", canonical_name=3.14, summary="A test NPC.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_integer_aliases_returns_error():
    """create_global_npc with aliases=7 (integer instead of list) must return an error."""
    driver = _mock_driver()
    result = create_global_npc(
        driver,
        uid="global-npc-test",
        canonical_name="Test NPC",
        summary="A test NPC.",
        aliases=7,
    )

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_float_aliases_returns_error():
    """create_global_npc with aliases=0.5 (float instead of list) must return an error."""
    driver = _mock_driver()
    result = create_global_npc(
        driver,
        uid="global-npc-test",
        canonical_name="Test NPC",
        summary="A test NPC.",
        aliases=0.5,
    )

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


# ── MP-03: Missing required arguments ────────────────────────────────────────

@pytest.mark.unit
def test_MP_03_create_global_npc_missing_uid_returns_error():
    """
    create_global_npc called without uid must return a structured error or raise TypeError.
    """
    driver = _mock_driver()
    try:
        result = create_global_npc(driver, canonical_name="Test NPC", summary="A test NPC.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_missing_canonical_name_returns_error():
    """
    create_global_npc called without canonical_name must return a structured error or raise TypeError.
    """
    driver = _mock_driver()
    try:
        result = create_global_npc(driver, uid="global-npc-test", summary="A test NPC.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_npc_missing_summary_returns_error():
    """
    create_global_npc called without summary must return a structured error or raise TypeError.
    """
    driver = _mock_driver()
    try:
        result = create_global_npc(driver, uid="global-npc-test", canonical_name="Test NPC")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


# ── MP-03: Extra / unexpected arguments ──────────────────────────────────────

@pytest.mark.unit
def test_MP_03_create_global_npc_extra_args_does_not_raise():
    """
    create_global_npc called with extra unknown keyword arguments must not propagate
    an unhandled exception.
    """
    driver = _mock_driver()
    try:
        result = create_global_npc(
            driver,
            uid="global-npc-test",
            canonical_name="Test NPC",
            summary="A test NPC.",
            unrecognized_field="surprise",
            another_extra=0,
        )
        assert_that(result).is_instance_of(dict)
    except TypeError:
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception for extra args: {type(exc).__name__}: {exc}")


# ── MP-04: Successful creation returns uid ────────────────────────────────────

@pytest.mark.unit
def test_MP_04_create_global_npc_success_returns_uid():
    """Valid create_global_npc must return a dict containing 'uid'."""
    driver = _driver_returning({"uid": "global-npc-elminster"})

    result = create_global_npc(driver, **VALID_GLOBAL_NPC)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("global-npc-elminster")


# ══════════════════════════════════════════════════════════════════════════════
# create_global_location
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_MP_03_create_global_location_null_uid_returns_error():
    """create_global_location with uid=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_location(driver, uid=None, canonical_name="Shadowdale", summary="A dale.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_location_null_canonical_name_returns_error():
    """create_global_location with canonical_name=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_location(driver, uid="global-loc-test", canonical_name=None, summary="A dale.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_location_empty_uid_returns_error():
    """create_global_location with uid="" must return a structured error."""
    driver = _mock_driver()
    result = create_global_location(driver, uid="", canonical_name="Shadowdale", summary="A dale.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_location_zero_uid_returns_error():
    """create_global_location with uid=0 (integer zero) must return a structured error."""
    driver = _mock_driver()
    result = create_global_location(driver, uid=0, canonical_name="Shadowdale", summary="A dale.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_location_integer_uid_returns_error():
    """create_global_location with uid=5 (integer) must return a structured error."""
    driver = _mock_driver()
    result = create_global_location(driver, uid=5, canonical_name="Shadowdale", summary="A dale.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_location_float_canonical_name_returns_error():
    """create_global_location with canonical_name=1.0 must return a structured error."""
    driver = _mock_driver()
    result = create_global_location(driver, uid="global-loc-test", canonical_name=1.0, summary="A dale.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_location_missing_uid_returns_error():
    """create_global_location without uid must return a structured error or raise TypeError."""
    driver = _mock_driver()
    try:
        result = create_global_location(driver, canonical_name="Shadowdale", summary="A dale.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_location_extra_args_does_not_raise():
    """create_global_location with extra unknown kwargs must not raise an unhandled exception."""
    driver = _mock_driver()
    try:
        result = create_global_location(
            driver,
            uid="global-loc-test",
            canonical_name="Shadowdale",
            summary="A dale.",
            mystery_field="unexpected",
        )
        assert_that(result).is_instance_of(dict)
    except TypeError:
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception for extra args: {type(exc).__name__}: {exc}")


@pytest.mark.unit
def test_MP_04_create_global_location_success_returns_uid():
    """Valid create_global_location must return a dict containing 'uid'."""
    driver = _driver_returning({"uid": "global-location-shadowdale"})

    result = create_global_location(driver, **VALID_GLOBAL_LOCATION)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("global-location-shadowdale")


# ══════════════════════════════════════════════════════════════════════════════
# create_global_item
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_MP_03_create_global_item_null_uid_returns_error():
    """create_global_item with uid=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_item(driver, uid=None, canonical_name="Pipe of Elminster", summary="A pipe.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_null_canonical_name_returns_error():
    """create_global_item with canonical_name=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_item(driver, uid="global-item-test", canonical_name=None, summary="A pipe.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_empty_uid_returns_error():
    """create_global_item with uid="" must return a structured error."""
    driver = _mock_driver()
    result = create_global_item(driver, uid="", canonical_name="Test Item", summary="A test item.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_zero_uid_returns_error():
    """create_global_item with uid=0 must return a structured error."""
    driver = _mock_driver()
    result = create_global_item(driver, uid=0, canonical_name="Test Item", summary="A test item.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_integer_uid_returns_error():
    """create_global_item with uid=7 (non-zero integer) must return a structured error."""
    driver = _mock_driver()
    result = create_global_item(driver, uid=7, canonical_name="Test Item", summary="A test item.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_float_uid_returns_error():
    """create_global_item with uid=2.5 (float) must return a structured error."""
    driver = _mock_driver()
    result = create_global_item(driver, uid=2.5, canonical_name="Test Item", summary="A test item.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_integer_canonical_name_returns_error():
    """create_global_item with canonical_name=0 (integer) must return a structured error."""
    driver = _mock_driver()
    result = create_global_item(driver, uid="global-item-test", canonical_name=0, summary="A test item.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_missing_uid_returns_error():
    """create_global_item without uid must return a structured error or raise TypeError."""
    driver = _mock_driver()
    try:
        result = create_global_item(driver, canonical_name="Test Item", summary="A test item.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_missing_canonical_name_returns_error():
    """create_global_item without canonical_name must return a structured error or raise TypeError."""
    driver = _mock_driver()
    try:
        result = create_global_item(driver, uid="global-item-test", summary="A test item.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_item_extra_args_does_not_raise():
    """create_global_item with extra unknown kwargs must not raise an unhandled exception."""
    driver = _mock_driver()
    try:
        result = create_global_item(
            driver,
            uid="global-item-test",
            canonical_name="Test Item",
            summary="A test item.",
            totally_unknown=True,
        )
        assert_that(result).is_instance_of(dict)
    except TypeError:
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception for extra args: {type(exc).__name__}: {exc}")


@pytest.mark.unit
def test_MP_04_create_global_item_success_returns_uid():
    """Valid create_global_item must return a dict containing 'uid'."""
    driver = _driver_returning({"uid": "global-item-pipe-of-elminster"})

    result = create_global_item(driver, **VALID_GLOBAL_ITEM)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("global-item-pipe-of-elminster")


# ══════════════════════════════════════════════════════════════════════════════
# create_global_faction
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_MP_03_create_global_faction_null_uid_returns_error():
    """create_global_faction with uid=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_faction(driver, uid=None, canonical_name="The Harpers", summary="A network.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_faction_null_canonical_name_returns_error():
    """create_global_faction with canonical_name=None must return a structured error."""
    driver = _mock_driver()
    result = create_global_faction(driver, uid="global-faction-test", canonical_name=None, summary="A network.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_faction_empty_uid_returns_error():
    """create_global_faction with uid="" must return a structured error."""
    driver = _mock_driver()
    result = create_global_faction(driver, uid="", canonical_name="The Harpers", summary="A network.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_faction_zero_uid_returns_error():
    """create_global_faction with uid=0 must return a structured error."""
    driver = _mock_driver()
    result = create_global_faction(driver, uid=0, canonical_name="The Harpers", summary="A network.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_faction_integer_uid_returns_error():
    """create_global_faction with uid=3 (non-zero integer) must return a structured error."""
    driver = _mock_driver()
    result = create_global_faction(driver, uid=3, canonical_name="The Harpers", summary="A network.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_faction_float_uid_returns_error():
    """create_global_faction with uid=0.1 (float) must return a structured error."""
    driver = _mock_driver()
    result = create_global_faction(driver, uid=0.1, canonical_name="The Harpers", summary="A network.")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_faction_missing_uid_returns_error():
    """create_global_faction without uid must return a structured error or raise TypeError."""
    driver = _mock_driver()
    try:
        result = create_global_faction(driver, canonical_name="The Harpers", summary="A network.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_global_faction_extra_args_does_not_raise():
    """create_global_faction with extra unknown kwargs must not raise an unhandled exception."""
    driver = _mock_driver()
    try:
        result = create_global_faction(
            driver,
            uid="global-faction-test",
            canonical_name="The Harpers",
            summary="A network.",
            unexpected_key="oops",
        )
        assert_that(result).is_instance_of(dict)
    except TypeError:
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception for extra args: {type(exc).__name__}: {exc}")


@pytest.mark.unit
def test_MP_04_create_global_faction_success_returns_uid():
    """Valid create_global_faction must return a dict containing 'uid'."""
    driver = _driver_returning({"uid": "global-faction-harpers"})

    result = create_global_faction(driver, **VALID_GLOBAL_FACTION)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("global-faction-harpers")


# ══════════════════════════════════════════════════════════════════════════════
# upsert_npc  (adventure-scoped)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_MP_03_upsert_npc_null_uid_returns_error():
    """upsert_npc with uid=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid=None, name="Jhaele", summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_null_name_returns_error():
    """upsert_npc with name=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid="npc-test", name=None, summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_null_source_adventure_returns_error():
    """
    upsert_npc with source_adventure=None must return a structured error.
    Every adventure-scoped entity requires a valid source_adventure uid.
    """
    driver = _mock_driver()
    result = upsert_npc(driver, uid="npc-test", name="Jhaele", summary="A farmer.", source_adventure=None)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_empty_uid_returns_error():
    """upsert_npc with uid="" must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid="", name="Jhaele", summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_zero_uid_returns_error():
    """upsert_npc with uid=0 (integer zero) must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid=0, name="Jhaele", summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_empty_name_returns_error():
    """upsert_npc with name="" must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid="npc-test", name="", summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_integer_uid_returns_error():
    """upsert_npc with uid=10 (integer) must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid=10, name="Jhaele", summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_float_uid_returns_error():
    """upsert_npc with uid=1.1 (float) must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid=1.1, name="Jhaele", summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_integer_name_returns_error():
    """upsert_npc with name=5 (integer) must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid="npc-test", name=5, summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_float_name_returns_error():
    """upsert_npc with name=0.0 (float) must return a structured error."""
    driver = _mock_driver()
    result = upsert_npc(driver, uid="npc-test", name=0.0, summary="A farmer.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_missing_source_adventure_returns_error():
    """
    upsert_npc without source_adventure must return a structured error or raise TypeError.
    """
    driver = _mock_driver()
    try:
        result = upsert_npc(driver, uid="npc-test", name="Jhaele", summary="A farmer.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_npc_extra_args_does_not_raise():
    """upsert_npc with extra unknown kwargs must not raise an unhandled exception."""
    driver = _mock_driver()
    try:
        result = upsert_npc(
            driver,
            uid="npc-test",
            name="Jhaele",
            summary="A farmer.",
            source_adventure=VALID_ADVENTURE_UID,
            totally_unknown_field="surprise",
        )
        assert_that(result).is_instance_of(dict)
    except TypeError:
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception for extra args: {type(exc).__name__}: {exc}")


@pytest.mark.unit
def test_MP_04_upsert_npc_success_returns_uid():
    """Valid upsert_npc must return a dict containing 'uid'."""
    driver = _driver_returning({"uid": "npc-jhaele-silvermane"})

    result = upsert_npc(driver, **VALID_NPC)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("npc-jhaele-silvermane")


# ══════════════════════════════════════════════════════════════════════════════
# upsert_location  (adventure-scoped)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_MP_03_upsert_location_null_uid_returns_error():
    """upsert_location with uid=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_location(driver, uid=None, name="Jhaele's Farm", summary="A farm.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_location_null_name_returns_error():
    """upsert_location with name=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_location(driver, uid="loc-test", name=None, summary="A farm.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_location_null_source_adventure_returns_error():
    """upsert_location with source_adventure=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_location(driver, uid="loc-test", name="Jhaele's Farm", summary="A farm.", source_adventure=None)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_location_empty_uid_returns_error():
    """upsert_location with uid="" must return a structured error."""
    driver = _mock_driver()
    result = upsert_location(driver, uid="", name="Jhaele's Farm", summary="A farm.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_location_zero_uid_returns_error():
    """upsert_location with uid=0 must return a structured error."""
    driver = _mock_driver()
    result = upsert_location(driver, uid=0, name="Jhaele's Farm", summary="A farm.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_location_integer_uid_returns_error():
    """upsert_location with uid=100 (non-zero integer) must return a structured error."""
    driver = _mock_driver()
    result = upsert_location(driver, uid=100, name="Jhaele's Farm", summary="A farm.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_location_float_name_returns_error():
    """upsert_location with name=3.14 (float) must return a structured error."""
    driver = _mock_driver()
    result = upsert_location(driver, uid="loc-test", name=3.14, summary="A farm.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_location_missing_source_adventure_returns_error():
    """upsert_location without source_adventure must return a structured error or raise TypeError."""
    driver = _mock_driver()
    try:
        result = upsert_location(driver, uid="loc-test", name="Jhaele's Farm", summary="A farm.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_location_extra_args_does_not_raise():
    """upsert_location with extra unknown kwargs must not raise an unhandled exception."""
    driver = _mock_driver()
    try:
        result = upsert_location(
            driver,
            uid="loc-test",
            name="Jhaele's Farm",
            summary="A farm.",
            source_adventure=VALID_ADVENTURE_UID,
            unknown_kwarg="surprise",
        )
        assert_that(result).is_instance_of(dict)
    except TypeError:
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception for extra args: {type(exc).__name__}: {exc}")


@pytest.mark.unit
def test_MP_04_upsert_location_success_returns_uid():
    """Valid upsert_location must return a dict containing 'uid'."""
    driver = _driver_returning({"uid": "location-jhaele-farm"})

    result = upsert_location(driver, **VALID_LOCATION)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("location-jhaele-farm")


# ══════════════════════════════════════════════════════════════════════════════
# upsert_item  (adventure-scoped)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_MP_03_upsert_item_null_uid_returns_error():
    """upsert_item with uid=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid=None, name="Wooden Chest", summary="A chest.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_null_name_returns_error():
    """upsert_item with name=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid="item-test", name=None, summary="A chest.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_null_source_adventure_returns_error():
    """upsert_item with source_adventure=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid="item-test", name="Wooden Chest", summary="A chest.", source_adventure=None)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_empty_uid_returns_error():
    """upsert_item with uid="" must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid="", name="Wooden Chest", summary="A chest.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_zero_uid_returns_error():
    """upsert_item with uid=0 (integer zero) must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid=0, name="Wooden Chest", summary="A chest.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_integer_uid_returns_error():
    """upsert_item with uid=8 (non-zero integer) must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid=8, name="Wooden Chest", summary="A chest.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_float_uid_returns_error():
    """upsert_item with uid=0.5 (float) must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid=0.5, name="Wooden Chest", summary="A chest.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_integer_name_returns_error():
    """upsert_item with name=0 (integer zero) must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid="item-test", name=0, summary="A chest.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_float_name_returns_error():
    """upsert_item with name=2.2 (float) must return a structured error."""
    driver = _mock_driver()
    result = upsert_item(driver, uid="item-test", name=2.2, summary="A chest.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_missing_source_adventure_returns_error():
    """upsert_item without source_adventure must return a structured error or raise TypeError."""
    driver = _mock_driver()
    try:
        result = upsert_item(driver, uid="item-test", name="Wooden Chest", summary="A chest.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_item_extra_args_does_not_raise():
    """upsert_item with extra unknown kwargs must not raise an unhandled exception."""
    driver = _mock_driver()
    try:
        result = upsert_item(
            driver,
            uid="item-test",
            name="Wooden Chest",
            summary="A chest.",
            source_adventure=VALID_ADVENTURE_UID,
            completely_made_up=True,
        )
        assert_that(result).is_instance_of(dict)
    except TypeError:
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception for extra args: {type(exc).__name__}: {exc}")


@pytest.mark.unit
def test_MP_04_upsert_item_success_returns_uid():
    """Valid upsert_item must return a dict containing 'uid'."""
    driver = _driver_returning({"uid": "item-wooden-chest"})

    result = upsert_item(driver, **VALID_ITEM)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("item-wooden-chest")


# ══════════════════════════════════════════════════════════════════════════════
# upsert_faction  (adventure-scoped)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_MP_03_upsert_faction_null_uid_returns_error():
    """upsert_faction with uid=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_faction(driver, uid=None, name="Shadowdale Militia", summary="Defenders.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_null_name_returns_error():
    """upsert_faction with name=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_faction(driver, uid="faction-test", name=None, summary="Defenders.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_null_source_adventure_returns_error():
    """upsert_faction with source_adventure=None must return a structured error."""
    driver = _mock_driver()
    result = upsert_faction(driver, uid="faction-test", name="Shadowdale Militia", summary="Defenders.", source_adventure=None)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_empty_uid_returns_error():
    """upsert_faction with uid="" must return a structured error."""
    driver = _mock_driver()
    result = upsert_faction(driver, uid="", name="Shadowdale Militia", summary="Defenders.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_zero_uid_returns_error():
    """upsert_faction with uid=0 (integer zero) must return a structured error."""
    driver = _mock_driver()
    result = upsert_faction(driver, uid=0, name="Shadowdale Militia", summary="Defenders.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_integer_uid_returns_error():
    """upsert_faction with uid=12 (non-zero integer) must return a structured error."""
    driver = _mock_driver()
    result = upsert_faction(driver, uid=12, name="Shadowdale Militia", summary="Defenders.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_float_uid_returns_error():
    """upsert_faction with uid=0.0 (float zero) must return a structured error."""
    driver = _mock_driver()
    result = upsert_faction(driver, uid=0.0, name="Shadowdale Militia", summary="Defenders.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_integer_name_returns_error():
    """upsert_faction with name=1 (integer) must return a structured error."""
    driver = _mock_driver()
    result = upsert_faction(driver, uid="faction-test", name=1, summary="Defenders.", source_adventure=VALID_ADVENTURE_UID)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_missing_source_adventure_returns_error():
    """upsert_faction without source_adventure must return a structured error or raise TypeError."""
    driver = _mock_driver()
    try:
        result = upsert_faction(driver, uid="faction-test", name="Shadowdale Militia", summary="Defenders.")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_upsert_faction_extra_args_does_not_raise():
    """upsert_faction with extra unknown kwargs must not raise an unhandled exception."""
    driver = _mock_driver()
    try:
        result = upsert_faction(
            driver,
            uid="faction-test",
            name="Shadowdale Militia",
            summary="Defenders.",
            source_adventure=VALID_ADVENTURE_UID,
            extra_kwarg="oops",
        )
        assert_that(result).is_instance_of(dict)
    except TypeError:
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception for extra args: {type(exc).__name__}: {exc}")


@pytest.mark.unit
def test_MP_04_upsert_faction_success_returns_uid():
    """Valid upsert_faction must return a dict containing 'uid'."""
    driver = _driver_returning({"uid": "faction-dale-militia"})

    result = upsert_faction(driver, **VALID_FACTION)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("faction-dale-militia")


# ══════════════════════════════════════════════════════════════════════════════
# MP-02: Not-found (404 sanity) — one test per entity sub-endpoint
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_MP_02_get_global_entity_not_found_npc_returns_structured_error():
    """
    get_global_entity with a non-existent NPC uid must return a structured error dict
    containing an 'error' key and must not raise.

    404 sanity test — characters (GlobalNPC) sub-endpoint.
    """
    driver = _driver_returning(None)

    result = get_global_entity(driver, uid="nonexistent-global-npc-xyzzy")

    assert_that(result).contains_key("error")


@pytest.mark.unit
def test_MP_02_get_global_entity_not_found_location_returns_structured_error():
    """
    get_global_entity with a non-existent location uid must return a structured error.

    404 sanity test — locations (GlobalLocation) sub-endpoint.
    """
    driver = _driver_returning(None)

    result = get_global_entity(driver, uid="nonexistent-global-location-xyzzy")

    assert_that(result).contains_key("error")


@pytest.mark.unit
def test_MP_02_get_global_entity_not_found_item_returns_structured_error():
    """
    get_global_entity with a non-existent item uid must return a structured error.

    404 sanity test — items (GlobalItem) sub-endpoint.
    """
    driver = _driver_returning(None)

    result = get_global_entity(driver, uid="nonexistent-global-item-xyzzy")

    assert_that(result).contains_key("error")


@pytest.mark.unit
def test_MP_02_get_global_entity_not_found_faction_returns_structured_error():
    """
    get_global_entity with a non-existent faction uid must return a structured error.

    404 sanity test — factions (GlobalFaction) sub-endpoint.
    """
    driver = _driver_returning(None)

    result = get_global_entity(driver, uid="nonexistent-global-faction-xyzzy")

    assert_that(result).contains_key("error")


@pytest.mark.unit
def test_MP_02_get_entity_not_found_npc_returns_structured_error():
    """
    get_entity with a non-existent adventure-scoped NPC uid must return a structured error.

    404 sanity test — adventure NPCs (NPC) sub-endpoint.
    """
    driver = _driver_returning(None)

    result = get_entity(driver, uid="nonexistent-npc-xyzzy")

    assert_that(result).contains_key("error")


@pytest.mark.unit
def test_MP_02_get_entity_not_found_location_returns_structured_error():
    """
    get_entity with a non-existent adventure-scoped location uid must return a structured error.

    404 sanity test — adventure locations (Location) sub-endpoint.
    """
    driver = _driver_returning(None)

    result = get_entity(driver, uid="nonexistent-location-xyzzy")

    assert_that(result).contains_key("error")


@pytest.mark.unit
def test_MP_02_get_entity_not_found_item_returns_structured_error():
    """
    get_entity with a non-existent adventure-scoped item uid must return a structured error.

    404 sanity test — adventure items (Item) sub-endpoint.
    """
    driver = _driver_returning(None)

    result = get_entity(driver, uid="nonexistent-item-xyzzy")

    assert_that(result).contains_key("error")


@pytest.mark.unit
def test_MP_02_get_entity_not_found_faction_returns_structured_error():
    """
    get_entity with a non-existent adventure-scoped faction uid must return a structured error.

    404 sanity test — adventure factions (Faction) sub-endpoint.
    """
    driver = _driver_returning(None)

    result = get_entity(driver, uid="nonexistent-faction-xyzzy")

    assert_that(result).contains_key("error")
