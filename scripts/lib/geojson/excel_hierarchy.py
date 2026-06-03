"""Load (基地, 片区) → [地块名] from 农业资产盘点明细.xlsx."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path


def load_excel_hierarchy(excel_path: Path) -> dict[tuple[str, str], list[str]]:
    try:
        import openpyxl
    except ImportError:
        print("  ⚠ openpyxl 未安装（pip install openpyxl），跳过 Excel 层级")
        return {}

    if not excel_path.is_file():
        print(f"  ⚠ Excel 不存在: {excel_path}")
        return {}

    wb = openpyxl.load_workbook(excel_path, read_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    col = {v: i for i, v in enumerate(header) if v}
    result: dict[tuple[str, str], list[str]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    for row in rows[1:]:
        base = row[col["基地名称"]] if "基地名称" in col else None
        district = row[col["片区名称"]] if "片区名称" in col else None
        plot = row[col["地块名称"]] if "地块名称" in col else None
        if base and district and plot:
            key = (base, district, plot)
            if key not in seen:
                result[(base, district)].append(plot)
                seen.add(key)
    return dict(result)
