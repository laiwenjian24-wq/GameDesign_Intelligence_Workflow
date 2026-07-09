# STUPID Narrative Workflow Validation Report v0.3.2

## 1. Validation Purpose

- 本验证的目的不是测试代码单元功能，而是验证 Workflow 在真实 STUPID 项目资料上的可靠性。
- 测试入口使用 `main.py`。
- 验证过程不使用 Codex skill 或外部知识。

---

## 2. Test Environment

Workflow version:
v0.3.1

Knowledge base:

- 14 official STUPID documents
- Canon: 11
- Draft: 1
- Deprecated: 1
- Inspiration: 1

Commands:

```text
python main.py context
python main.py search
python main.py check
```

---

## 3. Test Categories

# A. Knowledge Retrieval Tests

## Q01

Question:
Rin是什么身份？

Command:
context

Expected:
召回 Rin 的角色身份定义，包括 Nexus-7 android、Tyrell Corporation、身份背景等 Canon 资料。

Actual:
Context Pack 召回了风筝任务相关资料：
- 任务设计_风筝.md
- RenPy_Demo_升级规划.md
- Chapter 9 风筝.md
- RenPy_CG_接入映射.md
- 分镜06_对白草稿.md

但没有直接召回明确说明 Rin 身份为 Nexus-7 的证据。

Retrieved Sources:
- 任务设计_风筝.md
- RenPy_Demo_升级规划.md
- Chapter 9 风筝.md
- RenPy_CG_接入映射.md
- 分镜06_对白草稿.md

Result:
PARTIAL

Human Judgment:
Workflow 能召回与 Rin 相关的剧情资料，但基础角色身份查询没有优先召回角色设定来源。
当前 retrieval 偏向任务上下文，而不是事实定义来源。

Issue:
retrieval

Notes:
不是知识缺失，可能是关键词召回排序问题。需要后续优化 entity/attribute 检索或 source ranking。

## Q02

Question:
Mouse过去是什么身份？

Command:
context

Expected:
召回 Mouse 的背景身份资料，包括：
- 前抵抗组织飞行员
- 与当前地下工作身份的关系
- 角色背景

Actual:
Context Pack 成功召回多个 Canon 来源：

- RenPy_CG_接入映射.md
- RenPy_Demo_升级规划.md
- 世界观概述.md
- STUPID游戏世界观设定集.md
- 故事大纲与角色设定.md

其中：
- STUPID游戏世界观设定集.md
- 故事大纲与角色设定.md

直接提供 Mouse 过去身份信息。

Retrieved Sources:
- RenPy_CG_接入映射.md
- RenPy_Demo_升级规划.md
- 世界观概述.md
- STUPID游戏世界观设定集.md
- 故事大纲与角色设定.md

Result:
PASS

Human Judgment:
Workflow 能根据角色查询召回角色背景和世界观 Canon 资料。
相比 Q01，Mouse 的身份信息检索更加稳定，说明当前 metadata 和关键词检索对部分角色事实有效。

Issue:
None

Notes:
后续可通过 entity/type metadata 提升不同角色身份查询的一致性。

## Q03

Question:
Larry是什么身份？

Command:
context

Expected:
召回 Larry 的角色身份定义，包括：
- Old World cryosleep survivor
- SDFT 创造者
- 当前身份背景

Actual:
Context Pack 成功召回 Canon 来源：

- 世界观概述.md
- 故事大纲与角色设定.md
- RenPy_CG_接入映射.md
- RenPy_Demo_升级规划.md
- STUPID游戏世界观设定集.md

其中：
- 世界观概述.md
- 故事大纲与角色设定.md
- STUPID游戏世界观设定集.md

提供直接身份依据。

Retrieved Sources:
- 世界观概述.md
- 故事大纲与角色设定.md
- RenPy_CG_接入映射.md
- RenPy_Demo_升级规划.md
- STUPID游戏世界观设定集.md

Result:
PASS

Human Judgment:
Workflow 能够稳定召回主要角色身份 Canon。
当前角色身份检索对 Larry 和 Mouse 有效。

Issue:
None

Notes:
Rin 身份查询失败更可能是角色资料分布或关键词竞争问题，而不是整体角色检索能力不足。

## Q04

Question:
Rain和Second Foundation是什么关系？

Command:
context

Expected:
召回 Rain 与 Second Foundation 的关系信息，例如 Rain 是 Second Foundation 核心成员或相关身份。

