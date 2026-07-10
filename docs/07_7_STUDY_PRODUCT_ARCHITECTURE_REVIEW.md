# Universe OS
# 07_7_STUDY_PRODUCT_ARCHITECTURE_REVIEW.md

Version: 1.0

Document Type: Product Architecture Review

Status: Recommendation

Scope: Milestone 7.7 analysis only

---

# 1. Current Architecture Assessment

Milestone 7.6 后，Study Planet 已经从单目标学习工具推进到“多 Goal 学习空间”的雏形。

当前能力包括：

- Goal management。
- Multiple Goals。
- Goal switching。
- Long Term / Monthly / Weekly / Daily plan hierarchy。
- Daily Task execution。
- Study Session recording。
- Knowledge foundation。
- Retrieval foundation。
- Memory foundation。
- AI Core。
- Study Analyst capability。
- Study Workspace aggregation API。

当前架构方向总体正确：

```text
User
→ Universe
→ Study Planet
→ Current Goal
→ Plan
→ Task
→ Session
→ Knowledge / Memory
→ Analytics / Intelligence
```

但产品流仍有三个主要不清晰点：

1. Goal 是当前工作上下文，但 UI 中同时像“导航模块”和“业务对象”。
2. Plan 层级已经存在，但用户还不能自然理解“长期计划、月计划、周计划、每日任务”的创建和调整关系。
3. Knowledge、Memory、Analytics 已接入系统，但它们与 Goal / Task / Session 的关系还没有被产品化成清楚的学习反馈循环。

结论：

- Study Planet 应围绕 `Current Goal` 展开体验。
- Home 应回答“今天我应该做什么”。
- Plan 应回答“这个 Goal 如何推进”。
- Knowledge 应回答“我的学习资料属于哪里、能怎样帮助当前 Goal”。
- Analytics 应回答“我的学习行为说明了什么，下一步建议是什么”。
- Tutor 应回答“基于当前 Goal、计划、学习记录、Memory 和可用 Knowledge，我如何理解/解决这个问题”。

---

# 2. Product Model Problems

## 2.1 Goal 的层级身份不稳定

当前实现中 Goal 已经成为 Study Planet 的关键业务对象，但 IA 文档中 Goal 仍归属 Plan 二级能力。Milestone 7.6 又新增了 Goals 页面和 Goal switcher，这让用户可能产生两个疑问：

- 我是在管理一组 Goal，还是只是在编辑当前 Plan 的前置字段？
- 切换 Goal 会影响 Home、Plan、Knowledge、Analytics 和 Tutor 吗？

建议：

- Goal 不应只是 Plan 表单的一部分。
- Goal 也不应成为一个重型 Dashboard。
- Goal 应被定义为 Study Planet 内的 `Workspace Context`。
- UI 可以有 Goal 管理入口，但全局体验必须始终显示当前 Goal。

## 2.2 Plan 层级存在，但创建行为仍像一次性生成

当前 Plan UI 用 Long Term / Monthly / Weekly / Daily Tasks 展示层级，但创建行为仍是一次创建完整 7-day scaffold。用户可能认为四个按钮分别创建四类计划，但实际它们触发同一现有 API。

建议：

- 短期保留手动 scaffold，不做 AI 自动规划。
- 下个阶段需要把 Plan Builder 产品化：
  - 先确认 Goal。
  - 再创建 Long Term Plan。
  - 再补 Monthly Plan。
  - 再补 Weekly Plan。
  - 最后创建 Daily Tasks。
- 如果后端暂不新增接口，前端至少应将按钮合并为一个清晰动作：`Create Plan Structure`。

## 2.3 Daily execution 还不是完整工作流

当前用户可以从 Home 或 Plan 启动 Session，但任务执行体验仍偏“记录表单”，缺少清晰状态：

- 当前是否有 active session？
- 当前 session 属于哪个 Goal / Plan / Task？
- 完成 session 后如何更新今日任务、Memory 和 Analytics？
- 用户是否能看到近期 Study Records？

建议：

- Session 页面应成为 Study Planet 的 Focus Mode。
- Start / Finish / Notes / Feeling / Duration 应围绕当前 Task 展示。
- 完成后返回 Home，并展示进度变化和 Analyst insight 更新。

## 2.4 Knowledge ownership 还需要明确

Milestone 7.6 支持 Independent Knowledge 和 Goal linked Knowledge，这是正确方向。但产品上仍需解释：

- 某些资料属于当前 Goal。
- 某些资料是用户长期知识库的一部分。
- 同一资料未来可能服务多个 Goal。

建议：

- 当前阶段继续使用 `documents.goal_id` 的可选关系。
- 不强制所有 Knowledge 绑定 Goal。
- 后续如需要一份资料关联多个 Goal，再引入 `knowledge_goal_links` 关系表；不要现在提前扩展。

## 2.5 AI recommendation 的来源必须被用户理解

当前 Home 显示 AI Insight，数据来源是 Analytics / Study Analyst。方向正确，但 UI 应避免让用户误以为系统在自动决定计划。

建议：

- Home 中 AI Insight 应标注为“来自学习记录与当前 Goal 的分析”。
- AI 推荐只做 suggestion，不自动改 Goal、Plan 或 Task。
- 所有自动生成或 AI 草稿都必须需要用户确认后保存。

---

# 3. Recommended Domain Model

## 3.1 Goal 是否是 Study Planet 内的顶层对象？

是。

Goal 应是 Study Planet 内最高级的业务上下文，但不是 Universe 层级对象，也不是独立 Planet。

推荐定义：

```text
Study Planet
└── Goal
    ├── Plan
    ├── Task
    ├── Session
    ├── Knowledge links
    ├── Memory signals
    └── Analytics view
```

原因：

- 用户学习行为天然围绕目标组织。
- Plan、Task、Session 都需要知道“为什么学习”。
- Analytics 如果不按 Goal 归因，就只能显示泛化统计。
- Tutor / Analyst 需要 Current Goal 作为主要上下文。

注意：

- Study Planet 可以有多个 Goal。
- 同一时间应有一个 `Current Goal`。
- Global Home / Study Home 必须清楚显示当前 Goal。
- Goal 切换必须刷新 Plan、Today Tasks、Knowledge filter 和 Analytics context。

## 3.2 考试、阅读、通用学习是否共用同一个 Goal model？

应该共用。

推荐保留统一 `StudyGoal` 模型，并用 `goal_type` 区分场景：

```text
StudyGoal
├── goal_type: exam | reading | learning | growth
├── goal_name
├── description
├── deadline: optional
├── subjects
├── current_level
├── daily_available_minutes
├── priority
└── status
```

不要为考试、阅读、成长分别创建独立模型。

原因：

- 它们共享同一学习闭环：目标、计划、任务、学习记录、资料、分析。
- 不同点主要是字段可选性和 UI 文案，而不是业务边界。
- 统一模型更利于 Tutor / Analyst 读取上下文。

场景差异建议：

| Goal Type | Deadline | Plan Emphasis | Knowledge Emphasis |
| --- | --- | --- | --- |
| exam | 常见，建议填写 | 倒排时间、科目进度、复习节奏 | 教材、真题、错题 |
| reading | 可选 | 章节推进、阅读记录 | 书籍、笔记、摘录 |
| learning | 可选 | 主题学习、练习任务 | 课程、文档、项目资料 |
| growth | 通常长期 | 习惯、能力积累、阶段回顾 | 长期资料库、反思记录 |

## 3.3 Knowledge 是否总是属于 Goal？

不应该。

推荐模型：

```text
Knowledge Space
├── Independent Knowledge
└── Goal-linked Knowledge
```

规则：

- Knowledge 属于 User。
- Knowledge 可以选择性链接到 Goal。
- 当前阶段一份 Document 可选 `goal_id`。
- 未绑定 Goal 的资料仍可被保存、处理和查看。
- Tutor / Analyst 使用 Knowledge 时，应通过 Retrieval / ToolRouter，并根据当前 Goal 优先检索关联资料。

长期方向：

```text
User
└── Knowledge Space
    ├── Document A
    │   └── linked goals: Goal 1, Goal 2
    └── Document B
        └── independent
```

但多 Goal link 不是当前最急需求。

## 3.4 Plans 应由 Goal 生成还是手动创建？

当前阶段应是“Goal 驱动的手动创建”。

推荐分层：

1. Manual Plan：用户手动创建和编辑，是当前 MVP 真实行为。
2. AI-assisted Draft：后续可由 Study Analyst / Planner capability 生成草稿，但必须用户确认。
3. Autonomous Planning：暂不实现。

正确表达：

```text
Goal context
→ User creates or edits Plan
→ Tasks become executable
→ Sessions produce evidence
→ Analyst recommends adjustments
→ User decides whether to update Plan
```

禁止表达：

```text
AI silently changes Plan
AI automatically creates Tasks
AI decides user priorities without confirmation
```

## 3.5 推荐关系模型

```text
User
└── Study Planet
    ├── Goals
    │   └── Current Goal
    │       ├── Long Term Plan
    │       │   └── Monthly Plan
    │       │       └── Weekly Plan
    │       │           └── Daily Task
    │       │               └── Study Session
    │       ├── Knowledge links
    │       ├── Memory signals
    │       └── Analytics Summary
    ├── Independent Knowledge
    └── Planet-level Memory
```

字段关系建议：

| Object | Ownership | Required Relationship | Optional Relationship |
| --- | --- | --- | --- |
| Goal | user_id | User | none |
| Long Term Plan | user_id | Goal | none |
| Monthly Plan | user_id | Goal, Long Term Plan | none |
| Weekly Plan | user_id | Goal, Monthly Plan | none |
| Daily Task | user_id | Goal, Weekly Plan | Session |
| Study Session | user_id | Task when started from task | Goal for free study sessions, if supported later |
| Document | user_id | User | Goal |
| Memory | user_id, scope | User | planet_type, session_id |
| Analytics | derived | Goal / Task / Session / Knowledge / Memory | Retrieval context |

---

# 4. Recommended User Journey

## 4.1 First-time user

```text
Universe Portal
→ Enter Study Planet
→ No Current Goal
→ Create Goal
→ Goal becomes Current Goal
→ Create Plan Structure
→ See Today Task
→ Start Session
→ Finish Session
→ Home shows updated progress
→ Analytics shows first insight
```

## 4.2 Returning user

```text
Enter Study Planet
→ Study Home loads Current Goal
→ See Today Mission
→ Start or continue learning
→ Finish Session
→ Review progress and AI Insight
```

## 4.3 Multi-goal user

```text
Study Home
→ Switch Current Goal
→ Home / Plan / Today Tasks refresh
→ Knowledge filter follows selected Goal when user chooses
→ Analytics explains selected Goal progress
```

## 4.4 Reading goal user

```text
Create Goal: Read CSAPP
→ Upload CSAPP notes or PDF metadata
→ Create chapter-based Daily Tasks
→ Record reading sessions
→ Analyst identifies progress and weak concepts
→ Tutor answers questions with available Knowledge when retrieval exists
```

## 4.5 Exam goal user

```text
Create Goal: AI方向研究生
→ Add deadline
→ Create subject-based Plan
→ Complete Daily Tasks and Sessions
→ Upload materials and wrong questions
→ Analytics tracks progress, weak areas and recommended actions
```

---

# 5. UI Information Architecture

## 5.1 Recommended navigation

推荐保持 Study Workspace 六个主入口：

```text
Home
Plan
Knowledge
Tutor
Review
Analytics
```

Goal 不建议长期作为第七个主导航项。

原因：

- Goal 是 Workspace context，不是普通模块。
- 主导航过多会削弱“学习房间”的感觉。
- Goal 切换应是全局上下文行为，不应藏在一个页面里。

推荐 UI：

```text
Study Workspace Header
├── Universe Home
├── Study Planet
├── Current Goal Switcher
└── Location Breadcrumb

Navigation
├── Home
├── Plan
├── Knowledge
├── Tutor
├── Review
└── Analytics
```

Goal 管理可以存在为：

- Header 中的 Goal switcher。
- Plan 页面里的 `Manage Goals` secondary action。
- `/study/goals` route 可保留，但不一定出现在主导航。

## 5.2 Study Home review

当前方向正确：

- Current Goal 已成为首屏。
- Goal switcher 已出现。
- Today Tasks 从 current Goal 过滤。
- AI Insight 来自 Analytics。

还需要加强：

- Primary Next Action 应更强：如果有未完成 Today Task，首要动作就是 Start。
- Empty state 应根据缺口分层：
  - 无 Goal：Create Goal。
  - 有 Goal 无 Plan：Create Plan Structure。
  - 有 Plan 无 Today Task：Add Daily Task。
  - 有 Task 无 Session：Start Session。
  - 有完成记录：Review Analytics。
- Home 不应展示过多 Plan 细节，避免变成 Dashboard。只显示“当前计划摘要 + 今天任务”。

## 5.3 Goals review

当前 Goals 页面解决了多 Goal 管理问题，但信息层级可能和 Plan 重叠。

建议：

- Goals 页面保留为管理页。
- 主体验中使用 Header Goal Switcher。
- Goals 页面只做：
  - list goals。
  - create goal。
  - switch current goal。
  - archive goal later。
- 不在 Goals 页面展示 Plan、Task、Analytics 深层数据。

## 5.4 Plan review

当前 Plan 页面开始呈现层级，但按钮与行为不完全一致。

建议下一步：

- 将四个创建按钮调整为清晰的 Plan Builder。
- 避免用户误以为可以创建无父级的 Monthly / Weekly / Daily。
- Daily Tasks 必须显示所属 Week / Goal。
- Task 编辑应加入保存状态、失败状态和完成后的视觉反馈。

推荐结构：

```text
Plan
├── Current Goal Summary
├── Plan Builder / Plan Tree
│   ├── Long Term Plan
│   ├── Monthly Plan
│   ├── Weekly Plan
│   └── Daily Tasks
└── Task Actions
    ├── Edit
    ├── Complete
    └── Start Session
```

## 5.5 Knowledge review

当前 Knowledge 支持 Goal filter 和 Independent Knowledge，是正确方向。

建议：

- Upload 表单应默认选择 Current Goal，但允许 Independent Knowledge。
- Document list 应显示 Goal relation。
- Document detail 应显示 processing status、chunks、goal link。
- 后续再加入 Summary、semantic search、RAG Q&A，不要现在混进上传流程。

## 5.6 Analytics review

Analytics 应是用户看见“学习数据如何变成智能建议”的地方。

建议：

- Analytics 默认按 Current Goal 展示。
- 显示 dataQuality，明确数据不足时不能过度建议。
- 推荐展示：
  - progress summary。
  - learning insights。
  - weak areas。
  - recommended actions。
  - supporting data。
- 避免大量图表和管理后台式 Dashboard。

## 5.7 Tutor review

Tutor 当前边界应保持：

- Tutor 是 Study Agent capability 的消费入口。
- Tutor 不直接访问 RetrievalService、MemoryRepository 或 KnowledgeRepository。
- Tutor 回答必须说明 Knowledge 是否可用。

建议：

- Tutor UI 明确显示当前 Goal。
- 如果没有可用 Knowledge，提示“当前没有可用资料上下文”。
- 如果检索到 chunks，展示 grounding metadata。
- 不伪造引用。

---

# 6. AI Integration Boundary

当前 AI 边界应继续保持如下：

## 6.1 Study Workflow to Intelligence

```text
Study Workflow Data
→ AI Core
→ Study Agent capability
→ Structured Insight
→ UI recommendation
```

规则：

- Study Workflow 数据包括 Goal、Plan、Task、Session、Learning Events。
- AI Core 只负责 context、prompt、tool、provider orchestration。
- Study Analyst 输出 structured insight。
- UI 展示 insight，但不把 insight 当作自动执行指令。

## 6.2 Knowledge boundary

```text
Knowledge Service
→ Retrieval Service
→ AI Core ToolRouter
→ Study Tutor / Analyst context
```

规则：

