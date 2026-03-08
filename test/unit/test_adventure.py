"""
Adventure CRUD unit tests — Create operations.

Tests input validation and error-response shape for create_adventure and
get_adventure.  All tests are pure unit tests: the Neo4j driver is fully
mocked and the DB is never touched.

Requirement coverage:
    MP-02  All tool errors must return structured error content blocks, not exceptions.
    MP-03  Every tool must validate input parameters before executing any DB operation.
    MP-04  Tools that write data must return the uid(s) of created or modified nodes.
"""

import pytest
from unittest.mock import MagicMock
from assertpy import assert_that

from dnd_mcp.tools.adventure import create_adventure, get_adventure


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mock_driver():
    """Return a MagicMock representing a connected Neo4j driver."""
    return MagicMock()


VALID_ADVENTURE = {
    "uid": "shadowdale-2024",
    "name": "Shadowdale: The Troubles",
    "status": "draft",
    "setting": "Forgotten Realms",
    "tags": ["intrigue", "investigation", "tier-1"],
    "summary": "A political intrigue adventure set in Shadowdale.",
}


# ── MP-03: Null / None values ─────────────────────────────────────────────────

@pytest.mark.unit
def test_MP_03_create_adventure_null_uid_returns_error():
    """
    create_adventure with uid=None must return a structured error dict
    without touching the driver.
    """
    driver = _mock_driver()
    result = create_adventure(driver, uid=None, name="Test Adventure", status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_null_name_returns_error():
    """create_adventure with name=None must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(driver, uid="test-adventure", name=None, status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_null_status_returns_error():
    """create_adventure with status=None must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(driver, uid="test-adventure", name="Test Adventure", status=None)

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


# ── MP-03: Zero / empty-string values ────────────────────────────────────────

@pytest.mark.unit
def test_MP_03_create_adventure_zero_integer_uid_returns_error():
    """
    create_adventure with uid=0 (integer zero) must return a structured error.
    uid must be a non-empty string.
    """
    driver = _mock_driver()
    result = create_adventure(driver, uid=0, name="Test Adventure", status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_zero_float_uid_returns_error():
    """create_adventure with uid=0.0 (float zero) must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(driver, uid=0.0, name="Test Adventure", status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_empty_string_uid_returns_error():
    """
    create_adventure with uid="" must return a structured error.
    An empty string is not a valid unique identifier.
    """
    driver = _mock_driver()
    result = create_adventure(driver, uid="", name="Test Adventure", status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_whitespace_uid_returns_error():
    """
    create_adventure with uid consisting only of whitespace must return an error.
    Whitespace-only strings are not valid uids.
    """
    driver = _mock_driver()
    result = create_adventure(driver, uid="   ", name="Test Adventure", status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_empty_string_name_returns_error():
    """create_adventure with name="" must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(driver, uid="test-adventure", name="", status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_zero_integer_name_returns_error():
    """create_adventure with name=0 (integer) must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(driver, uid="test-adventure", name=0, status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


# ── MP-03: Wrong type — string field receives int or float ───────────────────

@pytest.mark.unit
def test_MP_03_create_adventure_integer_uid_returns_error():
    """
    create_adventure with uid=42 (non-zero integer) must return a structured error.
    uid must be a string.
    """
    driver = _mock_driver()
    result = create_adventure(driver, uid=42, name="Test Adventure", status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_float_uid_returns_error():
    """create_adventure with uid=3.14 (float) must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(driver, uid=3.14, name="Test Adventure", status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_float_name_returns_error():
    """create_adventure with name=3.14 (float) must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(driver, uid="test-adventure", name=3.14, status="draft")

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_integer_tags_returns_error():
    """
    create_adventure with tags=42 (integer instead of list) must return a structured error.
    tags must be a list of strings.
    """
    driver = _mock_driver()
    result = create_adventure(
        driver,
        uid="test-adventure",
        name="Test Adventure",
        status="draft",
        tags=42,
    )

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_float_tags_returns_error():
    """create_adventure with tags=1.5 (float) must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(
        driver,
        uid="test-adventure",
        name="Test Adventure",
        status="draft",
        tags=1.5,
    )

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_invalid_status_value_returns_error():
    """
    create_adventure with an unrecognized status value must return a structured error.
    Valid values are: draft, in-progress, complete.
    """
    driver = _mock_driver()
    result = create_adventure(
        driver,
        uid="test-adventure",
        name="Test Adventure",
        status="published",
    )

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_integer_status_returns_error():
    """create_adventure with status=1 (integer) must return a structured error."""
    driver = _mock_driver()
    result = create_adventure(
        driver,
        uid="test-adventure",
        name="Test Adventure",
        status=1,
    )

    assert_that(result).contains_key("error")
    driver.session.assert_not_called()


# ── MP-03: Missing required arguments ────────────────────────────────────────

@pytest.mark.unit
def test_MP_03_create_adventure_missing_uid_returns_error():
    """
    create_adventure called without uid must return a structured error or raise
    TypeError.  Either response is acceptable; the function must never silently
    create a node with a missing uid.
    """
    driver = _mock_driver()
    try:
        result = create_adventure(driver, name="Test Adventure", status="draft")
        assert_that(result).contains_key("error")
    except TypeError:
        pass  # acceptable — required positional argument omitted
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_missing_name_returns_error():
    """
    create_adventure called without name must return a structured error or raise TypeError.
    """
    driver = _mock_driver()
    try:
        result = create_adventure(driver, uid="test-adventure", status="draft")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


@pytest.mark.unit
def test_MP_03_create_adventure_missing_status_returns_error():
    """
    create_adventure called without status must return a structured error or raise TypeError.
    """
    driver = _mock_driver()
    try:
        result = create_adventure(driver, uid="test-adventure", name="Test Adventure")
        assert_that(result).contains_key("error")
    except TypeError:
        pass
    driver.session.assert_not_called()


# ── MP-03: Extra / unexpected arguments ──────────────────────────────────────

@pytest.mark.unit
def test_MP_03_create_adventure_extra_args_does_not_raise():
    """
    create_adventure called with extra unknown keyword arguments must not raise
    an unhandled exception.  The function may ignore extras or return a structured
    error, but must never propagate an unhandled exception.
    """
    driver = _mock_driver()
    try:
        result = create_adventure(
            driver,
            uid="test-adventure",
            name="Test Adventure",
            status="draft",
            unknown_field="unexpected",
            another_extra=999,
        )
        # If a value is returned it must be a dict (success or error shape).
        assert_that(result).is_instance_of(dict)
    except TypeError:
        # Acceptable if the function uses explicit keyword params.
        pass
    except Exception as exc:
        pytest.fail(f"Unexpected exception type raised for extra args: {type(exc).__name__}: {exc}")


# ── MP-04: Successful creation returns uid ────────────────────────────────────

@pytest.mark.unit
def test_MP_04_create_adventure_success_returns_uid():
    """
    A fully valid create_adventure call must return a dict containing 'uid'.
    The driver is mocked; this test verifies the response shape, not DB behaviour.
    """
    driver = _mock_driver()
    # Simulate the driver session returning the created node's uid.
    session = driver.session.return_value.__enter__.return_value
    session.run.return_value.single.return_value = {"uid": "shadowdale-2024"}

    result = create_adventure(driver, **VALID_ADVENTURE)

    assert_that(result).contains_key("uid")
    assert_that(result["uid"]).is_equal_to("shadowdale-2024")


# ── MP-02: Not-found (404 sanity) — Adventures ───────────────────────────────

@pytest.mark.unit
def test_MP_02_get_adventure_not_found_returns_structured_error():
    """
    Requesting a non-existent adventure uid must return a structured error dict
    containing an 'error' key.  It must never raise an unhandled exception.

    404 sanity test — adventures sub-endpoint.
    """
    driver = _mock_driver()
    # Simulate driver returning no result (node not found).
    session = driver.session.return_value.__enter__.return_value
    session.run.return_value.single.return_value = None

    result = get_adventure(driver, uid="nonexistent-adventure-uid-xyzzy")

    assert_that(result).contains_key("error")