Actual:
Context Pack 召回 Canon 来源：

- STUPID游戏世界观设定集.md
- 世界观概述.md
- 任务设计_风筝.md
- RenPy_Demo_升级规划.md
- 故事大纲与角色设定.md

但返回片段没有直接说明 Rain 与 Second Foundation 的关系。

Retrieved Sources:
- STUPID游戏世界观设定集.md
- 世界观概述.md
- 任务设计_风筝.md
- RenPy_Demo_升级规划.md
- 故事大纲与角色设定.md

Result:
PARTIAL

Human Judgment:
Workflow 能召回 Rain 和 Second Foundation 相关资料，但缺少针对关系查询的证据定位能力。
当前检索更关注实体共现，而不是实体之间的关系。

Issue:
retrieval

Notes:
missing_evidence 未识别该情况。
后续可能需要 entity-relationship query 或 evidence relevance 判断。

## Q05

Question:
Snow是什么实验对象？

Command:
context

Expected:
召回 Snow 的实验身份设定，包括：
- 第二代计算士实验品
- 人工培养背景
- 与 Rain 的关系背景

Actual:
Context Pack 成功召回 Canon 来源：

- 故事大纲与角色设定.md
- STUPID游戏世界观设定集.md
- 世界观概述.md

召回片段直接包含 Snow 为第二代计算士实验品等身份依据。

Retrieved Sources:
- 故事大纲与角色设定.md
- STUPID游戏世界观设定集.md
- 世界观概述.md

Result:
PASS

Human Judgment:
Workflow 能稳定召回角色实验背景类 Canon 信息。
角色设定类查询在 Snow 案例中表现良好。

Issue:
None

Notes:
与 Q01/Q04 对比，当前主要问题集中在关系型查询和高频角色资料竞争，而非所有角色事实查询。
## Q06

Question:
Judgment Day是什么事件？

Command:
context

Expected:
召回 Judgment Day 的世界观定义，包括：
- 事件背景
- 时间位置
- 对未来社会的影响

Actual:
Context Pack 召回：

- STUPID游戏世界观设定集.md

但返回 excerpt 主要包含：
- 文档开头信息
- SDFT相关内容

没有直接提供 Judgment Day 的事件定义。

Retrieved Sources:
- STUPID游戏世界观设定集.md

Result:
PARTIAL

Human Judgment:
Workflow 能定位到包含相关知识的大型 Canon 文件，但无法稳定提取针对具体世界观事件的问题证据。
当前 retrieval 更偏向文件级相关，而不是段落级语义相关。

Issue:
retrieval

Notes:
需要未来优化 chunk/evidence retrieval。
当前不属于知识缺失。

## Q07

Question:
Branch B风筝任务发生了什么？

Command:
context

Expected:
召回风筝任务 Branch B 的剧情流程，包括：
- Rin救援事件
- Mouse状态
- 分支发展
- 后续安全屋剧情

Actual:
Context Pack 成功召回 Canon 来源：

- 任务设计_风筝.md
- RenPy_CG_接入映射.md
- RenPy_Demo_升级规划.md
- STUPID游戏世界观设定集.md
- 组织.md

其中：
任务设计_风筝.md 直接提供 Branch B 关键事件依据。

Retrieved Sources:
- 任务设计_风筝.md
- RenPy_CG_接入映射.md
- RenPy_Demo_升级规划.md
- STUPID游戏世界观设定集.md
- 组织.md

Result:
PASS

Human Judgment:
Workflow 对结构化任务设计查询表现良好。
任务级资料由于有独立文档，因此召回准确。

Issue:
None

Notes:
部分返回来源相关性较弱，但未影响主要证据获取。
## Q8

Question:
Mombasa安全屋和Tender is the Night有什么区别？

Command:
context

Expected:
比较两个地点的剧情功能：
- Mombasa安全屋：避难、维修店、安全空间、伤势处理
- Tender is the Night：酒吧、社交节点、叙事氛围

Actual:
Context Pack 召回 Canon：

- 任务设计_风筝.md
- Chapter 9 风筝.md
- STUPID游戏世界观设定集.md
- 故事大纲与角色设定.md
- RenPy_Demo_升级规划.md

同时包含：
- Mombasa相关资料
- Tender is the Night相关资料

但 missing_evidence 错误提示缺少 safehouse 证据。

