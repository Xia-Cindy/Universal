# Universe OS
# 01_PRD.md

Version: 1.1

Document Type: Product Requirement Document

Status: Draft

Product: Universe OS

First Planet: Study Planet

---

# 1. 产品概述

## 1.1 产品定位

Universe OS 是一个个人 AI 操作系统。它不是普通工具集合，也不是传统 SaaS Dashboard，而是由多个 Planet 组成的个人智能世界。

每个 Planet 是一个独立智能 Workspace，拥有自己的视觉、导航、Agent、Memory、Knowledge 和业务数据。

第一阶段只实现：

- Universe Portal
- Study Planet

Study Planet 是 Universe OS 的第一个 Planet，定位为 AI 学习操作系统。它帮助用户围绕一个长期学习目标完成计划、记录、资料理解、AI 辅导、错题复习和学习分析。

## 1.2 核心体验

用户打开产品时，不是“进入一个后台系统”，而是进入自己的 Universe。

用户点击 Study Planet 后，进入一个专属学习空间。系统应立即回答一个问题：

> 今天我最应该做什么？

## 1.3 MVP 要解决的问题

Study Planet MVP 聚焦单个学习者的个人学习闭环：

1. 明确长期目标。
2. 将长期目标拆成可执行学习计划。
3. 记录真实学习行为。
4. 上传学习资料并让 AI 理解。
5. 基于资料进行 AI Summary 和 RAG Q&A。
6. 管理 Wrong Questions。
7. 按 Review 节奏复习。
8. 通过 Analytics 看见学习趋势和下一步建议。

## 1.4 非 MVP 范围

以下能力不进入 MVP：

- Work Planet、Novel Planet、Life Planet、Creator Planet 的完整功能。
- 多用户协作、班级、教师后台、组织管理。
- 社交、商城、内容分发、公开课程市场。
- 复杂考试题库交易系统。
- 移动端原生 App。
- 视频转写、音频转写、大规模 OCR 处理，除非底层 File Processing 已经具备稳定能力。

Work Planet、Novel Planet、Life Planet、Creator Planet 可以在 Universe Portal 中作为未来 Planet 占位展示，但不能在 MVP 中实现实际业务模块。

---

# 2. 用户画像

## Persona 001: Cindy

- 年龄：27 岁
- 职业：企业数字化实施工程师
- 地点：北京
- 学习目标：管理类联考 MEM
- 技术背景：SQL、Python 基础、数据分析兴趣、AI 应用兴趣

## 当前问题

1. 学习计划难以坚持，不知道每天优先做什么。
2. 学过的知识容易遗忘，复习节奏依赖自觉。
3. PDF、笔记、错题和资料分散，缺少统一 Knowledge。
4. 不清楚自己的学习效果和薄弱点。
5. 遇到问题时缺少能结合个人资料和历史记录的长期 Tutor。

## 用户成功定义

当 Cindy 使用 MVP 一周后，她应该能够：

- 看到一个围绕 MEM 目标生成的 Learning Plan。
- 每天进入 Study Home 后直接开始当天最重要任务。
- 上传教材或笔记后获得 AI Summary。
- 对上传资料进行 RAG Q&A，并看到引用来源。
- 保存 Wrong Questions，并收到 Review 提醒。
- 在 Analytics 中看到学习时间、任务完成率、薄弱知识点和 AI 建议。

---

# 3. 术语与命名规范

## 3.1 产品层级

- Universe OS：完整个人 AI 操作系统。
- Universe Portal：所有 Planet 的入口，不是 Dashboard。
- Planet：独立智能应用空间，例如 Study Planet。
- Workspace：进入 Planet 后的完整工作空间，例如 Study Workspace。
- Module：Workspace 内的功能模块。
- Agent：面向特定任务的 AI 工作角色。
- AI Core：所有 Planet 共享的 AI 能力层。
- Memory：记录用户目标、偏好、学习历史和关键事件。
- Knowledge：由文件、笔记、错题、概念和关系组成的个人知识系统。
- RAG：基于 Knowledge 检索并生成回答的能力。

## 3.2 Study Planet 模块命名

以下名称为 MVP 统一口径：

