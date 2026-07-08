# GameDesign Intelligence Workflow

本项目是一个面向游戏文案策划与叙事设计的 AI 辅助工作流，服务于原创 AVG / 视觉小说项目《STUPID: Before Judgment Day》。

第一阶段只做 Narrative Workflow：让项目资料能够被自动导入、自动分类、生成 metadata、建立检索能力，并支持剧情连续性检查与报告输出。

本项目不是通用聊天机器人，也不是完整游戏开发工具。它的核心目标是帮助叙事策划更稳定地管理世界观、角色、剧情草稿、灵感资料和叙事模式，降低设定污染、剧情矛盾和角色口吻漂移的风险。

## 第一阶段目标

第一版需要跑通以下闭环：

```text
资料导入 -> 自动分类 / metadata -> 建立检索 -> 连续性检查 -> 输出报告
```

第一阶段范围包括：

- 自动摄取项目资料。
- 支持 Markdown、TXT、PDF、PNG、JPG。
- 将资料分类为 Canon、Draft、Inspiration、Deprecated、Pattern。
- 为资料生成基础 metadata。
- 建立可检索知识库。
- 支持剧情连续性检查。
- 输出可读的检查报告。

第一阶段暂不实现：

- MCP。
- 多 Agent。
- 网页 UI。
- Ren'Py 脚本解析。
- Excel 解析。
- 完整知识图谱。
- 自动改写 Canon。

## 推荐底层路线

底层可以基于 LlamaIndex 或其他开源 RAG 框架实现。

第一版优先考虑 LlamaIndex，原因是它适合搭建可控的本地资料摄取、metadata、chunking、索引和检索流程。后续如果多模态资料、复杂 PDF、表格和图像理解需求上升，可以再评估 RAG-Anything、Qdrant、LightRAG 或其他开源组件。

第一版技术选择应服从一个原则：先把叙事工作流跑通，而不是追求框架复杂度。

## 目标用户

主要用户是游戏文案策划、叙事设计师、世界观设计者，以及负责维护《STUPID: Before Judgment Day》剧情资产的人。

系统需要帮助用户回答：

- 当前设定是否已经有 Canon 依据？
- 新剧情是否和现有世界观冲突？
- 角色行为和台词是否符合既有设定？
- 某个场景可以借用哪些 Pattern？
- 哪些资料只是灵感，不能当成项目事实？

## 核心资料分类

| 分类 | 含义 |
|---|---|
| Canon | 已确认设定、正式剧情事实、角色硬约束 |
| Draft | 草稿、备选剧情、未定稿设定 |
| Inspiration | 外部灵感、风格参考、竞品分析、素材启发 |
| Deprecated | 已废弃设定、旧版本剧情、历史遗留内容 |
| Pattern | 可复用叙事结构、场景模式、角色关系模式 |

AI 可以提出分类建议，但 Canon 的确认必须可审计，不能由模型静默覆盖。

## 当前阶段交付物

当前阶段先建立项目说明与规划文档：

- `README.md`
- `PROJECT_PLAN.md`
- `ARCHITECTURE.md`
- `WORKFLOW_SPEC.md`

后续才进入项目骨架、最小 CLI、资料摄取和检索实现。