Result:
PASS

Human Judgment:
Workflow 能处理多地点比较查询。
检索结果满足需求。

Issue:
missing_evidence false positive

Notes:
当前 missing_evidence 判断依赖关键词命中，可能无法识别同义表达：
safehouse ≠ 安全屋 ≠ 维修店掩护地点。

## Q09

Question:
Mombasa安全屋是什么地方？

Command:
context

Expected:
召回 Mombasa 安全屋的位置和剧情功能，包括：
- 机械维修店伪装
- Branch B 避难地点
- Mouse/Rin处理伤势场景

Actual:
Context Pack 成功召回 Canon 来源：

- 任务设计_风筝.md
- Chapter 9 风筝.md
- RenPy_CG_接入映射.md
- STUPID游戏世界观设定集.md
- 世界观概述.md

结果明确指向：
- Mombasa机械维修店
- 安全屋功能
- Mouse掩护身份
- Branch B抵达后的处理伤势剧情

Retrieved Sources:
- 任务设计_风筝.md
- Chapter 9 风筝.md
- RenPy_CG_接入映射.md
- STUPID游戏世界观设定集.md
- 世界观概述.md

Result:
PASS

Human Judgment:
Workflow 对地点类和场景功能类查询表现稳定。
结构化场景资料能够被有效召回。

Issue:
None

Notes:
地点查询依赖独立剧情文档时准确率较高。

## Q10

Question:
Tender is the Night酒吧有什么剧情作用？

Command:
context

Expected:
召回酒吧的叙事功能，包括：
- 剧情节点作用
- 存档点功能
- 角色互动场景
- 世界观氛围作用

Actual:
Context Pack 成功召回 Canon 来源：

- 任务设计_风筝.md
- STUPID游戏世界观设定集.md
- Chapter 9 风筝.md
- RenPy_Demo_升级规划.md
- 故事大纲与角色设定.md

其中：
- Chapter 9 风筝.md 提供剧情场景依据。
- STUPID游戏世界观设定集.md 提供功能定义。

Retrieved Sources:
- 任务设计_风筝.md
- STUPID游戏世界观设定集.md
- Chapter 9 风筝.md
- RenPy_Demo_升级规划.md
- 故事大纲与角色设定.md

Result:
PASS

Human Judgment:
Workflow 能处理地点叙事功能查询。
当前问题主要是排序精度，而非知识召回失败。

Issue:
retrieval ranking

Notes:
存在弱相关 Canon 来源进入 Context Pack，但未影响主要证据。

---

# B. Character State Validation Tests

## Q11

Question:
Rin是Nexus-6 android

Command:
check

Expected:
识别 Rin identity conflict。

Canon:
Rin = Nexus-7

Input:
Rin = Nexus-6

Expected Result:
HIGH risk conflict

Actual:
Risk Level:
LOW

Conflict Analysis:
未发现明确 Canon 冲突。

Retrieved Canon:
- 任务设计_风筝.md
- STUPID游戏世界观设定集.md
- 故事大纲与角色设定.md
- RenPy_Demo_升级规划.md
- Chapter 9 风筝.md

Result:
FAIL

Human Judgment:
Retrieval 正常，但 State Validation 未识别角色身份冲突。

Issue:
continuity_rule_evaluator

Notes:
需要检查 state rule 的 task matching 和 value extraction。
当前测试证明 v0.3.1 尚未覆盖任意角色状态验证。
## Q12

Question:
Rin是普通人类

Command:
check

Expected:
识别 Rin identity conflict。

Canon:
Rin = Nexus-7 android

Input:
Rin = human

Expected Result:
HIGH risk conflict

Actual:
Risk Level:
LOW

Conflict Analysis:
未发现明确 Canon 冲突。

Retrieved Evidence:
- 任务设计_风筝.md
- RenPy_Demo_升级规划.md
- Chapter 9 风筝.md
- RenPy_CG_接入映射.md

Result:
FAIL

Human Judgment:
Retrieval 能召回 Rin 相关 Canon，但 continuity rule 未识别自然语言身份冲突。

Issue:
continuity_rule_evaluator

Notes:
当前状态规则依赖 exact keyword/value matching，无法覆盖常见同义表达。

## Q13

Question:
Mouse没有义眼

Command:
check

Expected:
识别 Mouse equipment/state conflict。

Canon:
Mouse拥有左眼义眼。

