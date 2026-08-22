# Universe OS
# 02_INFORMATION_ARCHITECTURE.md

Version: 1.2

Document Type: Information Architecture Specification

Product: Universe OS

Purpose: Define the structural relationship between Universe, Planet, Workspace, Module, Agent, Memory and Knowledge.

---

# 1. Information Architecture Overview

Universe OS 使用多层信息架构：

```text
Universe OS
└── Universe Portal
    └── Planet
        └── Workspace
            └── Module
                └── Feature
```

核心原则：

- Universe Portal 是世界入口，不是功能 Dashboard。
- Planet 是独立智能空间。
- Workspace 是进入 Planet 后的完整工作区。
- Module 是 Workspace 内的功能单元。
- AI Core、Memory、Knowledge 是跨 Planet 的共享底层能力。

---

# 2. Canonical Terms

| Term | Definition | MVP Usage |
| --- | --- | --- |
| Universe OS | 个人 AI 操作系统整体 | 产品总称 |
| Universe Portal | 所有 Planet 的入口 | MVP 首屏 |
| Planet | 独立智能应用空间 | Study 为核心空间；Work 与 Novel 提供已实现的受限工作区 |
| Workspace | Planet 内完整工作空间 | Study Workspace |
| Module | Workspace 内功能模块 | Study Home、Learning Plan 等 |
| Agent | 专门执行任务的 AI 角色 | Study Agent |
| Memory | 用户目标、偏好、历史和关键事件 | Global、Planet、Session 三层 |
| Knowledge | 文件、概念、错题、总结和关系 | 支撑 RAG Q&A |
| RAG | Retrieval-Augmented Generation | 基于 Knowledge 的问答 |

---

# 3. Universe Portal IA

## 3.1 定位

Universe Portal 只负责“进入世界”。它不承载复杂业务数据，不展示密集表格，不替代 Study Home。

用户在 Portal 中应感受到：

- 自己拥有一个个人智能宇宙。
- Study Planet 是当前的核心学习空间。
- Work Planet 提供已实现的业务工作区；Novel 只提供草稿写作入口。
- Life 与 Creator 是未来扩展方向。

## 3.2 Portal 结构

```text
Universe OS Room
├── Study: active
│   ├── Home / Goals / Tutor
│   ├── Plan / Review / Analytics
│   └── Knowledge / Wordbook / Recall Board
├── Work: active
│   └── Case Home / Cases / Tech Stack / Projects / Resume
├── Novel: persisted draft workspace
├── Life: future
└── Creator: future
```

## 3.3 Planet Card/Object 信息

每个 Planet 对象必须包含：

- Planet name。
- Visual identity。
- Status。
- Short description。
- Primary action。

Study Planet：

- Status：active。
- Primary action：Enter Study Planet。
- 可展示今日学习提示，例如 Today: 1 task / Review: 2 items。

Work / Novel：

- Work：可进入，使用既有 Work service 与共享 Knowledge。
- Novel：仅提供草稿写作，不新增 Novel Agent。

Future Planet：

- Status：coming later。
- Primary action：不可进入或展示 Coming Later。
- 不展示虚假的业务数据。

## 3.4 Planet 进入流程

```text
Click Study Planet
→ Planet Loader
→ Load Study Workspace configuration
→ Initialize Study Agent
→ Load Planet Memory
→ Open Study Workspace
```

---

# 4. Planet Architecture

每个 Planet 必须遵循统一结构：

```text
Planet
├── Workspace
├── Modules
├── Agent
├── Planet Memory
├── Knowledge Scope
├── Tools
└── Planet Data
```

规则：

- Planet 之间不能直接共享 UI。
- Planet 之间不能直接依赖彼此业务数据。
- Planet 可以共享 AI Core、User Identity、Memory Service、Knowledge Service、File Service。
- 新增 Planet 必须通过 Planet Engine 注册，不能修改 Universe Portal 的核心结构。

---

# 5. Study Planet IA

## 5.1 Root Structure

```text
Study Planet
└── Study Workspace
    ├── Study Home
    ├── Goal
    ├── Learning Plan
    ├── Study Record
    ├── File Upload
    ├── AI Summary
    ├── Knowledge
    ├── RAG Q&A
    ├── Tutor
    ├── Wrong Questions
    ├── Review
    └── Analytics
```

## 5.2 MVP Navigation

主导航建议控制在 6 个一级入口，避免传统后台菜单感：

```text
Study Workspace Navigation
├── Home
├── Plan
├── Knowledge
├── Tutor
├── Review
└── Analytics
```

二级能力归属：

- Goal 属于 Plan。
- Learning Plan 属于 Plan。
- Study Record 从 Home 的 Start Learning 进入，也可在 Plan 任务中进入。
- File Upload 属于 Knowledge。
- AI Summary 属于 Knowledge 和文件详情。
- RAG Q&A 属于 Tutor 或 Knowledge。
- Wrong Questions 属于 Review。

## 5.3 Route Mapping

| User-facing Module | Route | Technical Module ID |
| --- | --- | --- |
| Study Home | /study | dashboard |
| Goal | /study/goals | goal |
| Learning Plan | /study/plan | plan |
| Study Record | Study Home / Plan execution flow | study_record |
| File Upload | /study/knowledge | file_upload |
| AI Summary | Knowledge document flow | ai_summary |
| Knowledge | /study/knowledge | knowledge |
| RAG Q&A | /study/tutor | rag_qa |
| Tutor | /study/tutor | tutor |
| Wrong Questions | /study/review | wrong_questions |
| Review | /study/review | review |
| Analytics | /study/analytics | analytics |

---

# 6. Study Home IA

路径：`/study`

目的：回答“今天我最应该做什么？”

内容结构：

```text
Study Home
├── Current Goal
├── Primary Next Action
│   ├── Today's Daily Task
│   └── Start Learning
├── AI Recommendation
├── Review Due
├── Recent Study Records
├── Knowledge Status
└── Progress Snapshot
```

状态：

- Empty：没有 Goal 时，主行动为 Create Goal。
- Loading：加载 Goal、Plan、Memory、Analytics。
- Success：今日任务完成后展示完成状态和下一步建议。
- Failure：AI Recommendation 加载失败时，基础内容仍可用。

---

# 7. Plan IA

路径：`/study/plan`

包含：

```text
Plan
├── Goal
│   ├── Goal Type: exam / learning / growth
│   ├── Goal Name
│   ├── Description
│   ├── Deadline: optional
│   ├── Subjects / Topics
│   ├── Current Level
│   └── Daily Available Minutes
├── Learning Plan
│   ├── Monthly Plan
│   ├── Weekly Plan
│   └── Daily Task
└── Plan Adjustment
```

Goal 是 Plan 的上层上下文。没有 Goal 时不能生成 Learning Plan。

---

# 8. Knowledge IA

路径：`/study/knowledge`

Knowledge 不是文件管理器，而是学习资料、概念和关系的个人知识空间。

结构：

```text
Knowledge
├── File Upload
├── Documents
├── Chunks
├── Subjects
├── Topics
├── Concepts
├── AI Summaries
├── Related Wrong Questions
└── Relationships
```

主要对象：

- Document：用户上传的原始资料。
- Chunk：RAG 检索单元。
- Concept：AI 或用户识别出的概念。
- Summary：对 Document 或 Study Record 的总结。
- Relationship：概念、资料、错题、复习项之间的关系。

示例：

```text
MEM
└── Math
    └── Permutation
        ├── Document: 数学讲义.pdf
        ├── Summary: 排列组合核心概念
        ├── Wrong Question: 例题 03
        └── Review: 2026-07-08
```

---

# 9. Tutor IA

路径：`/study/tutor`

Tutor 不是普通聊天。它是带有 Study Context 的学习老师。

页面结构：

