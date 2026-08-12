# Universe OS
# 03_UI_DESIGN_SPEC.md

Version: 1.2

Document Type: UI Design Specification

Product: Universe OS

Purpose: Define the visual language, interaction rules, screen states and user experience standards.

> 当前运行时基线：唯一正常入口为 5180 的空间房间。房间、家具热点与模块世界使用
> Three.js；Knowledge/Wordbook 书架阅读器当前是 DOM/CSS 3D 动效，不应误称为
> Three.js 书架。旧 Vue 页面不是用户入口。

---

# 1. Design Philosophy

Universe OS 不是传统 SaaS 应用，不是 admin dashboard，不是 ERP，不是数据管理后台，也不是 ChatGPT clone。

它应该让用户感觉：

> 我进入了自己的个人智能世界。

Study Planet 的体验应该像一个安静、专注、有记忆的学习房间。用户不是在操作菜单，而是在进入一个会理解自己目标、资料、问题和成长轨迹的学习空间。

核心体验路径：

```text
Discover → Enter → Focus → Learn → Review → Grow
```

---

# 2. Global UI Principles

## Principle 1: Planet First

Planet 是主要体验单元。用户不是打开功能列表，而是进入一个世界。

## Principle 2: Each Planet Has Identity

每个 Planet 必须有独立气质：

- Study Planet：calm、focused、knowledge-oriented。
- Work Planet：professional、structured、当前仅开放既有的受限工作区。
- Novel Planet：creative、imaginative、当前仅开放持久化草稿空间。
- Life Planet：personal、rhythmic、future placeholder only in MVP。
- Creator Planet：expressive、maker-oriented、future placeholder only in MVP。

## Principle 3: Next Action First

每个 Study screen 必须清楚显示用户下一步最应该做什么。

要求：

- 首屏有 primary next action。
- AI Recommendation 不藏在页面底部。
- 用户能从当前页面直接继续学习、上传资料、提问、复习或查看结果。

## Principle 4: Context-Aware AI

AI 必须表现为理解当前 Planet 和用户历史的智能体。

AI 可用上下文：

- Current Goal。
- Learning Plan。
- Study Records。
- Knowledge。
- Wrong Questions。
- Review history。
- Planet Memory。

## Principle 5: Avoid Traditional Dashboard Feeling

避免：

- 密集表格。
- 过多卡片堆叠。
- 20 项左侧菜单。
- 企业后台视觉。
- 数据图表占据首屏。
- 普通聊天窗口作为核心体验。

优先使用：

- Workspace。
- Timeline。
- Knowledge Map。
- Focus Mode。
- Intelligent Panel。
- Progress Snapshot。
- Personal Growth Record。

---

# 3. Universe Portal UI

## 3.1 Purpose

Universe Portal 是所有 Planet 的入口。它只负责“进入世界”，不提供复杂业务操作。

## 3.2 Layout

Desktop 概念：

```text
                 Universe OS

                     *

        Study                  Work
       active                coming later

                     Novel
                  coming later

        Life                 Creator
    coming later           coming later
```

## 3.3 Background

概念：deep personal space。

视觉要求：

- 深色空间感背景。
- 动态星点或轻微运动。
- 缓慢、有呼吸感的动效。
- 不使用廉价游戏化特效。
- 不使用企业后台大横幅。

## 3.4 Planet Object

Planet Object 包含：

- Visual identity。
- Name。
- Status。
- Short signal。
- Progress 或 coming later。
- Primary action。

Study Planet 示例：

```text
Study Planet
Status: Active
Today: 1 task
Review: 2 due
Action: Enter
```

Future Planet 示例（仅 Life / Creator）：

```text
Life Planet
Status: Coming later
Action: Preview unavailable
```

## 3.5 Interaction

Hover / Focus：

- 展示 Planet 简介。
- 展示状态。
- Study Planet 可显示 AI Recommendation 摘要。

Click Study Planet：

```text
Portal
→ Planet transition
→ Study Workspace loading
→ Study Home
```

Click Future Planet：