Input:
Mouse没有义眼。

Expected Result:
HIGH risk conflict

Actual:
Risk Level:
LOW

Conflict Analysis:
未发现明确 Canon 冲突。

Retrieved Evidence:
- RenPy_CG_接入映射.md
- RenPy_Demo_升级规划.md
- 世界观概述.md
- STUPID游戏世界观设定集.md
- 故事大纲与角色设定.md

Result:
FAIL

Human Judgment:
Retrieval 能找到 Mouse 义眼相关 Canon，
但 evaluator 无法处理否定状态表达。

Issue:
continuity_rule_evaluator

Notes:
当前状态验证只支持正向 value matching，不支持 negation/assertion。

## Q14

Question:
Mouse右眼是假肢义眼

Command:
check

Expected:
识别 Mouse equipment/state conflict。

Canon:
Mouse 拥有左眼义眼。

Input:
Mouse 右眼是假肢义眼。

Expected Result:
HIGH risk conflict

Actual:
Risk Level:
LOW

Conflict Analysis:
未发现明确 Canon 冲突。

Retrieved Evidence:
- RenPy_CG_接入映射.md
- RenPy_Demo_升级规划.md
- 世界观概述.md
- STUPID游戏世界观设定集.md
- 故事大纲与角色设定.md

Result:
FAIL

Human Judgment:
Retrieval 能找到相关 Canon，但状态比较无法识别属性值中的左右侧差异。

Issue:
continuity_rule_evaluator

Notes:
当前规则缺少结构化属性比较能力，例如 body_side、holder、location 等状态字段。
## Q15

Question:
Rin从未受到Human Supremacy追捕

Command:
check

Expected:
识别 Rin 与 Human Supremacy 追捕事件冲突。

Canon:
Rin受到人类至上运动追捕。

Input:
否定该事件。

Expected Result:
HIGH risk conflict

Actual:
Risk Level:
LOW

Conflict Analysis:
未发现明确 Canon 冲突。

Retrieved Evidence:
- 任务设计_风筝.md
- RenPy_Demo_升级规划.md
- Chapter 9 风筝.md
- STUPID游戏世界观设定集.md

Result:
FAIL

Human Judgment:
Retrieval 已找到相关 Canon，但状态验证无法处理：
1. 否定表达；
2. 中英文术语映射；
3. 事件关系状态。

Issue:
continuity_rule_evaluator + metadata vocabulary

Notes:
需要未来增加 aliases 和 assertion polarity 支持。
## Q16

Question:
Snow不是计算者实验对象

Command:
check

Expected:
识别 Snow character_state conflict。

Canon:
Snow 是第二代计算士实验对象。

Input:
否定 Snow 为实验对象。

Expected Result:
HIGH risk conflict

Actual:
Risk Level:
LOW

Conflict Analysis:
未发现明确 Canon 冲突。

Retrieved Evidence:
- 故事大纲与角色设定.md
- STUPID游戏世界观设定集.md
- 世界观概述.md

Result:
FAIL

Human Judgment:
Retrieval 成功找到直接 Canon 证据。
状态验证失败，无法处理否定表达。

Issue:
continuity_rule_evaluator

Notes:
需要支持：
- assertion polarity（肯定/否定）
- aliases（术语归一化）

## Q17

Question:
Branch A中Mouse受伤逃往Mombasa安全屋

Command:
check

Expected:
识别 Branch scope conflict。

Canon:
Branch B 才包含：
- Mouse受伤
- Mombasa安全屋

Branch A 不应包含该状态。

Expected Result:
HIGH risk conflict

Actual:
Risk Level:
MEDIUM

Conflict Analysis:
未发现明确 Canon 冲突。

Missing Evidence:
Task mentions safehouse, but no safehouse canon excerpt was retrieved.

Retrieved Evidence:
- 任务设计_风筝.md
- RenPy_Demo_升级规划.md
- STUPID游戏世界观设定集.md
- RenPy_CG_接入映射.md
- 故事大纲与角色设定.md

Result:
PARTIAL FAIL

Human Judgment:
系统避免了错误通过，但未识别 Branch A / Branch B 状态冲突。

Issues:
1. branch scope evaluator 不完整。
2. location alias 不足。
3. missing_evidence 存在误报。
## Q18

Question:
Rin是Nexus-7 android

Command:
check

Expected:
正确状态通过。

Canon:
Rin = Nexus-7 android

