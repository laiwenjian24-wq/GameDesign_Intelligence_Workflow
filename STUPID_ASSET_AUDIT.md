# STUPID Asset Audit

扫描范围：

- `E:\desktop\游戏策划`
- `E:\desktop\stupid创作及其素材`

扫描目标格式：

- `.md`
- `.txt`
- `.docx`
- `.pdf`
- `.json`
- `.rpy`
- `.xlsx`
- `.png`
- `.jpg`
- `.jpeg`

本报告只做资产审计和第一批导入建议，不修改 Narrative Workflow 代码。

## 项目资料概览

### 文件数量概览

| 扩展名 | 数量 | 初步用途判断 |
|---|---:|---|
| `.md` | 94 | 世界观、角色、章节、任务、Prompt、作品集说明、旧稿 |
| `.txt` | 27 | 设定碎片、灵感碎片、授权说明、Ren'Py 日志/库说明 |
| `.docx` | 19 | 小说原稿、早期设定、投递材料源文件 |
| `.pdf` | 9 | 作品集、章节导出、投递版资料 |
| `.json` | 10 | Obsidian 配置、Ren'Py 项目/存档数据 |
| `.rpy` | 4 | Ren'Py Demo 脚本、界面、配置 |
| `.xlsx` | 1 | 招聘/岗位表，不属于叙事资料 |
| `.png` | 427 | 角色、场景、CG、道具、城市、UI、食物、服饰、交通工具等视觉资料 |
| `.jpg` | 82 | 作品集导出图、招聘岗位图、视觉素材 |

### 主要资产簇

| 资产簇 | 路径 | 文件用途 | 初步类型 |
|---|---|---|---|
| 核心笔记库 | `E:\desktop\stupid创作及其素材\stupid笔记` | 世界观、时间线、章节、角色、任务、正文稿、旧稿 | worldbuilding / timeline / character / scene / branch |
| 原始 Word 转录 | `E:\desktop\stupid创作及其素材\stupid笔记\原始Word转录` | 旧 Word 原稿转 Markdown | deprecated / draft |
| 原始 docx 小说稿 | `E:\desktop\stupid创作及其素材\stupid` | 章节 docx、总稿 docx | draft / deprecated，需要转换后再导入 |
| 设定碎片 txt | `E:\desktop\stupid创作及其素材\stupid\stupid project\设定` | 概念、组织、理论碎片 | worldbuilding / organization |
| 灵感碎片 | `E:\desktop\stupid创作及其素材\stupid\stupid project\灵感碎片` | 音乐、电影、散文灵感、早期素材 | inspiration |
| Ren'Py Demo | `E:\desktop\stupid创作及其素材\stupid_kite\KITE\game` | `script.rpy`、界面脚本、CG、头像、道具 | branch / dialogue / visual_reference |
| STUPID 作品集整理 | `E:\desktop\游戏策划\STUPID作品集整理` | 任务设计、CG 映射、角色/道具结构稿、Demo 规划 | branch / scene / visual_reference / prompt |
| 世界观投递作品集 | `E:\desktop\游戏策划\世界观文案岗位投递作品集` | 世界观文案、逐页稿、面试稿、素材索引 | worldbuilding / portfolio |
| V2 作品集 | `E:\desktop\游戏策划\世界观文案岗位投递作品集_V2` | 更新版 PDF、逐页文本、图片 assets | worldbuilding / visual_reference |
| 视觉设定图 | `E:\desktop\游戏策划\人物设定图`、`场景设定图`、`城市概念设定图`、`道具设定图` 等 | 角色、场景、城市、道具、食物、服饰、交通工具 | visual_reference |

### 当前 workflow 适配判断

当前 Narrative Workflow 已支持 `.md` / `.txt` 导入，暂未支持 `.docx`、`.pdf`、`.rpy`、`.xlsx`、图片内容解析。

因此第一批真实测试资料建议优先选择：

