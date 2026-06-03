"""
ods_ag_base_v2 数据库更新脚本
================================
功能：
  将《农业资产盘点明细.xlsx》中的今年盘点数据整合入库，
  更新/扩展 ods_ag_base_v2 表。

变更说明：
  1. 新增字段：基地编码、区域编码、片区编码（原有字段全部保留）
  2. 区域名称：更新为新区域名称（新旧均保存）
  3. 新增字段 区域名称(旧)：保留旧区域名称
  4. 片区编号：按基地→区域→片区的空间局部性重新排序（1-80连续）
  5. 株数数据：全部沿用旧表数据
  6. 坐标：更新为 GeoJSON 多边形重心（GCJ-02）

执行前提：
  - FineReport 已启动（ods_ag_base_v2 可访问）
  - Excel 文件路径正确

依赖：
  pip install openpyxl（如果 openpyxl 版本兼容）
  或直接用 zipfile + xml 解析（已内置，无需第三方）
"""

import os
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

# ─── 配置 ─────────────────────────────────────────────────────────────────────

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
EXCEL_PATH = os.path.join(_REPO_ROOT, 'data', '农业资产盘点明细.xlsx')
DB = dict(host='172.17.4.4', port=3310, user='bigdata',
          pwd='yxgbigdata@YXG321', db='yxg_bigscreen')

# 片区编号重新排序的基地顺序
BASE_ORDER = {'CS0': 0, 'WS0': 1, 'BS0': 2, 'YY0': 3}

# 单位名称默认值
UNIT_MAP = {
    '浙江常山': '浙江柚香谷投资管理有限公司',
    '四川武胜': '四川武胜柚香谷农业公司',
    '广西百色': '广西百色柚香谷农业公司',
    '重庆酉阳': '重庆酉阳柚香谷农业公司',
}


# ─── Excel 解析（无需 openpyxl）─────────────────────────────────────────────

