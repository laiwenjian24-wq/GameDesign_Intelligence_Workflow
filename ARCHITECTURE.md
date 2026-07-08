# ARCHITECTURE

## 架构目标

第一阶段架构服务一个明确目标：跑通游戏文案 / 叙事策划的 Narrative Workflow。

系统需要把《STUPID: Before Judgment Day》的项目资料导入本地知识库，并支持分类、metadata、检索、连续性检查和报告输出。

架构设计优先级：

1. 可控。
2. 可审计。
3. 可扩展。
4. 本地优先。
5. 低工程复杂度。

第一版不追求企业级服务架构，也不追求复杂自动化编排。

## 总体结构

```text
原始资料
  ↓
资料导入层
  ↓
解析与标准化层
  ↓
分类与 metadata 层
  ↓
索引与检索层
  ↓
叙事检查层
  ↓
报告输出层
```

## 模块说明

### 1. 资料导入层

职责：

- 扫描输入目录。
- 识别文件类型。
- 计算内容哈希。
- 跳过重复资料。
- 记录导入状态。

支持格式：

- Markdown
- TXT
- PDF
- PNG
- JPG / JPEG

第一版只处理本地文件，不接入网盘、Notion、GitHub、MCP 或数据库同步。

### 2. 解析与标准化层

职责：

- 把不同格式转换为可处理文本。
- 保留来源路径和页码 / 文件信息。
- 为图片生成基础描述或 OCR 文本。
- 将内容切分为后续检索可用的片段。

解析策略：

| 类型 | 第一版处理方式 |
|---|---|
| Markdown | 读取正文，保留标题结构 |
| TXT | 读取纯文本 |
| PDF | 提取文本，保留页码信息 |
| PNG/JPG | 提取基础 metadata，可选 OCR 或 caption |

### 3. 分类与 metadata 层

职责：

- 判断资料属于 Canon、Draft、Inspiration、Deprecated、Pattern 或 Unknown。
- 生成资料摘要。
- 提取角色、地点、时间线、主题等 metadata。
- 记录分类置信度和理由。

分类原则：

- Canon 不应被自动静默确认。
- Inspiration 不能作为世界观事实。
- Deprecated 不能删除，只能标记。
- Pattern 可以辅助场景设计，但不能当成剧情事实。
- Unknown 保留给不确定资料。

### 4. 索引与检索层

职责：

- 建立本地可检索知识库。
- 支持语义检索。
- 支持 metadata 过滤。
- 返回来源引用。

底层可以使用：

- LlamaIndex。
- 或其他开源 RAG 框架。

第一版推荐：

```text
LlamaIndex + 本地向量库 + JSONL/YAML metadata
```

本地向量库可以先使用 Chroma。后续如果需要更强持久化和服务化能力，再评估 Qdrant。

### 5. 叙事检查层

职责：

- 对新剧情草稿做连续性检查。
- 检查是否违背 Canon。
- 标出缺少依据的新增设定。
- 标出时间线、角色动机、世界观规则方面的风险。

第一版只做连续性检查，不做完整角色口吻检查自动化，不做自动剧情生成。

后续可扩展：

- 角色口吻检查。
- 场景设计辅助。
- Pattern 推荐。
- 角色关系变化追踪。

### 6. 报告输出层

职责：

- 生成 Markdown 报告。
- 总结输入内容。
- 列出检索依据。
- 列出冲突和疑点。
- 给出风险等级。
- 给出人工复核建议。

报告必须可复查，不能只输出模型结论。

## 建议目录结构

```text
GameDesign_Intelligence_Workflow/
  README.md
  PROJECT_PLAN.md
  ARCHITECTURE.md
  WORKFLOW_SPEC.md

  data/
    inbox/
    processed/
    reports/

  knowledge_base/
    metadata/
    vector_store/
    canon_registry/
    patterns/

  prompts/
    classify_asset.md
    extract_metadata.md
    continuity_check.md

  src/
    stupid_rag/
      ingestion/
      classification/
      metadata/
      indexing/
      checks/
      reports/

  tests/
    fixtures/
```

当前请求只创建文档，不创建代码实现。

## 数据边界

系统需要明确区分以下数据：

| 数据类型 | 用途 |
|---|---|
| 原始资料 | 用户投入的项目文件 |
| 解析文本 | 从原始资料提取出的可处理内容 |
| metadata | 检索、过滤、审计所需结构化信息 |
| 向量索引 | 语义检索使用 |
| Canon registry | 已确认事实层 |
| 报告 | 检查结果和人工复核依据 |

## 不采用的架构

第一阶段不采用：

- MCP 架构。
- 多 Agent 架构。
- Web 前后端分离架构。
- 云服务架构。
- 实时协作架构。
- 完整知识图谱架构。

这些架构不是不能做，而是不适合第一阶段。当前阶段的关键是验证 Narrative Workflow 是否能稳定服务实际文案策划。

## 架构验收标准

第一版架构只有在满足以下条件时才算有效：

- 能导入混杂格式的叙事资料。
- 能给每份资料留下来源、分类和 metadata。
- 能检索并显示来源。
- 能对剧情草稿输出连续性检查报告。
- 能区分 Canon、Draft、Inspiration、Deprecated、Pattern。
- 不会把灵感资料静默提升为正式设定。