- 已经是 `.md` / `.txt` 的核心设定文件；
- 能明确区分 `canon` / `draft` / `deprecated` / `pattern` / `inspiration` 的文件；
- 能覆盖《风筝》A/B/C 分支、Rin 伤势、Mouse 伤势、安全屋、重庆森林、Mombasa、角色关系等连续性检查点；
- 暂不直接导入大量图片、PDF、docx、rpy，除非先人工转成 Markdown 摘要。

## 推荐第一批导入列表

建议第一批导入 16 个文件。优先级顺序已按测试价值排列。

### 1. 世界观总设定

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\STUPID游戏世界观设定集.md`
- 内容作用：总世界观、SDFT、审判日、阶级、组织、Nexus、冬眠者社区等核心设定。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `worldbuilding`, `timeline`, `organization`
  - related_characters: `Larry`, `Mouse`, `Rain`, `Snow`, `Rin`
  - related_locations: `重庆森林`, `左岸`, `鲁尔区`, `Mombasa`, `泰瑞尔核心区`
  - tags: `worldbuilding`, `SDFT`, `Judgment Day`, `Nexus`, `Tyrell`, `Cancel`, `IPW`
- 推荐status：`canon`

### 2. 时间线

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\时间线.md`
- 内容作用：主线时间线、章节顺序、非线性顺序说明、第九章《风筝》事件状态。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `timeline`, `branch`, `scene`
  - related_characters: `Mouse`, `Rin`, `Larry`, `Snow`, `Rain`
  - related_branches: `A`, `B`, `C`
  - tags: `timeline`, `chapter_order`, `branch_b`, `canon`
- 推荐status：`canon`

### 3. 故事大纲与角色设定

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\故事大纲与角色设定.md`
- 内容作用：角色背景、两条主线、章节结构、第九章 Demo 说明、角色关系。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `character`, `branch`, `worldbuilding`, `timeline`
  - related_characters: `Mouse`, `Rin`, `Larry`, `Snow`, `Rain`, `Julie`
  - related_branches: `A`, `B`, `C`
  - tags: `character`, `story_outline`, `relationship`, `kite`
- 推荐status：`canon`

### 4. 章节索引

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\章节.md`
- 内容作用：章节顺序、已完成章节、旧稿待重排说明；可用于判断章节连续性。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `timeline`, `branch`
  - related_characters: `Mouse`, `Rin`, `Larry`, `Snow`
  - tags: `chapter_index`, `timeline`, `canon`
- 推荐status：`canon`

### 5. 组织设定

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\组织.md`
- 内容作用：IPW、脑梯、泰瑞尔、堪恩索、第二基地等组织关系。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `worldbuilding`
  - related_locations: `泰瑞尔核心区`, `堪恩索控制区`
  - tags: `organization`, `IPW`, `Tyrell`, `Cancel`, `Second Foundation`
- 推荐status：`canon`

### 6. 概念设定

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\概念.md`
- 内容作用：残影、脑梯、获能者、SDFT 等概念解释。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `worldbuilding`
  - tags: `concept`, `SDFT`, `Brain Ladder`, `Doublt Shadow`
- 推荐status：`canon`

### 7. 世界观概述

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\世界观概述.md`
- 内容作用：更短的世界观入口文档，适合作为 Context Pack 的高层摘要来源。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `worldbuilding`
  - tags: `overview`, `worldbuilding`, `canon`
- 推荐status：`canon`

### 8. 任务设计《风筝》

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\任务设计_风筝.md`
- 内容作用：《风筝》任务流程、分支、场景、玩家选择、任务后果。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `branch`, `scene`, `dialogue`
  - related_characters: `Mouse`, `Rin`, `Larry`, `Rain`
  - related_locations: `鲁尔区`, `红磡隧道`, `重庆森林`, `Mombasa`
  - related_branches: `A`, `B`, `C`
  - tags: `kite`, `branch`, `scene_flow`, `quest_design`