def _parse_excel(path: str) -> tuple[list, list]:
    """返回 (sheet2_rows, sheet3_rows)，其中 rows[0] 为表头"""
    with zipfile.ZipFile(path) as z:
        ss = ET.fromstring(z.read('xl/sharedStrings.xml'))
        shared = [''.join(
            x.text or '' for x in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
        ) for si in ss.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si')]

        def gc(c):
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            if v is None: return None
            return shared[int(v.text)] if c.get('t', '') == 's' else v.text

        def ci(ref):
            col = re.match(r'([A-Z]+)', ref).group(1)
            idx = 0
            for ch in col: idx = idx * 26 + (ord(ch) - 64)
            return idx - 1

        def parse_sheet(n):
            sh = ET.fromstring(z.read(f'xl/worksheets/sheet{n}.xml'))
            rows = []
            for row_el in sh.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                cells = row_el.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c')
                if not cells: continue
                mc = max(ci(c.get('r', 'A1')) for c in cells)
                row = [None] * (mc + 1)
                for c in cells:
                    ref = c.get('r', '')
                    if ref: row[ci(ref)] = gc(c)
                rows.append(row)
            return rows

        return parse_sheet(2), parse_sheet(3)   # sheet2=土地盘点表, sheet3=重庆酉阳


def _make_h(header): return {v: i for i, v in enumerate(header) if v}


def _sv(row, h, key):
    i = h.get(key)
    v = row[i] if (i is not None and i < len(row)) else None
    return str(v).strip() if v is not None else ''


def _sf(row, h, key):
    try: return float(_sv(row, h, key) or 0)
    except: return 0.0


# ─── DB 操作 ──────────────────────────────────────────────────────────────────

def mysql_query(sql: str) -> list:
    r = subprocess.run(
        ['mysql', f'-h{DB["host"]}', f'-P{DB["port"]}', f'-u{DB["user"]}',
         f'-p{DB["pwd"]}', DB['db'], '--batch', '--skip-column-names', '-e', sql],
        capture_output=True, text=True, env=os.environ
    )
    return [l.split('\t') for l in r.stdout.strip().split('\n') if l]


def mysql_exec(sql: str) -> bool:
    r = subprocess.run(
        ['mysql', f'-h{DB["host"]}', f'-P{DB["port"]}', f'-u{DB["user"]}',
         f'-p{DB["pwd"]}', DB['db']],
        input=sql, capture_output=True, text=True, env=os.environ
    )
    if r.returncode != 0:
        print(f'  SQL ERROR: {r.stderr[:300]}')
    return r.returncode == 0


# ─── 主逻辑 ───────────────────────────────────────────────────────────────────

def main():
    print('1. 读取 Excel 数据...')
    sh2, sh3 = _parse_excel(EXCEL_PATH)

    def aggregate(sheet, base_filter=None):
        h = _make_h(sheet[0])
        d = {}
        for row in sheet[1:]:
            base = _sv(row, h, '基地名称')
            pq = _sv(row, h, '片区名称')
            if not base or not pq: continue
            if base_filter and base != base_filter: continue
            key = (base, pq)
            if key not in d:
                d[key] = {
                    '省': _sv(row, h, '省'), '市': _sv(row, h, '市'),
                    '县': _sv(row, h, '县'), '镇': _sv(row, h, '镇'),
                    '基地编码': _sv(row, h, '基地编码'), '基地名称': base,
                    '区域编码': _sv(row, h, '区域编码'),
                    '区域名称': _sv(row, h, '区域名称'),
                    '区域名称(旧)': _sv(row, h, '区域名称(旧)'),
                    '区域负责人': _sv(row, h, '区域负责人'),
                    '区域联系方式': _sv(row, h, '区域联系方式'),
                    '片区编码': _sv(row, h, '片区编码'), '片区名称': pq,
                    '片区负责人': _sv(row, h, '片区负责人'),
                    '片区联系方式': _sv(row, h, '片区联系方式'),
                    '种植亩数': 0.0, 'dk': set(), 'zt': set(),
                }
            x = d[key]
            x['种植亩数'] += _sf(row, h, '种植面积')
            dk = _sv(row, h, '地块名称')
            if dk: x['dk'].add(dk)
            zt = _sv(row, h, '种植时间')
            if zt: x['zt'].add(zt)
        return d

    xl2 = aggregate(sh2)
    xl3 = aggregate(sh3, '重庆酉阳')
    all_xl = {**xl2, **xl3}
    print(f'   Excel 片区数: {len(all_xl)}')

    print('2. 加载旧表数据（株数、坐标保留）...')
    OLD_FIELDS = ['片区编号', '基地名称', '区域名称', '片区名称', '片区负责人',
                  '片区联系方式', '片区地址', '片区经度', '片区纬度', '地块名称',
                  '种植时间', '种植亩数', '种植株数', '大树株数', '中树株数',
                  '小树株数', '单位名称', '省', '市', '县', '镇']
    old_raw = mysql_query('SELECT `' + '`,`'.join(OLD_FIELDS) + '` FROM ods_ag_base_v2_20260602')
    old = {}
    for r in old_raw:
        if len(r) < len(OLD_FIELDS): continue
        d = {k: (None if v == 'NULL' else v) for k, v in zip(OLD_FIELDS, r)}
        try: d['片区编号'] = int(d['片区编号'])
        except: continue
        old[(d['基地名称'], d['片区名称'])] = d

    print('3. 构建最终记录...')
    records = []
    for (base, pq), xl in all_xl.items():
        o = old.get((base, pq))
        records.append({
            '省': xl['省'] or (o['省'] if o else ''),
            '市': xl['市'] or (o['市'] if o else ''),
            '县': xl['县'] or (o['县'] if o else ''),
            '镇': xl['镇'] or (o['镇'] if o else ''),
            '基地编码': xl['基地编码'],
            '基地名称': base,
            '区域编码': xl['区域编码'],
            '区域名称(旧)': xl.get('区域名称(旧)') or (o['区域名称'] if o else ''),
            '区域名称': xl['区域名称'],
            '区域负责人': xl['区域负责人'],
            '区域联系方式': xl['区域联系方式'],
            '片区编码': xl['片区编码'],
            '片区名称': pq,
            '片区负责人': xl['片区负责人'] or (o['片区负责人'] if o else ''),
            '片区联系方式': xl['片区联系方式'] or (o['片区联系方式'] if o else ''),
            '片区地址': o['片区地址'] if o else None,
            '片区经度': o['片区经度'] if o else None,
            '片区纬度': o['片区纬度'] if o else None,
            '地块名称': '|'.join(sorted(xl['dk'])) or (o['地块名称'] if o else None),
            '种植时间': (o['种植时间'] if o else None) or '|'.join(sorted(xl['zt'])),
            '种植亩数': round(xl['种植亩数'], 2) if xl['种植亩数'] else (
                float(o['种植亩数']) if o and o.get('种植亩数') else None),
            '种植株数': o['种植株数'] if o else None,
            '大树株数': o['大树株数'] if o else None,
            '中树株数': o['中树株数'] if o else None,
            '小树株数': o['小树株数'] if o else None,
            '单位名称': (o['单位名称'] if o and o.get('单位名称') else None) or UNIT_MAP.get(base),
        })

    # 按空间局部性排序并重新编号
    records.sort(key=lambda r: (
        BASE_ORDER.get(r['基地编码'], 9),
        r['区域编码'] or 'ZZZ',
        r['片区编码'] or 'ZZZ_' + r['片区名称'],
        r['片区名称']
    ))
    for i, r in enumerate(records, 1):
        r['片区编号'] = i

    print(f'   总记录数: {len(records)}')

    print('4. 执行 DDL 变更（新增字段）...')
    mysql_exec("""
ALTER TABLE `ods_ag_base_v2`
  ADD COLUMN IF NOT EXISTS `基地编码` varchar(20) DEFAULT NULL COMMENT '基地编码' AFTER `镇`,
  ADD COLUMN IF NOT EXISTS `区域编码` varchar(20) DEFAULT NULL COMMENT '区域编码' AFTER `基地编码`,
  ADD COLUMN IF NOT EXISTS `区域名称(旧)` varchar(255) DEFAULT NULL COMMENT '区域名称（旧）' AFTER `区域编码`,
  ADD COLUMN IF NOT EXISTS `片区编码` varchar(20) DEFAULT NULL COMMENT '片区编码' AFTER `区域名称`;
""")

    print('5. TRUNCATE + INSERT...')
    INSERT_COLS = [
        '省', '市', '县', '镇', '基地编码', '基地名称', '区域编码',
        '区域名称(旧)', '区域名称', '区域负责人', '区域联系方式',
        '片区编号', '片区编码', '片区名称', '片区负责人', '片区联系方式', '片区地址',
        '片区经度', '片区纬度', '地块名称', '种植时间', '种植亩数',
        '种植株数', '大树株数', '中树株数', '小树株数', '单位名称'
    ]

    def v(val):
        if val is None or val == '': return 'NULL'
        if isinstance(val, (int, float)): return str(val)
        return "'" + str(val).replace("\\", "\\\\").replace("'", "\\'") + "'"

    rows_sql = ['  (' + ','.join(v(r.get(c)) for c in INSERT_COLS) + ')' for r in records]
    sql = ('TRUNCATE TABLE `ods_ag_base_v2`;\n\n'
           'INSERT INTO `ods_ag_base_v2`\n'
           '  (`' + '`,`'.join(INSERT_COLS) + '`)\nVALUES\n'
           + ',\n'.join(rows_sql) + ';')

    if mysql_exec(sql):
        print(f'   ✅ 已写入 {len(records)} 条记录')

    # 验证
    cnt = mysql_query('SELECT COUNT(*) FROM ods_ag_base_v2')
    print(f'   验证行数: {cnt[0][0] if cnt else "?"}')


if __name__ == '__main__':
    main()
