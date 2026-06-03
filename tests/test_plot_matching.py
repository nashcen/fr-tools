"""TC-MCH-* plot name matching."""

from lib.geojson.plot_matching import assign_to_plot, normalize_for_match


def test_normalize_strips_area_suffix():
    assert normalize_for_match("路里坑1.38亩") == "路里坑"


def test_assign_single_district_as_plot():
    assert assign_to_plot("九湾", "测绘图斑A", []) == "九湾"


def test_assign_exact_plot_name():
    plots = ["路里坑", "大埂"]
    assert assign_to_plot("路里坑", "路里坑", plots) == "路里坑"