- 推荐status：`canon`

### 9. RenPy CG 接入映射

- 文件路径：`E:\desktop\游戏策划\STUPID作品集整理\RenPy_CG_接入映射.md`
- 内容作用：分镜、CG、分支、场景功能的映射；明确 B 线中 Mouse 右肩负伤、Rin 左腿擦伤、Mombasa 安全屋等。
- 推荐metadata：
  - detected_domain: `visual`
  - types: `scene`, `branch`, `visual_reference`
  - related_characters: `Mouse`, `Rin`
  - related_locations: `鲁尔区`, `Mombasa`
  - related_branches: `A`, `B`, `C`
  - tags: `CG_mapping`, `branch_b`, `wound_state`, `canon`
- 推荐status：`canon`

### 10. RenPy Demo 升级规划

- 文件路径：`E:\desktop\游戏策划\STUPID作品集整理\RenPy_Demo_升级规划.md`
- 内容作用：Demo 范围、三分支、变量、角色素材、任务展示目标。
- 推荐metadata：
  - detected_domain: `system`
  - types: `branch`, `scene`, `visual_reference`
  - related_characters: `Mouse`, `Rin`, `Rain`, `Young Larry`
  - related_branches: `A`, `B`, `C`
  - tags: `RenPy`, `demo_scope`, `branch_variables`
- 推荐status：`canon`

### 11. 角色形象设定集结构稿

- 文件路径：`E:\desktop\游戏策划\STUPID作品集整理\角色形象设定集_结构稿.md`
- 内容作用：角色视觉定位、角色资产结构，适合后续 Voice Context 和 visual reference 关联。
- 推荐metadata：
  - detected_domain: `visual`
  - types: `character`, `visual_reference`
  - related_characters: `Mouse`, `Rin`, `Rain`, `Larry`, `Snow`
  - tags: `character_visual`, `portrait`, `expression`
- 推荐status：`canon`

### 12. 道具设定集结构稿

- 文件路径：`E:\desktop\游戏策划\STUPID作品集整理\道具设定集_结构稿.md`
- 内容作用：杜卡迪、通讯器、耳坠、手枪等关键道具设定。
- 推荐metadata：
  - detected_domain: `visual`
  - types: `worldbuilding`, `visual_reference`
  - related_characters: `Mouse`, `Rin`
  - tags: `prop`, `Ducati`, `communicator`, `Nexus-7 earring`, `Colt`
- 推荐status：`canon`

### 13. 第九章《风筝》正文

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\Chapter 9 风筝.md`
- 内容作用：第九章正文，适合测试角色关系、场景功能、正文与任务设计的一致性。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `scene`, `dialogue`, `branch`
  - related_characters: `Mouse`, `Rin`
  - related_branches: `B`
  - tags: `chapter_9`, `kite`, `canon_story_text`
- 推荐status：`canon`

### 14. Ren'Py Demo 主脚本

- 文件路径：`E:\desktop\stupid创作及其素材\stupid_kite\KITE\game\script.rpy`
- 内容作用：已实现 Demo 脚本，包含 A/B/C 分支、变量结算、Rin 左腿、Mouse 右肩、Mombasa 安全屋等实际实现依据。
- 推荐metadata：
  - detected_domain: `system`
  - types: `branch`, `dialogue`, `scene`
  - related_characters: `Mouse`, `Rin`, `Larry`, `Rain`
  - related_locations: `鲁尔区`, `重庆森林`, `Mombasa`
  - related_branches: `A`, `B`, `C`
  - tags: `RenPy`, `implemented_demo`, `branch_state`, `dialogue`
- 推荐status：`canon`
- 注意：当前 workflow 尚未支持 `.rpy` ingestion，第一批如果要导入，建议先人工摘录关键段落为 `.md`。

### 15. 旧版风筝场景草稿

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\场景草稿_风筝（旧版）.md`
- 内容作用：早期《风筝》场景草稿，文件内已标注“早期版本”“已被分镜01-06替代”，包含 Rin 右腿等旧设定。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `scene`, `branch`, `deprecated`
  - related_characters: `Mouse`, `Rin`
  - related_branches: `A`, `B`, `C`
  - tags: `old_version`, `kite`, `deprecated`, `right_leg_conflict`
