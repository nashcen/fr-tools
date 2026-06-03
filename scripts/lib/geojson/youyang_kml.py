"""Map 重庆酉阳 KML placemarks to Excel 片区名称."""

from __future__ import annotations

import re

from lib.geojson import plot_matching


def resolve_district(
    placemark_name: str,
    contract: str,
    contract_map: dict[str, set[str]],
    all_districts: list[str],
) -> str | None:
    districts = contract_map.get(contract)
    if districts:
        if len(districts) == 1:
            return next(iter(districts))
        matched = _match_among_districts(placemark_name, sorted(districts))
        if matched:
            return matched

    matched = _match_among_districts(placemark_name, all_districts)
    if matched:
        return matched

    if contract == "老龙无合同编号" and "老龙" in placemark_name:
        if "龙沙" in all_districts:
            return "龙沙"
    return None


def _match_among_districts(name: str, districts: list[str]) -> str | None:
    normalized = plot_matching.normalize_for_match(name)
    for district in districts:
        if district in name or district in normalized:
            return district
        if normalized.startswith(district):
            return district
    # 红阳 → 小河（盘点表地块名）
    if "红阳" in name or "红阳" in normalized:
        if "小河" in districts:
            return "小河"
    if "流石" in name and "小河" in districts:
        return "小河"
    if "王大志" in name and "平桥" in districts:
        return "平桥"
    return None