- Frontend 不直接访问 Retrieval 或 vector store。
- Tutor 不直接调用 RetrievalService。
- AI Core 不依赖 RAGFlow 或具体 Knowledge provider。
- Retriever Tool 只返回 chunks、metadata、identifiers、scores。

## 6.3 Memory boundary

```text
Memory Service
→ Context Preparation
→ AI Core payload
→ Study capability
```

规则：

- Memory 属于 User。
- Memory 使用 global / planet / session scope。
- AI Core 接收 prepared memory payload。
- Tutor / Analyst 不直接查询 Memory repository。
- 不做 personality inference。

## 6.4 Explicitly forbidden

Milestone 7.8+ 之前仍应避免：

- Autonomous planning。
- Hidden AI decisions。
- Personality inference。
- Tutor direct infrastructure access。
- Study Planet 内部创建独立 AI system。
- Knowledge Graph。
- 新 Planet。
- RAGFlow 生产集成，除非进入对应迁移里程碑。

---

# 7. Suggested Milestone 7.8+ Roadmap

## Milestone 7.8: Study Workspace IA Stabilization

Objective:

稳定 Study Workspace 的信息架构，让 Goal 成为全局上下文，而不是额外 Dashboard。

Scope:

- Move Goal switcher to Study Workspace header。
- Decide whether Goals appears in primary navigation or only as secondary management page。
- Update route mapping and docs to reflect final Goal placement。
- Add consistent empty states by missing object: no Goal / no Plan / no Task / no Session。

Out of scope:

- AI planning。
- RAG expansion。
- Database redesign。

## Milestone 7.9: Plan Builder Productization

Objective:

让 Plan 从“单次 scaffold”变成用户可理解的层级编辑流程。

Scope:

- Clarify Plan creation action.
- Ensure Monthly / Weekly / Daily cannot be orphaned.
- Add task grouping by Week.
- Add clear save / complete / error states.

Possible backend need:

- If current API cannot support granular plan creation, define small plan-specific APIs before coding.

## Milestone 7.10: Daily Execution Focus Mode

Objective:

把 Study Session 从记录表单升级为真实学习执行模式。

Scope:

- Active session state.
- Timer and task context.
- Finish summary.
- Return-to-Home progress update.
- Study Record list.

Out of scope:

- Autonomous recommendations.
- New Memory extraction model.

## Milestone 7.11: Knowledge Workspace Productization

Objective:

让 Knowledge 与 Goal / independent library 的关系清楚可用。

Scope:

- Default upload goal to Current Goal.
- Show Independent vs Goal-linked documents.
- Improve document detail and processing states.
- Prepare UI for future RAGFlow provider migration without exposing provider details.

Out of scope:

- RAGFlow integration.
- AI Summary.
- Knowledge Graph.

## Milestone 7.12: Analytics as Learning Intelligence

Objective:

让 Analytics 成为 Study Planet 的 intelligence surface。

Scope:

- Current Goal scoped analytics.
- Data quality explanation.
- Recommended actions with supporting evidence.
- Link recommended actions back to Plan / Task / Knowledge.

Out of scope:

- Automatic plan mutation.
- Personality inference.

## Milestone 7.13: Tutor Context Transparency

Objective:

让用户理解 Tutor 使用了哪些上下文。

Scope:

- Show Current Goal in Tutor.
- Show available context: Goal, Plan, Tasks, Sessions, Memory, Knowledge.
- Show retrieval grounding when available.
- Explicitly show when Knowledge is unavailable.

Out of scope:

- New Agent system.
- Direct Tutor to RetrievalService dependency.

---

# Final Recommendation

Study Planet 的下一步不应继续堆功能，而应稳定产品模型：

```text
Current Goal
→ Plan Structure
→ Today Task
→ Study Session
→ Knowledge / Memory Evidence
→ Analytics Insight
→ User-confirmed next action
```

Goal 是 Study Planet 内正确的顶层业务对象。Knowledge 不应强制绑定 Goal。Plan 应由 Goal 驱动，但当前阶段保持手动创建和用户确认。AI 的价值应体现在解释、建议和洞察，而不是隐藏决策或自动改写用户计划。
