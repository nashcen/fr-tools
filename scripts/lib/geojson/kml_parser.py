"""Parse DJI survey KML into polygon records."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from lib.geojson.kml_sources import DISCARD_COLORS

NS = "http://www.opengis.net/kml/2.2"
_Q = lambda tag: f"{{{NS}}}{tag}"


def kml2hex(color: str) -> str:
    c = color.lstrip("#")
    return f"#{c[6:8]}{c[4:6]}{c[2:4]}".lower() if len(c) == 8 else c


def parse_kml(fpath: str) -> list[dict]:
    tree = ET.parse(fpath)
    root = tree.getroot()

    styles: dict[str, str] = {}
    for style in root.iter(_Q("Style")):
        sid = style.get("id", "")
        poly_style = style.find(_Q("PolyStyle"))
        if poly_style is not None:
            color_el = poly_style.find(_Q("color"))
            if color_el is not None and color_el.text:
                styles[f"#{sid}"] = kml2hex(color_el.text)

    results: list[dict] = []

    def walk(element, path: list[str]) -> None:
        for child in element:
            tag = child.tag.replace(f"{{{NS}}}", "")
            if tag in ("Folder", "Document"):
                name_el = child.find(_Q("name"))
                folder_name = (
                    name_el.text.strip()
                    if name_el is not None and name_el.text
                    else ""
                )
                walk(child, path + ([folder_name] if folder_name else []))
            elif tag == "Placemark":
                name_el = child.find(_Q("name"))
                name = name_el.text.strip() if name_el is not None and name_el.text else ""
                style_url = child.find(_Q("styleUrl"))
                color = ""
                if style_url is not None and style_url.text:
                    color = styles.get(style_url.text.strip(), "")
                polygon = child.find(_Q("Polygon"))
                if polygon is None:
                    continue
                outer = polygon.find(
                    f'.//{_Q("outerBoundaryIs")}/{_Q("LinearRing")}/{_Q("coordinates")}'
                )
                if outer is None or not outer.text:
                    continue
                coords = []
                for point in outer.text.strip().split():
                    parts = point.split(",")
                    try:
                        coords.append([float(parts[0]), float(parts[1])])
                    except (ValueError, IndexError):
                        continue
                if len(coords) < 3:
                    continue
                path_text = " ".join(path).lower()
                results.append(
                    {
                        "name": name,
                        "path": list(path),
                        "color": color,
                        "is_seed": any(k in path_text for k in ("种植", "种面")),
                        "coords": coords,
                    }
                )

    walk(root, [])
    return results


def should_keep(placemark: dict) -> bool:
    if "测绘" in " ".join(placemark["path"]):
        return not placemark["is_seed"]
    return not placemark["is_seed"] and placemark["color"] not in DISCARD_COLORS