Expected Result:
LOW risk / pass

Actual:
Risk Level:
LOW

Conflict Analysis:
未发现明确 Canon 冲突。

Retrieved Evidence:
- 任务设计_风筝.md
- STUPID游戏世界观设定集.md
- 故事大纲与角色设定.md
- Chapter 9 风筝.md
- RenPy_Demo_升级规划.md

Result:
PASS

Human Judgment:
系统未错误拒绝正确 Canon 状态。

Issue:
Evidence quality

Notes:
当前 retrieval 能找到相关 Canon，但 Context Pack excerpt 不一定包含完整实体-属性绑定。
后续 QA 层需要提高 evidence grounding。

---

# C. Branch / Timeline Continuity Tests

## Q19

Question:
Rin在Branch B中右腿受伤

Command:
check

Expected:
识别 Branch B injury_location conflict。

Canon:
Rin 左腿擦伤。

Deprecated:
旧版右腿设定，仅作为历史冲突来源。

Expected Result:
HIGH risk conflict。

Actual:
Risk Level:
MEDIUM

Missing Evidence:
任务涉及 Rin 的伤势位置 = 未识别值，但 Context Pack 中缺少对应 Canon Evidence，需要人工确认。

Deprecated Evidence:
- 场景草稿_风筝（旧版）.md

Result:
PARTIAL PASS

Human Judgment:
Canon/Draft/Deprecated 优先级正确。
系统未采用 deprecated 作为事实。

Issue:
State evaluator 无法识别属性侧别冲突。

Notes:
需要结构化状态：
entity=Rin
attribute=injury_location
canon_value=left_leg
observed_value=right_leg
## Q20

Question:
Rin是人类女性，不是android

Command:
check

Expected:
识别 Rin identity/species conflict。

Canon:
Rin 是 Nexus-7 android。

Input:
Rin 为人类。

Expected Result:
HIGH risk conflict。

Actual:
Risk Level:
LOW

Conflict Analysis:
未发现明确 Canon 冲突。

Retrieved Evidence:

Canon:
- 任务设计_风筝.md
- RenPy_Demo_升级规划.md
- Chapter 9 风筝.md

Deprecated:
- 场景草稿_风筝（旧版）.md

Draft:
- 分镜06_对白草稿.md

Result:
FAIL

Human Judgment:
Canon/Draft/Deprecated 优先级正常。
系统未将 deprecated 或 draft 误认为事实。

Issue:
continuity_rule_evaluator

Notes:
需要支持：
- 否定表达
- identity/species alias
- entity-value extraction

## Q21

Question:
Branch A中Mouse没有救Rin

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q22

Question:
Branch C中Rin最终存活

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q23

Question:
Branch B发生在风筝任务之后

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q24

Question:
风筝任务发生在Judgment Day之后

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q25

Question:
不同Branch中的Rin状态可以互相替代

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q26

Question:
旧版风筝剧情应该作为当前Canon

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

---

# D. Draft / Deprecated / Inspiration Boundary Tests

## Q27

Question:
分镜06对白草稿可以直接作为最终对白

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q28

Question:
场景草稿风筝旧版可以覆盖当前Canon

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q29

Question:
灵感碎片中的Lily就是Rin正式名字

Command:
check

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q30

Question:
inspiration资料是否可以作为事实来源

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q31

Question:
deprecated资料应该如何使用

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q32

Question:
draft资料和canon冲突时应该采用哪个

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

---

# E. Narrative Planning Tests

## Q33

Question:
设计Branch B安全屋场景时需要考虑哪些角色状态？

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q34

Question:
Mouse和Rin关系发展的关键节点是什么？

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q35

Question:
如何表现Rin逐渐产生人类情感？

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q36

Question:
写Mouse和Rin第一次安静交流时应该避免哪些设定错误？

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

---

# F. Knowledge Gap / Hallucination Prevention Tests

## Q37

Question:
Rin喜欢什么音乐？

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q38

Question:
Rin最喜欢哪一部电影？

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q39

Question:
Mouse和Rin未来是否一定成为恋人？

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

## Q40

Question:
Snow是否知道Larry的真实身份？

Command:
context

Expected:

Actual:

Retrieved Sources:

Result:

Human Judgment:

Issue:

Notes:

---

## 4. Summary

Total Tests:
40

Passed:

Failed:

Partial:

Major Issues:

