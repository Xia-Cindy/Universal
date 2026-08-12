# Universe OS
# 09_STUDY_WORK_PRODUCT_DESIGN.md

Version: 0.2

Document Type: Product Design and Architecture Proposal

Status: Historical design proposal with implementation-status addendum

Scope:

- Study Planet Goal / Knowledge / Plan productization
- RAGFlow PDF embedding validation
- Work Planet initial product design
- Dynamic Resume design

> 2026-08-12 状态说明：本文件中的 Goal 创建、Plan 日历、Work 基础模型、实体书架、
> 资料归属的笔记/知识卡和 Wordbook 记忆卡已有不同程度实现。它们的真实能力与限制以
> `docs/10_PLATFORM_CAPABILITIES_AND_GAPS.md` 为准；本文件中仍标记为“建议”或
> “Recommendation”的数据模型、自动化和 RAGFlow 验收事项均不得视为已交付。

---

# 1. Design Objective

本设计文档用于定义 Universe OS 下一阶段的产品方向。

目标不是新增一堆功能页面，而是让 Universe OS 从 Study Planet 的学习闭环，进一步演进为“学习 → 知识沉淀 → 工作能力 → 职业表达”的个人操作系统。

本阶段设计聚焦四个问题：

1. Study Goal 创建体验过于表单化，需要变成下钻式创建流程。
2. Knowledge 需要根据 Goal 类型呈现不同的知识空间形态。
3. Plan 需要日历化，让每日任务可视化，并为未来 Work Planet Plan 留出统一计划能力。
4. Work Planet 需要一个初版产品模型：技术栈目录、技术内容空间、动态简历。

---

# 2. Architecture Boundary

## 2.1 保持不变

Universe OS 的核心架构保持：

```text
Universe OS
├── AI Core
├── Shared Services
│   ├── Memory
│   ├── Knowledge
│   ├── Retrieval
│   └── File / RAGFlow Provider
└── Planets
    ├── Study Planet
    └── Work Planet
```

## 2.2 禁止事项

本设计不允许：

- 新建第二套 AI Core。
- 让 Work Planet 直接读取 Study Planet 内部业务表。
- 让 Tutor、Analyst 或未来 Work Agent 直接调用 RAGFlow。
- 让前端直接调用 RAGFlow。
- 自动生成虚假学习记录、工作经历或简历项目。
- 自动推断人格、心理画像或隐藏能力标签。
- 在没有用户确认的情况下自动修改计划。

## 2.3 正确共享路径

Study Planet 和 Work Planet 可以共享 Knowledge，但必须经过 Shared Knowledge Service：

```text
Work Planet
→ Knowledge Service
→ Knowledge Provider / RAGFlow
```

不能走：

```text
Work Planet
→ Study Planet repository
```

---

# 3. Product Model Overview

## 3.1 Study Planet 新模型

Study Planet 继续以 Goal 为 Workspace Context。

```text
Study Planet
└── Current Goal
    ├── Goal Knowledge Space
    ├── Learning Roadmap
    ├── Plan Calendar
    ├── Daily Tasks
    ├── Study Sessions
    ├── Tutor
    └── Analytics
```

不同 Goal 类型拥有不同 Knowledge 表现：

| Goal Type | 用户场景 | Knowledge 展示 |
| --- | --- | --- |
| Exam Goal | 考研、证书、资格考试 | 隔离考试知识库 |
| Reading Goal | 阅读一本或多本书 | 书架 |
| Learning Goal | 学习某个知识领域 | 知识卡片 |
| Growth Goal | 长期成长方向 | 混合知识空间 |

## 3.2 Work Planet 新模型

Work Planet 是职业能力空间，不是传统任务看板。

```text
Work Planet
├── Work Home
├── Tech Stack
│   └── Tech Stack Detail
├── Work Knowledge
├── Projects / Experience
├── Dynamic Resume
└── Interview Prep
```

Work Planet 的核心问题是：

> 我正在积累哪些工作能力？这些能力如何变成岗位竞争力？

---

