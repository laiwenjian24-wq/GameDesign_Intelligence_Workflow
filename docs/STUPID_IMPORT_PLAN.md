# STUPID 第一批真实资料导入计划

本计划基于 `STUPID_ASSET_AUDIT.md` 的审计结果，用于第一阶段 Narrative Workflow 真实资料测试。

本次只新增导入配置，不修改原始文件，不修改 ingestion / metadata / retrieval / workflow 核心逻辑。

## 导入目标

第一批导入目标不是覆盖所有 STUPID 资料，而是验证当前 workflow 是否能稳定处理：

- Canon / Draft / Inspiration / Deprecated 区分；
- Context Pack 组装；
- continuity_checker 基于 Context Pack 的判断；
- Source Citation；
- Branch B 连续性；
- Mouse / Rin 角色关系；
- 未来 Dynamic Voice Context Builder 的输入质量。

## 第一批导入文件

配置文件：

```text
knowledge_base/import_manifest.json
```

共 14 个文件：

| # | 文件 | status | 主要测试用途 |
|---:|---|---|---|
| 1 | `STUPID游戏世界观设定集.md` | canon | 世界观规则、组织、审判日、Nexus |
| 2 | `时间线.md` | canon | 时间线、Branch B、伤势状态 |
| 3 | `故事大纲与角色设定.md` | canon | 角色关系、主线结构、未来 Voice Context |
| 4 | `章节.md` | canon | 章节顺序、当前版本边界 |
| 5 | `组织.md` | canon | IPW、Tyrell、Cancel、Second Foundation |
| 6 | `概念.md` | canon | SDFT、脑梯、残影等术语 |
| 7 | `世界观概述.md` | canon | Context Pack 高层摘要 |
| 8 | `任务设计_风筝.md` | canon | 《风筝》任务流程、分支、场景功能 |
| 9 | `Chapter 9 风筝.md` | canon | 正文语气、角色关系、场景节奏 |
| 10 | `RenPy_CG_接入映射.md` | canon | CG/分镜/分支映射、Rin 左腿、Mouse 右肩 |
| 11 | `RenPy_Demo_升级规划.md` | canon | Demo 范围、分支变量、实现意图 |
| 12 | `场景草稿_风筝（旧版）.md` | deprecated | 旧版右腿冲突、Deprecated Evidence |
| 13 | `分镜06_对白草稿.md` | draft | 安全屋对白、Voice Context；带旧右腿风险 |
| 14 | `灵感碎片.md` | inspiration | 灵感隔离、Lily/Rin 早期命名风险 |

## 为什么这些文件进入第一批

### 1. 足够覆盖当前 workflow 的核心能力

当前 workflow 已完成：

- ingestion；
- metadata；
- status priority；
- retrieval；
- citation；
- Context Pack；
- continuity_checker based on Context Pack。

这 14 个文件正好覆盖四类 status：

| status | 文件数 | 用途 |
|---|---:|---|
| canon | 11 | 事实依据 |
| deprecated | 1 | 旧设定冲突 |
| draft | 1 | 草稿参考 |
| inspiration | 1 | 灵感隔离 |

这比只导入 Canon 更适合测试系统，因为 Context Pack 和 continuity_checker 的价值就在于区分资料等级。

### 2. 能集中测试《风筝》Branch B

第一批资料围绕第九章《风筝》建立测试闭环：

```text
世界观规则
-> 角色关系
-> 任务设计
-> Branch B 状态
-> 安全屋 / Mombasa 场景
-> Rin 左腿 vs 旧版右腿
```

这正好对应当前 continuity_checker 已能处理的高价值测试点。

### 3. 为后续 Voice Context 预留素材

`Chapter 9 风筝.md` 和 `分镜06_对白草稿.md` 可以作为后续角色口吻测试的第一批文本。

注意：`分镜06_对白草稿.md` 当前只能作为 `draft`，不能作为 Canon，因为它带有 `contains_old_right_leg_conflict` 风险标签。

## 每个文件支持的功能测试

### Context Pack 测试

主要依赖：

- `STUPID游戏世界观设定集.md`
- `世界观概述.md`
- `故事大纲与角色设定.md`
- `任务设计_风筝.md`
- `RenPy_CG_接入映射.md`
- `场景草稿_风筝（旧版）.md`
- `灵感碎片.md`

预期能输出：

- `canon_context`
- `draft_reference`
- `inspiration_context`
- `deprecated_warnings`
- `evidence_sources`
- `restrictions`

### continuity_checker 测试

主要依赖：

- `时间线.md`
- `任务设计_风筝.md`
- `RenPy_CG_接入映射.md`
- `场景草稿_风筝（旧版）.md`
- `分镜06_对白草稿.md`

推荐测试输入：

```text
Mouse 在安全屋里给 Rin 的右腿换药。
```

期望：

- Canon Evidence 指向 Rin 左腿；
- Deprecated Evidence 指向旧版右腿；
- Draft Reference 显示对白草稿但不作为事实；
- Final Decision 采用 Canon；
- Rewrite Suggestion 改为左腿。

### Dynamic Voice Context Builder 未来测试

主要依赖：

- `故事大纲与角色设定.md`
- `Chapter 9 风筝.md`
- `分镜06_对白草稿.md`
- `任务设计_风筝.md`

可测试：

- Rin 在安全屋场景中的防御、迟疑、自嘲、有限信任；
- Mouse 的克制、回避、照护和愧疚；
- 对白是否破坏场景功能；
- 草稿对白与 Canon 状态是否冲突。

## 未来需要拆分的文件

以下文件第一批可以整体导入，但后续应拆分，否则检索噪声会增加。

### `STUPID游戏世界观设定集.md`

建议拆分为：

- `canon_world_sdft.md`
- `canon_judgment_day.md`
- `canon_organizations.md`
- `canon_nexus_series.md`
- `canon_locations.md`
- `canon_social_classes.md`

### `故事大纲与角色设定.md`

建议拆分为：

- `canon_character_mouse.md`
- `canon_character_rin.md`
- `canon_character_larry.md`
- `canon_character_snow.md`
- `canon_character_rain.md`
- `canon_relationship_mouse_rin.md`
- `canon_two_protagonist_lines.md`

### `时间线.md`

建议拆分为：

- `canon_timeline_main.md`
- `canon_timeline_mouse_line.md`
- `canon_timeline_larry_snow_line.md`
- `canon_timeline_kite_branch_b.md`

### `任务设计_风筝.md`

建议拆分为：

- `canon_kite_scene_flow.md`
- `canon_kite_branch_a.md`
- `canon_kite_branch_b.md`
- `canon_kite_branch_c.md`
- `canon_kite_state_changes.md`

### `分镜06_对白草稿.md`

建议拆分为：

- `draft_safehouse_dialogue_mouse_rin.md`
- `deprecated_safehouse_right_leg_version.md`

原因：该文件同时有 Voice Context 价值和旧伤势冲突风险，长期混在一起会污染检索。

## 暂不导入的资料

暂缓：

- PDF 作品集；
- docx 小说原稿；
- 原始 Word 转录；
- Prompt 类文件；
- 大量图片资源；
- Ren'Py 非主脚本；
- Obsidian / Ren'Py JSON；
- 招聘岗位资料；
- `script.rpy` 原文件。

其中 `script.rpy` 很有价值，但当前 workflow 尚未支持 `.rpy`。建议后续摘录关键 Branch B 段落为 Markdown 后导入。

## 下一步导入方案

### Step 1：确认 Manifest

检查：

```text
knowledge_base/import_manifest.json
```

重点确认：

- 文件路径是否存在；
- `场景草稿_风筝（旧版）.md` 是否为 `deprecated`；
- `分镜06_对白草稿.md` 是否为 `draft`，并带有 `contains_old_right_leg_conflict`；
- `灵感碎片.md` 是否为 `inspiration`。

### Step 2：复制文件到 raw_assets

当前 ingestion 还不会读取 `import_manifest.json`，所以实际导入仍需要把文件复制到：

```text
knowledge_base/raw_assets/
```

建议保留原文件名，不修改原始文件。

### Step 3：运行 ingestion

在项目根目录执行：

```powershell
& 'E:\Desktop\python\python.exe' main.py
```

输出应更新：

```text
knowledge_base/processed/metadata.jsonl
```

### Step 4：运行检索和检查

Context Pack：

```powershell
& 'E:\Desktop\python\python.exe' main.py context "Mouse 在安全屋里给 Rin 的右腿换药。"
```

Continuity Check：

```powershell
& 'E:\Desktop\python\python.exe' main.py check "Mouse 在安全屋里给 Rin 的右腿换药。"
```

Search：

```powershell
& 'E:\Desktop\python\python.exe' main.py search "Branch B Rin 左腿 Mouse 右肩 Mombasa"
```

## 重要限制

`import_manifest.json` 当前只是导入计划配置，不会自动影响 ingestion 结果。

也就是说，当前系统仍然主要依靠：

- 文件名；
- 目录名；
- 文本关键词；
- 简单规则。

如果要让 manifest 中的 status / tags / reason 真正覆盖自动 metadata，需要后续再做 manifest-aware ingestion。但这属于新功能，本轮没有实现。

