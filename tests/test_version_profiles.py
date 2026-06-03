"""TC-VER-* version profile flags (detail checks in test_all_versions.py)."""

import pytest

from lib.geojson.profiles import ALL_VERSION_DIRS, get_profile

V74 = "农业基地_v7.4_GCJ02_L3_SingleMap"
V73 = "农业基地_v7.3_GCJ02_L3"
V71 = "农业基地_v7.1_GCJ02_MultiPolygon"
V70 = "农业基地_v7.0_GCJ02_Polygon"


def test_all_versions_registered():
    assert len(ALL_VERSION_DIRS) == 5


def test_unknown_version_raises():
    with pytest.raises(KeyError, match="Unknown"):
        get_profile("农业基地_v9.9_unknown")


def test_v70_legacy_only():
    p = get_profile(V70)
    assert p.write_legacy_merged
    assert not p.write_layered_l1_l2_l3
    assert not p.write_l1_flat_per_base


def test_v71_flat_only():
    p = get_profile(V71)
    assert p.write_l1_flat_per_base
    assert not p.write_legacy_merged
    assert not p.write_layered_l1_l2_l3


def test_v73_full_tree_with_legacy():
    p = get_profile(V73)
    assert p.write_legacy_merged and p.write_layered_l1_l2_l3


def test_v74_tree_no_legacy():
    p = get_profile(V74)
    assert p.write_layered_l1_l2_l3
    assert not p.write_legacy_merged