| Canonical Name | 用户展示名称 | 技术模块 id | 说明 |
| --- | --- | --- | --- |
| Study Home | Study Home | dashboard | 进入 Study Planet 后的首页，不称 Statistics Dashboard |
| Goal | Goal | goal | 长期学习目标 |
| Learning Plan | Learning Plan | plan | 年/月/周/日计划 |
| Study Record | Study Record | study_record | 学习 Session 和学习记录 |
| File Upload | File Upload | file_upload | 上传学习资料 |
| AI Summary | AI Summary | ai_summary | 对资料或记录生成总结 |
| Knowledge | Knowledge | knowledge | 原 Knowledge Base，用户侧统一称 Knowledge |
| Wordbook | Wordbook | wordbook | 与学习 Goal 关联的个人单词、词组、例句和笔记空间 |
| RAG Q&A | RAG Q&A | rag_qa | 基于 Knowledge 的问答 |
| Tutor | Tutor | tutor | 原 AI Tutor，用户侧统一称 Tutor |
| Wrong Questions | Wrong Questions | wrong_questions | 错题管理 |
| Review | Review | review | 复习提醒与复习队列 |
| Analytics | Analytics | analytics | 原 Statistics/Learning Analytics |

不再使用的用户侧名称：

- Statistics
- Knowledge Base
- AI Tutor
- Courses
- Notes

其中 Courses 和 Notes 可以作为 later version 功能，但不属于 Study Planet MVP 的独立主模块。

---

# 4. 产品结构

## 4.1 MVP 产品结构

Universe OS

```text
Universe Portal
└── Study Planet
    └── Study Workspace
        ├── Study Home
        ├── Goal
        ├── Learning Plan
        ├── Study Record
        ├── File Upload
        ├── AI Summary
        ├── Knowledge
        ├── Wordbook
        ├── RAG Q&A
        ├── Tutor
        ├── Wrong Questions
        ├── Review
        └── Analytics
```

## 4.2 Future Planet 占位

Universe Portal 可以展示以下未来 Planet：

- Work Planet
- Novel Planet
- Life Planet
- Creator Planet

MVP 中这些 Planet 只允许展示名称、视觉占位、状态文案和“coming later”提示，不允许进入真实 Workspace。

---

# 5. 用户核心流程

## Flow 001: 进入 Study Planet

1. 用户打开 Universe OS。
2. Universe Portal 展示 Study Planet 和未来 Planet 占位。
3. 用户点击 Study Planet。
4. 系统加载 Study Workspace、Study Agent、Planet Memory 和 Study 模块。
5. 用户进入 Study Home。
6. Study Home 展示今日目标、下一步行动、AI Recommendation、最近学习和关键进度。

结果：用户不需要思考导航结构，立即知道今天最应该做什么。

## Flow 002: 创建学习目标并生成计划

1. 用户在 Goal 中选择目标类型：考试目标、知识学习或成长目标。
2. 用户输入目标名称、描述、可选截止日期、科目/主题、当前水平、每日可用时间。
3. 系统基于 Goal 创建或展示 Learning Plan。
4. 系统保存 Long Term Goal、Monthly Plan、Weekly Plan、Daily Task。
5. Study Home 自动显示今天的第一优先任务。

结果：长期目标被拆成可执行任务。

## Flow 003: 开始并结束学习

1. 用户从 Study Home 或 Learning Plan 点击 Start Learning。
2. 系统创建 Study Session。
3. 用户记录学习科目、主题、时长、笔记和感受。
4. 用户结束 Session。
5. 系统生成 Study Record，并更新 Memory、Analytics 和 Review 候选项。

结果：真实学习行为进入长期学习档案。

## Flow 004: 上传学习资料并生成 Knowledge

1. 用户上传 PDF、Markdown 或 TXT 学习资料。
2. File Processing 解析文本。
3. Knowledge Service 执行 chunk、embedding 和 metadata 保存。
4. AI Summary 生成结构化总结。
5. RAG Q&A 可以基于资料回答问题。

结果：资料不只是存档，而是进入可检索、可问答的 Knowledge。

## Flow 005: Tutor 问答

1. 用户在 Tutor 或 RAG Q&A 输入问题。
2. 系统识别当前 Goal、Study Memory、相关 Knowledge 和最近 Wrong Questions。
3. AI Core 检索相关 chunks。
4. Tutor 给出解释、来源引用、相关概念和下一步建议。
5. 系统保存 Learning Event。

结果：AI 回答必须结合用户资料和学习历史，不能只是通用聊天。

## Flow 006: Wrong Questions 和 Review