- 展示 coming later 状态。
- 不进入空 Workspace。

---

# 4. Planet Workspace UI

进入 Planet 后，整个应用气质应改变。

Study Planet 应让用户感到：

> 我进入了自己的学习房间。

## 4.1 Workspace Layout

Desktop：

```text
Study Workspace
├── Planet Header
│   ├── Planet Name
│   ├── AI Status
│   └── Memory Status
├── Navigation
│   ├── Home
│   ├── Plan
│   ├── Knowledge
│   ├── Wordbook
│   ├── Tutor
│   ├── Review
│   └── Analytics
├── Main Workspace
└── Contextual AI Panel
```

Navigation 不应呈现为传统后台菜单。它更像空间中的区域切换。

Wordbook 当前以与 Knowledge 一致的实体词汇书呈现：标签映射为书本，点击封面后进入双页阅读和记忆卡；词条保留发音、个人释义、短语、例句、笔记以及背过/记错状态。后续任何词汇花园等替代视图必须复用同一 Wordbook API 和数据所有权，不能另建词库。

## 4.2 Responsive Rules

- Desktop first。
- Tablet second。
- Mobile third。
- Mobile 可以折叠 Navigation，但不能隐藏 primary next action。
- 文本不能溢出按钮、卡片、图表或面板。

---

# 5. Study Planet Visual Language

Theme: Learning Space

感觉：

- Calm。
- Focused。
- Intelligent。
- Personal。

颜色：

- 主色：冷静的蓝或青。
- 辅色：白、深灰、柔和中性色。
- 状态色：成功、警告、错误必须克制。
- 禁止全站单一蓝紫渐变。
- 禁止大量同色卡片堆叠。

字体与布局：

- Hero-scale type 只用于 Portal 或重要入口。
- Study Workspace 内使用紧凑、可读、稳定的层级。
- 卡片圆角不超过 8px，除非未来设计系统另有规定。
- 数据图表只用于解释，不做装饰。

---

# 6. Study Screens

## 6.1 Study Home

Route: `/study`

用户目标：知道今天最应该做什么。

Primary next action：

- 没有 Goal：Create Goal。
- 有 Daily Task：Start Learning。
- 有 Review due：Start Review 可作为次级或并列行动。

内容：

- Current Goal。
- Today’s Primary Task。
- AI Recommendation。
- Review Due。
- Recent Study Records。
- Progress Snapshot。
- Knowledge Status。

Empty State：

- 文案聚焦“创建第一个学习目标”。
- 主按钮：Create Goal。
- 不展示空图表。

Loading State：

- 加载 Goal、Plan、Memory、Analytics。
- 保持空间感和轻量动效。

Success State：

- 今日任务完成后，显示完成反馈、学习时长和下一步建议。

Failure State：

- AI Recommendation 失败时，页面仍展示 Goal 和 Daily Task。
- 提供 Retry。

AI Recommendation：

- 必须说明建议依据，例如“基于 3 天未复习排列组合”。

## 6.2 Plan: Goal and Learning Plan

Route: `/study/plan`

用户目标：把长期目标变成可执行计划。

Primary next action：

- 没有 Goal：Create Goal。
- 有 Goal 但无计划：Generate Plan。
- 有计划：Start Today’s Task 或 Adjust Plan。

UI 形式：

- Goal Type selector：考试目标、知识学习、成长目标。
- Timeline view。
- Goal → Monthly Plan → Weekly Plan → Daily Task。
- 不使用纯表格作为主视图。

Goal 摘要示例：

```text
成为 AI 工程师
Type: 成长目标
Deadline: Long-term
Progress: 35%
AI: Finish today's systems reading session.
```

Empty State：

- 引导选择目标类型，并填写 goal name、description、optional deadline、subjects、daily available minutes。

Loading State：

- Generate Plan 时展示 Planner Agent 正在分析 Goal 和 Memory。

Success State：

- 计划生成后，突出今天第一项任务。

Failure State：

- 计划生成失败时保留 Goal，不清空输入。