# 4. Study Goal Creation Redesign

## 4.1 Current Problem

当前 Goal 创建更像普通 CRUD 表单。

问题：

- 用户一进入就被要求填写完整表单。
- 不同 Goal 类型使用同一套字段，导致考试信息、阅读信息、知识学习信息混在一起。
- Create Goal 行为缺少仪式感，不像进入一个个人学习空间。

## 4.2 Target Experience

Study Home / Header 不直接展示完整创建表单。

只展示一个主按钮：

```text
Create Goal
```

点击后进入下钻页面：

```text
/study/goals/new
```

## 4.3 Goal Creation Flow

```text
Step 1: 选择目标类型
→ Step 2: 填写目标信息
→ Step 3: 配置 Knowledge Space
→ Step 4: 进入 Study Workspace
```

### Step 1: Goal Type

用户选择：

- 考试目标
- 阅读目标
- 知识学习目标
- 成长目标

### Step 2: Goal Info

通用字段：

- 目标名称
- 描述
- 截止时间，可选
- 当前水平
- 每日可用时间
- 优先级

考试目标额外字段：

- 考试名称
- 考试日期
- 考试科目

阅读目标额外字段：

- 书名
- 作者，可选
- 阅读状态
- 阅读标签

知识学习目标额外字段：

- 知识领域
- 初始主题
- 学习产出类型

成长目标额外字段：

- 成长方向
- 时间周期
- 阶段目标

## 4.4 Acceptance Criteria

- Given 用户没有 Goal，When 点击 Create Goal，Then 进入 `/study/goals/new`。
- Given 用户选择考试目标，When 创建成功，Then 系统创建一个 Goal-scoped Knowledge Space。
- Given 用户选择阅读目标，When 创建成功，Then Knowledge 页面使用书架视图。
- Given 用户选择知识学习目标，When 创建成功，Then Knowledge 页面使用知识卡片视图。
- Given 用户取消创建，When 返回，Then 不产生空 Goal。

---

# 5. Goal-aware Knowledge Spaces

## 5.1 Design Principle

Knowledge 不应只有一种“文件列表”形态。

Knowledge 的底层仍然是共享 Knowledge Service，但用户看到的形态由 Goal 类型决定。

```text
Knowledge Service
├── Document
├── Chunk
├── Provider Metadata
├── Tags
├── Collections
└── Goal Relation
```

---

## 5.2 Exam Goal Knowledge Space

### Product Intent

考试目标的知识库必须隔离，因为不同考试的科目、资料和检索上下文不同。

示例：

```text
AI 方向研究生
├── 408 数据结构
├── 数学基础
├── 机器学习
└── 英语
```

另一个考试目标：

```text
PMP
├── 项目管理过程组
├── 敏捷
└── 模拟题
```

两个 Goal 的 Knowledge 不应默认混合。

### Recommended Implementation

短期：

- `documents.goal_id` 必填或默认绑定当前 Exam Goal。
- Retrieval 默认带 `goal_id` filter。
- UI 默认只显示当前 Exam Goal 的资料。

中期：

- 每个 Exam Goal 可映射一个 RAGFlow dataset。
- `provider_dataset_id` 可按 Goal 维度存储。

### Acceptance Criteria

- Given 用户在 Exam Goal A 上传资料，When 切换到 Exam Goal B，Then 默认看不到 Goal A 的资料。
- Given Tutor 在 Exam Goal B 中回答问题，Then 默认不检索 Goal A 的 Knowledge。
- Given 用户主动选择 All Knowledge，Then 可跨 Goal 查看，但必须有明确提示。

---

## 5.3 Reading Goal Bookshelf

### Product Intent

阅读目标的 Knowledge 应像书架，而不是普通文件列表。

```text
Reading Goal: 阅读 CSAPP
└── Bookshelf
    ├── CSAPP
    │   ├── PDF
    │   ├── 阅读笔记
    │   ├── 章节标签
    │   └── 摘录卡片
    └── Supplementary Reading
```

### Book Model

建议新增概念模型：

```text
KnowledgeCollection
├── id
├── user_id
├── goal_id
├── type: book
├── title
├── author
├── status
├── tags
└── created_at
```

一个 Book 可以关联多个 Document：

- PDF
- Markdown notes
- TXT notes
- 手动摘录

### Book Tags

每本书可自定义标签：

- 数据结构
- 操作系统
- 计算机系统
- 难读
- 已读
- 待读
- 重点复习

### Acceptance Criteria

- Given 当前 Goal 是 Reading Goal，When 进入 Knowledge，Then 默认展示 Bookshelf。
- Given 用户上传一本 PDF，When 选择关联 Book，Then 文档归入该书。
- Given 用户给书添加标签，When 返回书架，Then 标签可见并可筛选。

---

## 5.4 Learning Goal Knowledge Cards

### Product Intent

知识学习目标不是围绕考试科目，也不一定围绕书。

它更适合用知识卡片组织：

```text
Learning Goal: 学习 RAG 系统
├── Card: 什么是 Chunking
├── Card: Embedding 模型选择
├── Card: RAGFlow Provider Adapter
└── Card: 检索质量评估
```

### Knowledge Card Model

建议新增概念模型：

```text
KnowledgeCard
├── id
├── user_id
├── goal_id
├── title
├── summary
├── body
├── tags
├── linked_document_ids
├── linked_chunk_ids
├── source_type
└── created_at
```

卡片可以：

- 手动创建。
- 关联文档。
- 关联 chunk。
- 作为 Tutor / Analytics 的上下文来源。

### Acceptance Criteria

- Given 当前 Goal 是 Learning Goal，When 进入 Knowledge，Then 展示 Card view。
- Given 用户创建知识卡片，When 保存，Then 卡片绑定当前 Goal。
- Given 卡片关联文档，When 查看卡片，Then 可看到来源文档。

---

# 6. Study Plan Calendar

## 6.1 Current Problem

当前 Plan 仍偏层级对象展示。

即使已经从 Long Term / Monthly / Weekly / Daily 的原始按钮改成路线图，用户仍不容易感知：

- 哪天做什么。
- 哪些任务堆积。
- 哪些任务超时。
- 本周优先级如何调整。

## 6.2 Target Experience

Plan 页面增加 Calendar：

```text
Study Plan
├── Learning Roadmap
├── Current Stage
├── Weekly Focus
├── Calendar
└── Today's Mission
```

Calendar 展示：

- 每日任务。
- 完成状态。
- 预计学习时长。
- 优先级。
- 当前 session 状态。

## 6.3 Task Priority

Daily Task 增加用户可见优先级：

- High
- Medium
- Low

Calendar 上通过视觉权重展示：

- High：更强提示。
- Medium：普通任务。
- Low：轻量任务。

## 6.4 Work Planet Integration Preparation

Calendar 未来应成为跨 Planet 的计划呈现模式，但不是共享业务表。

建议抽象：

```text
Plan Event
├── planet_type
├── source_type
├── source_id
├── title
├── date
├── duration_minutes
├── priority
├── status
└── route
```

Study Planet 生成 Study Plan Event。

Work Planet 生成 Work Plan Event。

前端可以复用 Calendar component，但 backend 仍按 Planet 边界提供数据。

## 6.5 Acceptance Criteria

- Given 当前 Goal 有 Daily Tasks，When 进入 Plan，Then Calendar 显示任务分布。
- Given 用户修改任务优先级，When 返回 Calendar，Then 优先级变化可见。
- Given 用户点击某日任务，Then 可进入任务编辑或 Start Learning。
- Given 当前是 Work Planet，Then 未来可复用 Calendar UI，但数据来自 Work API。

---

# 7. PDF Embedding / RAGFlow Validation

## 7.1 Current Observation

RAGFlow provider 接收 PDF 后，Universe 会记录：

- `providerDatasetId`
- `providerDocumentId`
- `providerStatus`

此前文档可能停留在：

```text
chunking
```

此前 embedding provider key 曾阻止异步处理；该部署配置已修复。2026-08-13 的受控 TXT、Markdown 与新 PDF runtime sample 已确认解析、embedding、状态轮询、chunk cache、Retrieval 与 Tutor 来源链路通过；既有长 PDF 仍按各自状态单独核对。

## 7.2 Required Diagnosis

需要单独做 RAGFlow runtime validation。

检查项：

- RAGFlow 当前 API / embedding provider 配置是否有效。
- RAGFlow dataset 是否创建成功。
- RAGFlow 是否配置 embedding model。
- PDF parser 是否可用。
- RAGFlow document status 是否从 queued / running 进入 done。
- Universe 是否能轮询 provider status。
- Universe 是否能拉取 provider chunks。
- RetrievalService 是否能搜索 provider-backed chunks。

## 7.3 Product Behavior

PDF 不应只显示模糊的 `chunking`，也不应因为旧 local fallback 规则而跳过 provider 处理。

建议状态：

```text
Uploaded to RAGFlow
Parsing PDF
Embedding in progress
Ready for Q&A
Failed: parser not available
Failed: embedding model not configured
```

## 7.4 Acceptance Criteria

- Given PDF 已上传到 RAGFlow，When RAGFlow 仍在解析，Then UI 显示明确 processing state 并自动轮询。
- Given RAGFlow provider 已启用，When 用户上传 PDF，Then Universe 自动提交处理，不要求用户额外点击旧的 local `Process` 行为。
- Given RAGFlow embedding model 未配置，When 处理失败，Then UI 显示可理解错误。
- Given RAGFlow 处理完成，When 打开文档详情，Then Universe 拉取 chunk preview。
- Given chunk ready，When Tutor 提问，Then Retrieval 通过 ToolRouter 返回相关 chunks。

---

# 8. Work Planet Initial Design

## 8.1 Product Positioning

Work Planet 是职业能力工作空间。

它不是传统项目管理工具，也不是企业后台系统。

Work Planet 回答三个问题：

1. 我正在积累哪些职业能力？
2. 我的技术栈和项目证据是什么？
3. 我如何把这些能力表达成不同岗位的简历？

## 8.2 Work Planet IA

```text
Work Planet
├── Work Home
├── Tech Stack
├── Projects
├── Work Knowledge
├── Dynamic Resume
└── Interview Prep
```

## 8.3 Work Home

Work Home 只回答：

> 当前职业成长下一步是什么？

展示：

- 当前职业方向。
- 重点技术栈。
- 最近项目证据。
- 简历准备状态。
- 下一步行动。

## 8.4 Tech Stack Directory

Tech Stack 是 Work Planet 的核心目录。

示例：

```text
Tech Stack
├── Python
├── SQL
├── FastAPI
├── Vue
├── RAG
├── Data Analysis
└── Digital Transformation
```

每个技术栈卡片展示：

- 技术名称。
- 熟练度。
- 关联知识。
- 关联项目。
- 最近学习 / 使用记录。
- 简历可用证据数。

## 8.5 Tech Stack Detail

点击技术栈后下钻到详情页：

```text
/work/tech-stack/:id
```

详情页展示：

- Overview
- Knowledge
- Projects
- Evidence
- Learning History
- Resume Snippets

## 8.6 Work Knowledge

Work Planet 可以引用 Study Planet 的 Knowledge，但必须通过 Shared Knowledge Service。

允许：

- 引用 Study 中的 RAG、FastAPI、SQL、AI 工程资料。
- 将某个知识卡片标记为 Work-relevant。
- 将学习资料转化为项目证据。

不允许：

- Work 直接读取 Study repository。
- Work 修改 Study Goal / Plan / Task。

---

# 9. Dynamic Resume

## 9.1 Product Intent

动态简历不是简单的文本编辑器。

它根据 Work Planet 中的技术栈、项目、知识、证据，为不同岗位生成不同版本简历。

核心问题：

> 面向这个岗位，我应该如何表达自己的能力？

## 9.2 Resume Inputs

Dynamic Resume 使用：