```text
Tutor
├── Question Input
├── Context Selector
│   ├── Current Goal
│   ├── Subject
│   ├── Topic
│   └── Selected Documents
├── AI Thinking / Retrieval Status
├── Answer
├── Sources
├── Related Concepts
├── Suggested Next Action
└── Save Actions
    ├── Save as Note / Learning Event
    └── Save as Wrong Question
```

RAG Q&A 是 Tutor 的一种模式。只要回答使用 Knowledge 检索，就必须展示来源。

---

# 10. Review IA

路径：`/study/review`

包含：

```text
Review
├── Due Today
├── Upcoming
├── Wrong Questions
├── Important Concepts
├── Review Result
└── Master Status
```

Wrong Questions 路径：`/study/review/wrong-questions`

Wrong Questions 是 Review 的核心来源之一，不作为主导航的独立一级入口。

---

# 11. Analytics IA

路径：`/study/analytics`

Analytics 用于解释学习状态，而不是展示大量图表。

内容结构：

```text
Analytics
├── Study Time Trend
├── Task Completion
├── Subject Distribution
├── Wrong Question Distribution
├── Review Completion
├── Weak Concepts
└── AI Recommendation
```

空数据时必须展示建议行动，例如“完成第一次 Study Session 后将生成趋势”。

---

# 12. Memory Architecture

Memory 分三层：

## 12.1 Global Memory

所有 Planet 共享。

示例：

- user_name: Cindy
- long_term_interest: AI/Data professional
- preferred_language: Chinese

## 12.2 Planet Memory

属于单个 Planet。

Study 示例：

- current_exam: MEM
- active_goal_id
- weak_subjects
- preferred_study_time

## 12.3 Session Memory

一次学习过程内的临时上下文。

示例：

- study_session_id
- subject
- topic
- started_at
- recent_questions

---

# 13. Knowledge Relationship Rules

Knowledge 中的对象关系应支持以下边：

- Document contains Chunk。
- Chunk mentions Concept。
- Concept belongs_to Subject。
- Topic includes Concept。
- Wrong Question tests Concept。
- Summary explains Document。
- Review targets Concept 或 Wrong Question。
- Tutor Answer cites Chunk。

这些关系服务于 RAG Q&A、Review 和 Analytics。

---

# 14. Future Planet Extension

未来新增 Planet 时，只需要创建：

```text
New Planet
├── Workspace
├── Modules
├── UI Identity
├── Agent
├── Tools
├── Planet Memory
└── Knowledge Scope
```

不能修改：

- Universe Core 的基本入口模型。
- AI Core 的共享边界。
- Memory Service 的三层结构。
- Knowledge Service 的通用对象模型。

当前/未来 Planet 边界：

- Work Planet：已有受限工作区，必须经过 shared Knowledge、Memory 与 API 边界。
- Novel Planet：已有持久化草稿空间，不新增 Novel Agent。
- Life Planet。
- Creator Planet。

Health Planet、Finance Planet 等可以作为更远期想法，但不进入当前文档主范围。

---

# 15. IA Acceptance Criteria

- Given 用户打开 Universe Portal，When Study Planet 可用，Then Study Planet 显示 active 状态；Work 与 Novel 只展示其已交付的受限入口，Life 与 Creator 显示 coming later。
- Given 用户点击 Future Planet，When Planet 未实现，Then 系统展示 coming later，不进入空 Workspace。
- Given 用户进入 Study Planet，When Workspace 加载完成，Then 主导航只展示 Home、Plan、Knowledge、Tutor、Review、Analytics。
- Given 用户需要上传资料，When 进入 Knowledge，Then File Upload 作为 Knowledge 内主行动出现。
- Given 用户需要管理错题，When 进入 Review，Then Wrong Questions 作为 Review 内二级能力出现。

---

# 16. Design Goal

最终用户体验不是“打开软件”，而是：

进入自己的 Universe。

点击 Study，进入学习宇宙。

未来点击 Novel，进入创作宇宙。

未来点击 Work，进入工作宇宙。

Universe OS 成为个人 AI 操作系统。

---

# End