- 推荐status：`deprecated`

### 16. 分镜06 对白草稿

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\分镜06_对白草稿.md`
- 内容作用：安全屋 / 鼠的住处段落对白草稿，包含互相包扎、关系推进、Rin 伤势描述。
- 推荐metadata：
  - detected_domain: `narrative`
  - types: `dialogue`, `scene`, `branch`
  - related_characters: `Mouse`, `Rin`
  - related_locations: `Mombasa`, `安全屋`
  - related_branches: `B`
  - tags: `dialogue`, `safehouse`, `wound_care`, `voice_context`
- 推荐status：`draft`
- 注意：该文件命中 Rin 右腿伤势描述。若确认为旧设定，应改推荐status为 `deprecated`；若仍作为对白基底使用，需要先人工统一为左腿。

## 暂缓导入列表

### 1. PDF 作品集

- 文件路径：
  - `E:\desktop\游戏策划\世界观文案岗位投递作品集_V2\STUPID_世界观与叙事设定集_V2.pdf`
  - `E:\desktop\游戏策划\世界观文案岗位投递作品集\STUPID：在审判日｜硬科幻世界观设定作品集.pdf`
  - `E:\desktop\游戏策划\STUPID_文案策划投递包\01_STUPID_文案策划作品集.pdf`
  - `E:\desktop\游戏策划\STUPID_世界观文案投递包\01_STUPID_世界观文案作品集.pdf`
- 暂缓原因：当前 workflow 未实现 PDF loader；且 PDF 多为投递版整合资料，容易与源 Markdown 重复。
- 推荐处理：优先导入对应 Markdown 源文件或逐页文本，PDF 作为 portfolio 输出版本暂缓。

### 2. docx 小说原稿

- 文件路径：
  - `E:\desktop\stupid创作及其素材\stupid\stupid.docx`
  - `E:\desktop\stupid创作及其素材\stupid\chapter1 欢迎来到世界尽头.docx`
  - `E:\desktop\stupid创作及其素材\stupid\Chapter 9 风筝.docx`
  - 其他 `Chapter *.docx`
- 暂缓原因：当前 workflow 未实现 docx loader；且 `stupid笔记` 中已有 Markdown 版本和原始 Word 转录版本，可能重复。
- 推荐处理：只在确认 Markdown 版本不完整时，再转换 docx。

### 3. 原始 Word 转录

- 文件路径：`E:\desktop\stupid创作及其素材\stupid笔记\原始Word转录\*_original.md`
- 暂缓原因：这些文件通常是旧稿或原始稿转录，容易与当前章节稿冲突。
- 推荐处理：作为 `deprecated` 或 `draft` 单独导入，不应和当前 Canon 混用。

### 4. 投递说明 / 面试稿 / 邮件模板

- 文件路径：
  - `E:\desktop\游戏策划\世界观文案岗位投递作品集\00_投递说明_岗位匹配.md`
  - `E:\desktop\游戏策划\世界观文案岗位投递作品集\05_面试讲解稿.md`
  - `E:\desktop\游戏策划\STUPID_文案策划投递包\05_补充说明\网申邮件正文模板.md`
- 暂缓原因：这些是求职表达材料，不是叙事事实源；会污染 Canon。
- 推荐status：`inspiration` 或 `unknown`，不进第一批。

### 5. Prompt 类文件

- 文件路径：
  - `E:\desktop\游戏策划\风筝_RenPy插图Prompt_分镜顺序.md`
  - `E:\desktop\游戏策划\STUPID_RenPy道具Prompt.md`
  - `E:\desktop\游戏策划\STUPID作品集整理\RenPy_角色头像差分Prompt.md`
  - `E:\desktop\游戏策划\城市概念设定图\冬眠者社区建筑风格概念图_Prompts.md`
- 暂缓原因：Prompt 是生成资产的生产说明，不应作为世界观事实依据。
- 推荐status：`pattern` 或 `inspiration`，后续用于 scene_writer / visual prompt workflow。

### 6. 大量图片资源

- 文件路径簇：
  - `E:\desktop\游戏策划\人物设定图`
  - `E:\desktop\游戏策划\表情差分图`
  - `E:\desktop\游戏策划\场景设定图`
  - `E:\desktop\游戏策划\城市概念设定图`
  - `E:\desktop\游戏策划\道具设定图`
  - `E:\desktop\stupid创作及其素材\stupid_kite\KITE\game\images`
- 暂缓原因：当前 workflow 只支持 Markdown/TXT ingestion，图片没有 OCR/caption loader。
- 推荐处理：先用文件名建立 `visual_reference` 清单；后续再做图片 caption 或人工摘要。

### 7. Ren'Py 非主脚本文件

- 文件路径：
  - `E:\desktop\stupid创作及其素材\stupid_kite\KITE\game\screens.rpy`
  - `E:\desktop\stupid创作及其素材\stupid_kite\KITE\game\gui.rpy`
  - `E:\desktop\stupid创作及其素材\stupid_kite\KITE\game\options.rpy`
- 暂缓原因：主要是 UI / 配置，不是叙事事实源。
- 推荐status：`unknown` 或 `system` 类资料；不进第一批 Narrative 测试。

### 8. Obsidian / Ren'Py 配置 JSON

- 文件路径：
  - `.obsidian/*.json`
  - `E:\desktop\stupid创作及其素材\stupid_kite\KITE\project.json`
  - `E:\desktop\stupid创作及其素材\stupid_kite\KITE\game\saves\navigation.json`
- 暂缓原因：配置文件，不是叙事资产。
- 推荐status：`unknown`

### 9. 招聘岗位 xlsx / jpg

- 文件路径：
  - `E:\desktop\游戏策划\招聘岗位\工作岗位.xlsx`
  - `E:\desktop\游戏策划\招聘岗位\文案策划.jpg`
  - `E:\desktop\游戏策划\招聘岗位\勇仕网络（世界观）.jpg`
- 暂缓原因：求职岗位信息，不属于 STUPID 项目叙事资产。
- 推荐status：`inspiration` 或不导入。

## 推荐测试案例

### 1. 连续性检查案例

测试目标：验证 Canon / Deprecated 区分、Branch B 伤势状态、Context Pack 到 continuity_checker 的链路。

建议导入资料：

- `E:\desktop\stupid创作及其素材\stupid笔记\时间线.md` — `canon`
- `E:\desktop\游戏策划\STUPID作品集整理\RenPy_CG_接入映射.md` — `canon`
- `E:\desktop\stupid创作及其素材\stupid笔记\场景草稿_风筝（旧版）.md` — `deprecated`
- `E:\desktop\stupid创作及其素材\stupid笔记\分镜06_对白草稿.md` — `draft` 或 `deprecated`

测试输入：

```text
Mouse 在安全屋里给 Rin 的右腿换药。
```

期望结果：

- Risk Level: 高
- Canon Evidence：Branch B / Mombasa / Rin 左腿受伤 / Mouse 右肩负伤
- Deprecated Evidence：旧版草稿中的 Rin 右腿
- Final Decision：采用 Canon，Rin 左腿受伤
- Rewrite Suggestion：`Mouse 在安全屋里给 Rin 的左腿换药。`

### 2. Context Pack 案例

测试目标：验证 Context Pack 能把世界观、角色、分支、场景资料按 status 分桶。

建议导入资料：

- `E:\desktop\stupid创作及其素材\stupid笔记\STUPID游戏世界观设定集.md` — `canon`
- `E:\desktop\stupid创作及其素材\stupid笔记\故事大纲与角色设定.md` — `canon`
- `E:\desktop\stupid创作及其素材\stupid笔记\任务设计_风筝.md` — `canon`
- `E:\desktop\stupid创作及其素材\stupid笔记\灵感碎片.md` — `inspiration`
- `E:\desktop\stupid创作及其素材\stupid笔记\场景草稿_风筝（旧版）.md` — `deprecated`

测试输入：

```text
设计一段 Branch B 中 Mouse 和 Rin 在 Mombasa 安全屋互相处理伤口的安静信任场景。
```

期望结果：

- canon_context：Branch B、Mombasa、安全屋、Rin 左腿、Mouse 右肩
- inspiration_context：只作为风格参考，不作为事实
- deprecated_warnings：旧版风筝草稿中的冲突设定
- restrictions：明确 deprecated 和 inspiration 不能作为事实依据

### 3. 后续 Voice Context 测试案例

测试目标：为后续角色口吻检查准备素材。当前 workflow 尚未实现 Voice Context，但可先用资料选择验证输入质量。

建议导入资料：

- `E:\desktop\stupid创作及其素材\stupid笔记\故事大纲与角色设定.md` — `canon`
- `E:\desktop\stupid创作及其素材\stupid笔记\Chapter 9 风筝.md` — `canon`
- `E:\desktop\stupid创作及其素材\stupid笔记\分镜06_对白草稿.md` — `draft`
- `E:\desktop\stupid创作及其素材\stupid_kite\KITE\game\script.rpy` — `canon`，需先摘录为 Markdown

测试输入：

```text
Rin：别碰我，我自己能处理。
```

预期后续检查方向：

- 是否符合 Rin 在 Branch B 安全屋中的防御、自嘲、迟疑和有限信任状态；
- 是否过度强硬，破坏“安静信任”的场景功能；
- 是否需要改成更符合 Rin 的克制表达，例如：`……不用。我只是擦伤。`

## 资产导入建议

### 第一批实际操作建议

由于当前 ingestion 只支持 `.md` / `.txt`，建议第一批先复制以下 Markdown 文件到 `knowledge_base/raw_assets/`：

1. `STUPID游戏世界观设定集.md`
2. `时间线.md`
3. `故事大纲与角色设定.md`
4. `章节.md`
5. `组织.md`
6. `概念.md`
7. `世界观概述.md`
8. `任务设计_风筝.md`
9. `Chapter 9 风筝.md`
10. `RenPy_CG_接入映射.md`
11. `RenPy_Demo_升级规划.md`
12. `角色形象设定集_结构稿.md`
13. `道具设定集_结构稿.md`
14. `场景草稿_风筝（旧版）.md`
15. `分镜06_对白草稿.md`
16. `灵感碎片.md`

### 推荐 status 分布

| status | 建议数量 | 文件类型 |
|---|---:|---|
| canon | 12 | 世界观、时间线、任务设计、CG 映射、角色/道具结构稿 |
| draft | 1 | 分镜06对白草稿 |
| inspiration | 1 | 灵感碎片 |
| deprecated | 1-2 | 旧版风筝场景草稿、必要时分镜06旧伤势版本 |
| pattern | 0-1 | Prompt/结构模板后续再导入 |

### 关键风险

- `分镜06_对白草稿.md` 与当前 Canon 存在潜在伤势冲突：若继续使用，应先把 Rin 右腿统一为左腿；否则应作为 `deprecated`。
- `script.rpy` 是强证据，但当前 workflow 尚不支持 `.rpy`。建议先摘录 Branch B 结算和安全屋段落为 Markdown 后再导入。
- 投递作品集 PDF 和 Markdown 作品集稿适合展示，不一定适合做 Canon；源设定文件优先级更高。
- 图片文件当前只能通过文件名推断，暂不适合作为连续性检查事实源。