1. 用户手动保存错题，或从 Tutor 回答中保存为 Wrong Question。
2. 系统记录题目、科目、知识点、错误类型、正确答案和 AI Analysis。
3. Review 按 1 天、3 天、7 天、30 天生成复习项。
4. 用户完成 Review 后更新 Master Status。
5. Analytics 更新薄弱点和复习效果。

结果：错题进入复习闭环。

---

# 6. Study Planet MVP 功能需求

## Module 01: Study Home

目标：进入 Study Planet 后，用户能立即知道当前状态和下一步行动。

必须展示：

- 当前 Goal。
- 今日最重要 Daily Task。
- Start Learning 入口。
- 今日学习时长、本周学习时长、连续学习天数。
- 最近 Study Record、Wrong Questions、Review 项。
- AI Recommendation。

状态要求：

- Empty State：没有 Goal 时，引导创建第一个 Goal。
- Loading State：加载 Memory、Plan、Analytics 时显示温和的空间感 loading，不显示后台骨架屏堆叠。
- Success State：完成今日任务后显示完成反馈和下一步建议。
- Failure State：计划或 AI Recommendation 加载失败时，保留 Study Home 基础内容并提供重试。

验收标准：

- Given 用户没有 Goal，When 进入 Study Home，Then 页面显示创建 Goal 的主行动入口。
- Given 用户已有今日 Daily Task，When 进入 Study Home，Then 首屏显示任务名称、科目、预计时长和 Start Learning。
- Given 用户完成一次 Study Session，When 返回 Study Home，Then 今日时长和最近学习记录被更新。
- Given AI Recommendation 生成失败，When Study Home 渲染，Then 页面仍可显示 Goal、Task 和 Record。

## Module 02: Goal

目标：管理 Study Planet 的长期学习目标。

MVP 字段：

- goal_type：exam / learning / growth
- goal_name
- description
- exam_name：仅考试目标需要
- deadline：可为空
- subjects
- current_level
- daily_available_minutes
- priority
- status

验收标准：

- Given 用户填写 Goal 表单，When 点击保存，Then 系统创建 Goal 并返回 Goal 详情。
- Given 用户选择知识学习或成长目标，When deadline 为空，Then 系统允许保存。
- Given deadline 早于今天，When 用户保存，Then 系统阻止保存并显示明确错误。
- Given 用户已有 active Goal，When 进入 Study Home，Then Goal 被作为 Study Planet 当前上下文。

## Module 03: Learning Plan

目标：将 Goal 拆成月、周、日任务。

必须支持：

- 基于 Goal 生成计划。
- 查看 Monthly Plan、Weekly Plan、Daily Task。
- 手动调整 Daily Task 的日期、时长和状态。
- 将今日任务同步到 Study Home。

AI 计划输入：

- Goal。
- Deadline。
- Subjects。
- Current Level。
- Daily Available Minutes。
- Existing Study Records。

AI 计划输出：

- Monthly milestones。
- Weekly focus。
- Daily tasks。
- Risk notes。

验收标准：

- Given 用户创建 Goal，When 点击 Generate Plan，Then 系统生成至少一个 Monthly Plan、一个 Weekly Plan 和未来 7 天 Daily Task。
- Given 用户调整 Daily Task 日期，When 保存，Then Study Home 的今日任务同步更新。
- Given AI 计划生成失败，When 用户查看 Learning Plan，Then 系统保留 Goal 并允许重新生成。

## Module 04: Study Record

目标：记录真实学习行为。

MVP 字段：

- subject
- topic
- duration_minutes
- start_time
- end_time
- linked_task_id
- notes
- feeling

验收标准：

- Given 用户点击 Start Learning，When Session 开始，Then 系统创建进行中的 Study Session。
- Given 用户结束 Session，When 保存，Then 系统生成 Study Record 并更新任务完成状态。
- Given duration_minutes 小于 1，When 保存，Then 系统提示时长无效。

## Module 05: File Upload

目标：让学习资料进入 Knowledge。

MVP 必须支持：

- PDF。
- Markdown。
- TXT。
- 文件 metadata：file_name、file_type、subject、topic、upload_time、processing_status。

Later version：

- Word。
- 图片 OCR。
- 视频字幕。
- 音频转写。

验收标准：

- Given 用户上传 PDF，When 文件解析成功，Then processing_status 变为 processed，并生成 chunks。
- Given 文件格式不支持，When 用户上传，Then 系统显示支持格式说明。
- Given 文件解析失败，When 用户查看文件状态，Then 系统显示 failed 和失败原因。

