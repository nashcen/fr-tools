"""Match KML placemarks to Excel plot names."""

from __future__ import annotations

import re


def normalize_for_match(raw: str) -> str:
    name = re.sub(r"-+\d+\.?\d*亩?$", "", raw)
    name = re.sub(r"\d+\.?\d*亩$", "", name)
    name = re.sub(r"地块\d+\.?\d*亩?$", "地块", name)
    name = re.sub(r"（[\d\.]+亩?）$", "", name)
    name = re.sub(r"T\d+$", "", name)
    name = re.sub(r"^（(.+)）$", r"\1", name)
    name = re.sub(r"地块$", "", name)
    name = re.sub(r"村$", "", name)
    return name.strip()


def assign_to_plot(district: str, placemark_name: str, plots: list[str]) -> str:
    if not plots:
        return district
    if len(plots) == 1:
        return plots[0]
    normalized = normalize_for_match(placemark_name)
    if normalized in plots:
        return normalized
    for plot in plots:
        if plot in normalized or normalized in plot:
            return plot
    return normalized or placemark_name