AI Recommendation：

- 指出计划风险，例如时间不足、科目偏科、复习间隔过长。

## 6.3 Study Session / Study Record

Route: `/study/session/:id`

用户目标：专注完成一次学习并保存记录。

Primary next action：

- Start Timer。
- Finish Session。
- Save Record。

Focus Mode 内容：

- Current Task。
- Subject / Topic。
- Timer。
- Notes。
- Feeling。
- Contextual Tutor。

Empty State：

- 如果没有从任务进入，允许用户手动选择 subject/topic。

Loading State：

- Session 创建时展示轻量状态。

Success State：

- 保存后显示学习时长、完成任务、建议复习项。

Failure State：

- 保存失败时保留用户输入，允许重试。

AI Recommendation：

- Session 结束后给出一句下一步建议。

## 6.4 Knowledge and File Upload

Route: `/study/knowledge`

用户目标：让资料变成 AI 可理解的 Knowledge。

Primary next action：

- Knowledge 为空：Upload File。
- 有文件处理中：View Processing Status。
- 有资料：Ask with Knowledge 或 Generate Summary。

UI 形式：

- Knowledge Map / Concept view。
- Document list 可以存在，但不能成为唯一主体验。

File Upload 支持：

- PDF。
- Markdown。
- TXT。

Empty State：

- 引导上传第一份资料。

Loading State：

- 展示 processing_status：uploaded、parsing、chunking、embedding、processed、failed。

Success State：

- 文件 processed 后展示 Summary 入口和 Ask with Knowledge。

Failure State：

- 展示失败原因和 Retry Processing。

AI Recommendation：

- 推荐从哪份资料开始总结，或提示资料缺口。

## 6.5 AI Summary

Route: `/study/knowledge/summary/:id`

用户目标：快速理解资料重点。

Primary next action：

- Generate Summary。
- Save to Knowledge。
- Add to Review。

内容结构：

- 标题。
- 核心概念。
- 重点。
- 易错点。
- 示例。
- 复习建议。
- Sources。

Empty State：

- 文件未 processed 时提示等待处理完成。

Loading State：

- 展示 AI 正在读取资料和生成总结。

Success State：

- Summary 生成后可保存、复制、加入 Review。

Failure State：

- 生成失败时保留文件状态，允许重试。

AI Recommendation：

- 指出最值得复习的概念。

## 6.6 Tutor and RAG Q&A

Route: `/study/tutor`

用户目标：获得结合个人资料和学习历史的解释。

Primary next action：

- Ask Question。
- Select Context。
- Save Answer。

UI 形式：

- 不是普通聊天。
- 必须有 Context Selector。
- 必须展示 Sources 和 Related Concepts。

Empty State：

- 没有 Knowledge 时，允许普通解释，但明确提示“上传资料后可获得基于资料的回答”。

Loading State：

- 展示 retrieval、reasoning、answering 状态。

Success State：

- 回答包含解释、例子、来源、下一步建议。

Failure State：

- 检索失败时说明原因，可切换为不基于资料的解释。

AI Recommendation：

- 推荐保存为 Wrong Question、加入 Review 或继续学习某概念。

## 6.7 Wrong Questions

Route: `/study/review/wrong-questions`

用户目标：保存、理解并复习错题。

Primary next action：

- Add Wrong Question。
- Review Due Question。

Card 内容：

- Question。
- Subject / Topic。
- Error Type。
- Correct Answer。
- User Answer。
- AI Analysis。
- Review Date。
- Master Status。

Empty State：

- 引导添加第一道错题，或从 Tutor 回答中保存。

Loading State：

- 加载错题和 Review 状态。

Success State：

- 保存后展示首次 Review 日期。

Failure State：

- 保存失败时保留表单内容。

AI Recommendation：

- 解释错误类型，并推荐复习相关 Concept。

## 6.8 Review

Route: `/study/review`

用户目标：完成今天该复习的内容。

Primary next action：

- Start Today’s Review。
- Mark as Mastered / Need Again。

内容：

