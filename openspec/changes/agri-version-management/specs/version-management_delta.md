# Delta：版本管理规范

**Change ID：** `agri-version-management`  
**影响范围：** `specs/geojson.md`、`specs/bigscreen.md`

---

## ADDED

### Requirement：GeoJSON 版本目录命名规范

GeoJSON 版本目录统一命名格式：

```
农业基地_v{major}.{minor}_{坐标系}_{几何类型描述}
```

| 占位符 | 规则 | 示例 |
|--------|------|------|
| `{major}` | 与 FVS 主版本对齐（大屏 v7 → GeoJSON v7.x） | `7` |
| `{minor}` | 每次 GeoJSON 格式升级递增 | `3` |
| `{坐标系}` | `GCJ02` 或 `WGS84` | `GCJ02` |
| `{几何类型描述}` | 简短标注：`Polygon`、`MultiPolygon`、`L3`（三层层级）等 | `L3` |

**当前生效版本**用 `✅` 标注，旧版本保留但标注为 `⚠ 归档` 或 `❌ 已废弃`。

#### 示例目录结构

```
农业基地-大疆测绘/
  农业基地_v7.3_GCJ02_L3/    ✅ 当前生效
  农业基地_v7.2_GCJ02_MP_L2/   🔧 L2 验证（基地/片区，类比省/市）
  农业基地_v7.1_GCJ02_ MultiPolygon/  ⚠ 归档（目录名含空格，已废弃）
  农业基地_v7.0_GCJ02_Polygon/  ❌ 已废弃
  农业基地_v6.9_WGS84_Polygon/  ❌ 已废弃（坐标系错误）
  农业基地_v6.0_TEST/            ❌ 已废弃
```

### Requirement：GeoJSON 版本更新流程补充

在 `specs/geojson.md` § 六「更新流程」末尾追加步骤：

```
6. 更新 openspec/release-notes-geojson.md：
   - 新增版本条目，记录 feature、bug、todo、可用性
   - 将旧生效版本状态改为 ⚠ 归档
   - 将新版本标注为 ✅ 当前生效
```

### Requirement：FVS 版本命名规范

FVS 文件统一命名格式（已在实际文件中体现，补充为正式规范）：

```
Agriculture_v{版本号}_{YYYYMMDD}_{UI描述}.fvs
```

- `{版本号}`：`major.minor` 形式，如 `v7.0`
- `{YYYYMMDD}`：保存日期
- `{UI描述}`：`UI_Green`、`UI_Blue`、`UI_Yellow` 等，或 `TEST`（测试版）

**部署规则：**
- `YXG-项目/1.农业大屏/` 保存**所有历史版本**（归档用）
- `YXG-项目/` 根目录**不保存**大屏 FVS 文件（历史混乱根因）
- 工具类 FVS（`KML转GEOJSON.fvs` 等）放入专用目录，不与大屏版本混放

### Requirement：FVS 版本更新流程补充

在 `specs/bigscreen.md` 末尾追加章节：

```markdown
## 七、FVS 版本管理

1. 每次保存新版本时，命名格式：`Agriculture_v{版本}_{YYYYMMDD}_{UI}.fvs`
2. 保存到 `YXG-项目/1.农业大屏/` 目录
3. 更新 `openspec/release-notes-fvs.md`：
   - 新增版本条目（feature/bug/todo/可用性）
   - 旧版本状态改为 ⚠ 归档
   - 新版本标注为 ✅ 当前生效
4. 更新 `openspec/specs/bigscreen.md` 变更历史表格
```

---

## MODIFIED

（无修改现有 requirement，仅新增）

---

## REMOVED

（无）