- 用户手动填写的基础信息。
- Work Planet 技术栈。
- Work Projects。
- Knowledge evidence。
- Study / Work 学习记录。
- 用户确认过的项目经历。

## 9.3 Role-based Resume Versions

支持岗位版本：

- AI Engineer
- Data Analyst
- Backend Engineer
- Digital Transformation Consultant
- Product / AI Product Manager

每个岗位版本包含：

- Summary
- Skills
- Project Experience
- Work Experience
- Education / Certification
- Knowledge Evidence
- Gaps / Next Preparation

## 9.4 Evidence Rule

Resume 不能凭空生成经历。

每一条项目或技能建议需要标记来源：

```text
Source
├── user-entered
├── work-project
├── knowledge-card
├── study-record
└── manual-confirmed
```

AI 只能生成草稿，必须由用户确认。

## 9.5 Dynamic Update

当 Work Planet 更新时：

- 新增技术栈。
- 新增项目证据。
- 新增 Knowledge。
- 新增学习记录。

Resume 可以提示：

```text
Your Backend Engineer resume has 2 new evidence items available.
```

但不能自动覆盖已确认简历。

## 9.6 Acceptance Criteria

- Given 用户创建一个技术栈，When 打开 Resume，Then 可将该技术栈加入某岗位简历草稿。
- Given 用户没有项目证据，When 生成简历，Then 系统明确提示缺少证据。
- Given 用户选择 AI Engineer 岗位，When 生成草稿，Then 技能和项目排序偏向 AI / backend / RAG 相关内容。
- Given Work Planet 新增证据，When 返回 Resume，Then 显示可更新提示，不自动覆盖旧版本。

---

# 10. Data Model Direction

## 10.1 Study Extensions

建议新增或扩展：

```text
knowledge_collections
├── id
├── user_id
├── goal_id
├── type
├── title
├── description
├── tags
└── status
```

```text
knowledge_cards
├── id
├── user_id
├── goal_id
├── collection_id
├── title
├── summary
├── body
├── tags
├── linked_document_ids
├── linked_chunk_ids
└── created_at
```

```text
daily_tasks
新增:
├── priority
└── calendar_date
```

## 10.2 Work Planet Foundation

建议新增：

```text
work_profiles
├── id
├── user_id
├── target_direction
└── status
```

```text
tech_stacks
├── id
├── user_id
├── name
├── category
├── proficiency
├── description
├── tags
└── status
```

```text
work_projects
├── id
├── user_id
├── title
├── description
├── tech_stack_ids
├── evidence_ids
└── status
```

```text
resume_versions
├── id
├── user_id
├── role_target
├── title
├── content
├── evidence_refs
├── status
└── updated_at
```

## 10.3 Shared Knowledge References

Work Planet 不复制 Study Knowledge。

使用引用关系：

```text
knowledge_refs
├── id
├── user_id
├── source_planet
├── target_planet
├── knowledge_type
├── knowledge_id
├── relation_type
└── created_at
```

---

# 11. API Direction

## 11.1 Study Goal Creation

```text
GET  /api/study/goals/new/options
POST /api/study/goals
```

保持现有 Goal API 兼容，但前端改为下钻创建体验。

## 11.2 Knowledge Space

```text
GET  /api/study/goals/{goal_id}/knowledge-space
POST /api/knowledge/collections
POST /api/knowledge/cards
GET  /api/knowledge/cards
PATCH /api/knowledge/cards/{card_id}
```

## 11.3 Plan Calendar

```text
GET   /api/study/plans/calendar
PATCH /api/study/tasks/{task_id}
```

未来 Work Planet：

```text
GET /api/work/plans/calendar
```

## 11.4 Work Planet

```text
GET  /api/work/home
GET  /api/work/tech-stacks
POST /api/work/tech-stacks
GET  /api/work/tech-stacks/{tech_stack_id}
POST /api/work/projects
GET  /api/work/resumes
POST /api/work/resumes/draft
```

---

# 12. Frontend Direction