- Due Today。
- Upcoming。
- Wrong Questions。
- Important Concepts。
- Review Result。

Empty State：

- 没有待复习项时，展示下一次复习时间或建议学习任务。

Loading State：

- 加载 Review queue。

Success State：

- 完成后显示掌握状态和下一次复习日期。

Failure State：

- 更新状态失败时允许重试。

AI Recommendation：

- 根据 Review 表现调整建议。

## 6.9 Analytics

Route: `/study/analytics`

用户目标：理解自己是否在进步，以及下一步该改变什么。

Primary next action：

- View Recommendation。
- Adjust Plan。
- Review Weak Concepts。

内容：

- Study Time Trend。
- Task Completion。
- Subject Distribution。
- Wrong Question Distribution。
- Review Completion。
- Weak Concepts。
- AI Recommendation。

Empty State：

- 数据不足时提示完成一次 Study Session。
- 不展示空图表墙。

Loading State：

- 加载指标和 AI 分析。

Success State：

- 展示趋势、解释和行动建议。

Failure State：

- 指标加载失败时提供 Retry，并显示已有本地数据。

AI Recommendation：

- 必须指出依据，例如“本周逻辑学习时间低于计划 40%”。

---

# 7. Component System

Global components：

- PlanetObject。
- WorkspaceLayout。
- PlanetHeader。
- ContextualAIPanel。
- Timeline。
- ProgressRing。
- TaskCard。
- MemorySignal。
- KnowledgeNode。
- SourceCitation。
- EmptyState。
- LoadingState。
- ErrorState。

组件规则：

- Icon buttons 使用清晰符号并提供 tooltip。
- 可点击元素必须有 hover/focus/disabled 状态。
- AI 输出必须有 loading、success、failure 状态。
- SourceCitation 必须可追溯到文件或 chunk。

---

# 8. Animation Rules

动画应该：

- Smooth。
- Slow。
- Meaningful。
- 帮助表达“进入世界”或“AI 正在处理”。

避免：

- 过度游戏化。
- 快速闪烁。
- 装饰性强但无意义的粒子爆炸。
- 影响阅读的背景动效。

---

# 9. Forbidden UI Patterns

Codex 和设计实现必须避免：

- Traditional admin dashboard。
- 左侧 20 项菜单。
- 数据表格作为主体验。
- ChatGPT clone。
- Generic SaaS template。
- 大量嵌套卡片。
- 只靠紫蓝渐变建立视觉。
- 用空图表填充无数据状态。
- 把 Future Planet 做成可进入的空页面。

---

# 10. MVP UI Scope

Universe：

- Universe Portal。
- Study Planet active object。
- Work 的受限工作区、Novel 草稿入口，以及 Life/Creator future placeholders。
- Planet entry transition。

Study Planet：

- Study Workspace。
- Study Home。
- Plan: Goal + Learning Plan。
- Study Session / Study Record。
- Knowledge: File Upload + AI Summary。
- Tutor: RAG Q&A。
- Review: Wrong Questions + Review Queue。
- Analytics。

---

# 11. UI Acceptance Criteria

- Given 用户进入 Universe Portal，When 页面加载，Then 首屏应表达 personal universe，而不是后台首页。
- Given 用户进入 Study Planet，When Study Workspace 加载，Then 主导航只出现 Home、Plan、Knowledge、Tutor、Review、Analytics。
- Given 任一 Study screen 首次加载，When 数据为空，Then 页面展示明确 empty state 和 primary action。
- Given AI 正在生成内容，When 用户等待，Then 页面展示 loading state 且不阻塞非相关操作。
- Given AI 或数据请求失败，When 页面渲染，Then 用户看到错误原因、可重试动作和已加载内容。
- Given 用户完成关键动作，When 保存成功，Then 页面显示 success state，并给出下一步建议。

---

# 12. Final UI Goal

Universe OS 应该感觉像一个个人操作系统。

用户不是在使用一个工具。

用户是在进入自己的 Universe，并在 Study Planet 中学习、提问、复习和成长。

---

# End