## Module 06: AI Summary

目标：自动总结资料或学习记录。

输入：

- processed file chunks。
- Study Record notes。
- selected subject/topic。

输出 Markdown：

- 标题。
- 核心概念。
- 重点。
- 易错点。
- 例题或示例。
- 复习建议。
- 来源引用。

验收标准：

- Given 文件已 processed，When 用户点击 Generate Summary，Then 系统生成结构化 Markdown Summary。
- Given Summary 引用了资料内容，When 用户查看 Summary，Then 每段关键结论包含来源文件或 chunk 引用。
- Given Summary 生成失败，When 用户重试，Then 系统不重复创建空 Summary。

## Module 07: Knowledge

目标：建立个人学习 Knowledge，而不是传统文件管理器。

MVP 内容：

- Document。
- Chunk。
- Concept。
- Subject。
- Topic。
- Wrong Question。
- Relationship。

必须支持：

- 按 subject/topic 浏览资料。
- 查看文件处理状态。
- 查看与概念相关的 Summary、Wrong Questions 和 Review。

验收标准：

- Given 文件处理完成，When 用户进入 Knowledge，Then 可以按 subject/topic 找到该文件。
- Given 某概念存在关联错题，When 用户查看概念，Then 页面展示相关 Wrong Questions。
- Given Knowledge 为空，When 用户进入页面，Then 显示上传资料的主行动入口。

## Module 08: RAG Q&A

目标：基于用户 Knowledge 回答问题。

必须能力：

- 检索相关 chunks。
- 回答问题。
- 展示来源引用。
- 推荐相关概念。
- 保存问答为 Learning Event。

验收标准：

- Given Knowledge 中存在相关资料，When 用户提问，Then 回答包含至少一个来源引用。
- Given 检索不到相关资料，When 用户提问，Then AI 明确说明当前 Knowledge 不足，并给出可上传或可补充的资料建议。
- Given 用户点击保存，When 问答被保存，Then Learning Event 进入 Memory。

## Module 08.5: Wordbook

目标：让用户把学习中遇到的词汇沉淀成可持续补充的个人单词本，而不是临时的文件或表格。

必须支持：

- 先按语言浏览，再通过标签缩小单词列表。
- 手动添加单词、释义、音标和标签。
- 通过 TXT 或 CSV 批量导入单词；同一 Goal scope 内重复单词必须提示并跳过。
- 在单词详情下钻维护词组、例句与个人笔记。
- 默认关联当前 Study Goal，同时允许独立单词本。

验收标准：

- Given 用户新增单词，When 保存，Then Wordbook 列表出现该词并可编辑详情。
- Given 用户上传 TXT/CSV，When 同一 scope 存在重复单词，Then 只导入新词并反馈跳过数量。
- Given 用户在详情添加标签、词组、句子和笔记，When 再次打开，Then 内容保持可读且持久化。

## Module 09: Tutor

目标：成为长期学习老师，而不是普通聊天窗口。

Tutor 必须结合：

- 当前 Goal。
- Planet Memory。
- 最近 Study Records。
- Wrong Questions。
- Knowledge 检索结果。

能力：

- 解释知识。
- 举例。
- 出题。
- 检查理解。
- 推荐下一步学习或 Review。

验收标准：

- Given 用户询问某知识点，When Tutor 回答，Then 回答包含解释、例子和下一步建议。
- Given 用户有相关 Wrong Questions，When Tutor 回答，Then 优先提醒相关错误类型。
- Given 用户要求出题，When Tutor 生成题目，Then 题目与当前 subject/topic 相关。

## Module 10: Wrong Questions

目标：管理错题并连接 Review 和 Knowledge。

MVP 字段：

- question
- subject
- topic
- error_type
- correct_answer
- user_answer
- ai_analysis
- source
- review_date
- master_status

验收标准：

- Given 用户保存错题，When 保存成功，Then 错题进入 Wrong Questions 列表并生成首次 Review 日期。
- Given 用户编辑 master_status，When 保存，Then Review 队列同步更新。
- Given question 为空，When 保存，Then 系统阻止并提示必填。

## Module 11: Review

目标：根据遗忘规律提醒复习。

MVP 复习节奏：

- 第 1 次：1 天后。
- 第 2 次：3 天后。
- 第 3 次：7 天后。
- 第 4 次：30 天后。

Review 来源：

- Wrong Questions。
- AI Summary。
- 用户标记的重要 Concept。

验收标准：