## 12.1 Study Frontend

新增或重构：

```text
frontend/src/planets/study/goals/new/
├── GoalTypePicker.vue
├── GoalDetailsForm.vue
└── GoalKnowledgeSetup.vue
```

```text
frontend/src/planets/study/knowledge/
├── ExamKnowledgeSpace.vue
├── BookshelfView.vue
├── KnowledgeCardView.vue
└── KnowledgeTagEditor.vue
```

```text
frontend/src/planets/study/plan/
├── PlanCalendar.vue
├── TaskPriorityEditor.vue
└── CalendarTaskDetail.vue
```

## 12.2 Work Frontend

新增：

```text
frontend/src/planets/work/
├── layout/WorkWorkspace.vue
├── home/WorkHome.vue
├── tech-stack/TechStackDirectory.vue
├── tech-stack/TechStackDetail.vue
├── resume/DynamicResume.vue
└── projects/WorkProjects.vue
```

---

# 13. Milestone Roadmap

## Milestone 7.9 Study Goal and Plan Productization

Scope:

- Create Goal 下钻式页面。
- Plan Calendar。
- Daily Task priority。
- Home / Plan primary action 保持 backend-owned。

Not included:

- Work Planet。
- Dynamic Resume。
- Knowledge Cards 完整实现。

## Milestone 8.x RAGFlow Runtime Validation

Scope:

- PDF processing status polling。
- RAGFlow embedding configuration diagnostics。
- Chunk preview refresh。
- Provider error normalization。
- Retrieval smoke tests against provider-backed documents。

Not included:

- Work Planet。
- Resume。

## Milestone 9.0 Goal-aware Knowledge Spaces

Scope:

- Exam Goal isolated Knowledge Space。
- Reading Goal Bookshelf。
- Learning Goal Knowledge Cards。
- Tags and collections。

Not included:

- Dynamic Resume。
- Work Planet full implementation。

## Milestone 10.0 Work Planet Foundation

Scope:

- Work Planet registration。
- Work Workspace。
- Tech Stack directory。
- Tech Stack detail。
- Shared Knowledge references。

Not included:

- Full AI Work Agent。
- Resume generation。

## Milestone 10.5 Dynamic Resume Foundation

Scope:

- Resume versions。
- Role target selection。
- Evidence-based resume draft。
- Resume update suggestions。

Not included:

- Automatic job application。
- Fabricated experience generation。

---

# 14. Open Decisions

## Decision 001: Exam Goal Knowledge Isolation

Options:

1. Filter by `goal_id` inside one user-level RAGFlow dataset.
2. Create one RAGFlow dataset per Exam Goal.

Recommendation:

- Start with `goal_id` filtering.
- Move to per-goal dataset if retrieval quality or isolation requires stronger separation.

## Decision 002: Knowledge Cards Persistence

Options:

1. Store cards as first-class database records.
2. Store cards as markdown documents with metadata.

Recommendation:

- Store cards as first-class records.
- Allow cards to link to documents/chunks.

## Decision 003: Calendar Ownership

Options:

1. Shared calendar table.
2. Planet-owned tasks exposed through common Plan Event API shape.

Recommendation:

- Use Planet-owned data.
- Expose common Plan Event response shape to frontend.

## Decision 004: Dynamic Resume AI Boundary

Options:

1. AI can auto-update resume.
2. AI only suggests draft updates and requires user confirmation.

Recommendation:

- AI only suggests.
- User must confirm before resume version changes.

---

# 15. Implementation Readiness Checklist

Before implementation:

- Confirm Milestone order.
- Commit or isolate current uncommitted RAGFlow / Study smoke-test changes.
- Decide Exam Goal Knowledge isolation strategy.
- Decide whether KnowledgeCollection / KnowledgeCard require new migrations in Milestone 9.
- Validate RAGFlow PDF processing with real provider status polling.

Definition of done for each milestone:

- Code implemented.
- Database migration added when required.
- API tests added.
- Frontend build passes.
- Backend tests pass.
- Documentation updated.
- Commit created.
