"""
Graph Integrity unit tests — GI category.

These tests verify the structural rules that apply to every node in the
graph: uid uniqueness, required properties, tier values, and so on.
All tests in this module are pure unit tests. No DB required.
"""

import pytest
from unittest.mock import MagicMock, patch
from assertpy import assert_that

from test.fixtures.shadowdale import (
    make_elminster,
    make_pipe_of_elminster,
    make_adventure,
    make_elminster_context,
    make_jhaele,
    make_full_fixture,
)


# ── GI-01: uid uniqueness ─────────────────────────────────────────────────────

@pytest.mark.unit
def test_GI_01_uid_uniqueness():
    """
    Every node in the full fixture must have a unique uid.
    No two nodes may share a uid regardless of tier or label.
    """
    fixture = make_full_fixture()
    uids = [node["uid"] for node in fixture["nodes"]]
    unique_uids = set(uids)

    assert_that(uids).is_length(len(unique_uids))


# ── GI-02: tier property required on all nodes ────────────────────────────────

@pytest.mark.unit
def test_GI_02_tier_property_required():
    """
    Every node must have a 'tier' property.
    Valid values are: global, adventure, context.
    """
    VALID_TIERS = {"global", "adventure", "context"}
    fixture = make_full_fixture()

    for node in fixture["nodes"]:
        assert_that(node).contains_key("tier")
        assert_that(node["tier"]).described_as(
            f"Node {node['uid']} has invalid tier '{node.get('tier')}'"
        ).is_in(*VALID_TIERS)