- Given 新 Wrong Question 被创建，When 系统生成 Review，Then review_date 默认为 1 天后。
- Given 用户完成一次 Review，When 标记结果为 mastered，Then 下一次 Review 日期按规则生成。
- Given 今天存在 Review 项，When 用户进入 Study Home，Then 今日 Review 出现在下一步行动或次级行动中。

## Module 12: Analytics

目标：分析学习效果，给出下一步行动建议。

MVP 指标：

- 今日学习时长。
- 本周学习时长。
- 连续学习天数。
- Daily Task 完成率。
- Subject 时间分布。
- Wrong Questions 数量和错误类型分布。
- Review 完成率。
- AI Recommendation。

验收标准：

- Given 用户完成 Study Record，When 进入 Analytics，Then 学习时长趋势包含该记录。
- Given 用户有 Wrong Questions，When 查看 Analytics，Then 可以看到错误类型分布。
- Given 数据不足，When 进入 Analytics，Then 页面显示空状态和建议行动，而不是空图表。

---

# 7. AI Agent 需求

Study Agent 是 Study Planet 的主 Agent，角色是学习教练。

Study Agent 包含以下能力：

- Planner：生成和调整 Learning Plan。
- Tutor：解释知识、举例、出题、检查理解。
- Reviewer：生成 Review 队列和复习提醒。
- Analyst：分析 Study Records、Wrong Questions 和 Review 结果。
- Coach：生成个性化 AI Recommendation。

Agent 输出要求：

- 必须使用当前 Study Planet 上下文。
- 必须优先使用用户 Knowledge 和 Memory。
- 涉及资料内容时必须提供来源引用。
- 不能虚构用户没有上传或记录过的事实。

---

# 8. 非功能需求

## 8.1 性能

- Universe Portal 首次可交互时间目标小于 2 秒。
- Study Home 首屏基础信息加载目标小于 2 秒。
- AI Summary、RAG Q&A、Learning Plan 生成允许异步状态，不阻塞页面基础操作。

## 8.2 数据安全

- 用户数据必须按 user_id 隔离。
- Planet 数据必须按 planet_id 或 planet_type 隔离。
- 文件、chunks、Memory、Study Records 不允许跨用户读取。

## 8.3 可扩展

- 新 Planet 必须通过 Planet Engine 注册。
- Future Planet 不应要求重写 Universe Core、AI Core、Memory 或 Knowledge。

---

# 9. MVP 版本范围

## 必须完成

Universe Portal：

- 展示 Study Planet。
- 展示 Work/Novel/Life/Creator Planet 的 future placeholders。
- 点击 Study Planet 进入 Study Workspace。

Study Planet：

- Study Home。
- Goal。
- Learning Plan。
- Study Record。
- File Upload。
- AI Summary。
- Knowledge。
- Wordbook。
- RAG Q&A。
- Tutor。
- Wrong Questions。
- Review。
- Analytics。

## 不包含

- Work Planet、Novel Planet、Life Planet、Creator Planet 的真实 Workspace。
- 多用户协作。
- 社交、商城、课程市场。
- 教师或机构后台。
- 原生移动端。

---

# 10. MVP 总体验收标准

MVP 完成后，用户必须能够：

1. 进入 Universe Portal，并看到 Study Planet 是唯一可进入 Planet。
2. 点击 Study Planet 进入 Study Workspace。
3. 创建 MEM 学习 Goal。
4. 基于 Goal 生成 Learning Plan。
5. 从 Study Home 开始一次 Study Session。
6. 保存 Study Record。
7. 上传 PDF、Markdown 或 TXT 学习资料。
8. 生成 AI Summary。
9. 基于 Knowledge 进行 RAG Q&A，并看到来源引用。
10. 手动添加或批量导入 Wordbook 单词，并保存词组、例句和笔记。
11. 保存和管理 Wrong Questions。
12. 完成 Review 并更新掌握状态。
13. 查看 Analytics，并获得 AI Recommendation。

---

# 11. 关键产品风险

- RAG 引用质量决定用户信任度，必须优先保证来源引用可追溯。
- AI Recommendation 不能泛泛而谈，必须来自 Goal、Plan、Record、Wrong Questions、Review 或 Knowledge。
- Study Home 不能演变成传统数据 Dashboard，首屏必须围绕“下一步行动”组织。
- Future Planet 只能作为 Portal 氛围和架构扩展的信号，不能扩大 MVP 范围。

---

# End
