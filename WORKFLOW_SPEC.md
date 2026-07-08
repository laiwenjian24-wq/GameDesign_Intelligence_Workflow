# WORKFLOW_SPEC

## 工作流目标

本文件定义第一阶段 Narrative Workflow 的行为规格。

该工作流面向游戏文案策划和叙事设计，服务《STUPID: Before Judgment Day》的资料管理、设定检索和剧情连续性检查。

第一阶段只做 Narrative Workflow，不做 MCP、不做多 Agent、不做网页 UI。

## 总流程

```text
1. 用户放入资料
2. 系统扫描资料
3. 系统解析内容
4. 系统生成分类建议和 metadata
5. 系统建立或更新检索索引
6. 用户提交剧情草稿或查询问题
7. 系统检索相关资料
8. 系统执行连续性检查
9. 系统输出 Markdown 报告
```

## 资料导入工作流

### 输入

用户将文件放入本地输入目录。

支持格式：

- `.md`
- `.txt`
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`

### 处理步骤

1. 扫描输入目录。
2. 识别文件类型。
3. 计算内容哈希。
4. 判断是否已导入。
5. 提取文本或基础描述。
6. 保存解析结果。
7. 进入分类与 metadata 阶段。

### 输出

每个文件需要形成一条文档记录。

最低记录字段：

```yaml
doc_id:
source_path:
file_name:
file_type:
content_hash:
ingested_at:
parse_status:
```

## 分类工作流

### 分类集合

```text
Canon
Draft
Inspiration
Deprecated
Pattern
Unknown
```

### 分类定义

#### Canon

已确认的正式设定、剧情事实、角色事实、世界观规则。

Canon 是连续性检查的最高优先级依据。

#### Draft

正在创作或讨论中的草稿。Draft 可以参与参考，但不能覆盖 Canon。

#### Inspiration

外部灵感、竞品分析、风格参考、图片参考、主题参考。

Inspiration 不能被当成项目事实。

#### Deprecated

已废弃或不再使用的旧设定、旧剧情、旧角色方案。

Deprecated 默认不参与正向设定回答，但可以用于追踪历史决策。

#### Pattern

可复用的叙事结构、场景模板、冲突模式、关系模式或设计原则。

Pattern 可以辅助场景设计，但不能作为 Canon 事实。

#### Unknown

系统无法可靠判断分类时使用。

Unknown 必须进入人工复核队列。

### 输出字段

```yaml
asset_class:
classification_confidence:
classification_reason:
needs_review:
```

### 关键规则

- AI 只能建议分类，不能静默确认 Canon。
- 低置信度资料必须进入人工复核。
- Unknown 不是错误，是安全状态。
- Deprecated 不等于删除。

## Metadata 工作流

### 目标

metadata 用于检索、过滤、连续性检查和报告引用。

### 建议字段

```yaml
doc_id:
title:
summary:
asset_class:
project_relevance:
characters:
locations:
timeline_refs:
themes:
stupid_domain:
spoiler_level:
canon_confidence:
source_path:
file_type:
content_hash:
created_at:
updated_at:
ingested_at:
```

### STUPID domain 建议枚举

```text
worldbuilding
character
plot
scene
dialogue
mechanics
visual_reference
pattern
production_note
```

## 检索工作流

### 输入

用户可以输入自然语言问题，例如：

```text
审判日前世界观里，学校系统处于什么状态？
```

也可以输入带过滤条件的问题，例如：

```text
只查 Canon：某角色是否知道审判机制的真相？
```

### 检索要求

检索结果必须包含：

- 回答摘要。
- 来源文件。
- 相关片段。
- 资料分类。
- 置信度或相关度。

### 检索优先级

默认优先级：

1. Canon
2. Draft
3. Pattern
4. Inspiration
5. Deprecated

Deprecated 默认不进入普通回答，除非用户明确要求查询旧设定。

## 连续性检查工作流

### 输入

用户提交：

- 新剧情草稿。
- 场景大纲。
- 角色行为描述。
- 世界观新增设定。

### 检查目标

系统需要检查：

- 是否违背 Canon。
- 是否引入了无依据的新事实。
- 是否和时间线冲突。
- 是否和角色已确认动机冲突。
- 是否误用了 Inspiration。
- 是否复活了 Deprecated 设定。

### 输出报告结构

建议报告格式：

```markdown
# 连续性检查报告

## 输入摘要

## 检索依据

## 发现的问题

## 风险等级

## 需要人工确认的问题

## 建议处理方式

## 来源引用
```

### 风险等级

```text
High    明确违反 Canon 或关键时间线
Medium  存在动机、设定或因果疑点
Low     表述不清、证据不足或需要补充说明
Info    无明显冲突，但有可优化点
```

## 报告输出工作流

### 输出格式

第一版输出 Markdown。

### 报告必须包含

- 检查时间。
- 输入文件或输入文本摘要。
- 使用的检索范围。
- 关键依据。
- 问题列表。
- 风险等级。
- 来源引用。
- 人工复核建议。

### 报告不应包含

- 无来源的确定性判断。
- 把 Inspiration 当 Canon 的结论。
- 自动改写后的 Canon。
- 未标注假设的推断。

## 第一阶段不做事项

明确不做：

- MCP。
- 多 Agent。
- 网页 UI。
- 自动写完整剧情。
- 自动修改项目正式设定。
- Excel。
- Ren'Py 脚本解析。
- 复杂图片理解。
- 知识图谱。
- 多用户权限。

## 第一版验收用例

### 用例 1：导入资料

给定一组 Markdown、TXT、PDF、PNG、JPG 资料，系统能生成文档记录、分类建议和 metadata。

### 用例 2：查询 Canon

用户询问一个世界观问题，系统只基于 Canon 回答，并提供来源。

### 用例 3：避免灵感污染

用户询问正式设定时，系统不能把 Inspiration 内容当成 Canon。

### 用例 4：检查剧情草稿

用户提交一段新剧情，系统输出连续性检查报告，指出潜在冲突和人工复核问题。

### 用例 5：识别废弃设定

如果新剧情引用了 Deprecated 资料，系统需要标出风险。

## 后续扩展方向

第一阶段跑通后，可以考虑：

- 角色口吻检查。
- 场景设计辅助。
- Pattern 推荐。
- Ren'Py 脚本解析。
- Excel 设定表导入。
- 更强图像理解。
- 知识图谱。
- 简单桌面或网页界面。

这些扩展必须建立在第一阶段 Narrative Workflow 已经稳定的基础上。

