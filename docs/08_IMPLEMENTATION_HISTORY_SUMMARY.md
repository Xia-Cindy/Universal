# Universe OS 阶段实施总览

版本：0.2
文档类型：实施历史总结  
状态：Historical Record with 2026-08 Current Baseline

> 本文前半部分保留各阶段当时的实施事实，不能把其中的旧运行命令当作当前操作说明。
> 当前唯一正常入口为 `http://127.0.0.1:5180/`；运行说明以 README、
> `docs/10_DELIVERY_ROADMAP_2026-08-09.md` 和
> `docs/11_OPERATIONS_AND_RECOVERY.md` 为准。

---

# 1. 总体目标

Universe OS 的当前实现目标是构建一个以 Planet 为组织方式的个人 AI 操作系统。

当前产品重点是 Study Planet，围绕一个用户的学习目标、计划、任务、学习记录、知识资料、Memory 和 AI 分析形成个人学习工作空间。

核心架构原则在所有阶段保持不变：

- 只有一个共享 AI Core。
- Study Planet 负责学习业务流程。
- Memory、Knowledge、Retrieval 是共享系统服务。
- Tutor 和 Analyst 是 Study Agent 的能力，不是独立 AI 系统。
- 不新增未批准的 Planet。
- 不做自动规划、人格推断、隐藏决策。

---

# 2. 仓库与文档准备

## 已完成操作

- 初始化 Git 仓库。
- 对齐仓库结构：
  - `AGENTS.md`
  - `docs/`
  - `backend/`
  - `frontend/`
  - `database/`
  - `scripts/`
- 将最终 Markdown 产品文档移动到 `docs/`。
- 建立文档作为单一事实源的规则。
- 创建并持续维护：
  - `README.md`
  - `TODO.md`
  - `CHANGELOG.md`
  - `docs/04_TECH_ARCHITECTURE.md`

## 对应提交

- `chore: align repository structure and documentation`

---

# 3. Milestone 1 Foundation

## 目标

搭建 Universe OS / Study Planet 的基础工程骨架，不实现完整业务闭环。

## 已完成操作

- 创建后端基础结构。
- 增加 API contract 边界。
- 增加 Planet registry。
- 将 Study Planet 标记为当前可用 Planet。
- 将 Work / Life / Novel / Creator 等 Planet 保持为未来占位。
- 建立数据库基础迁移和 seed。
- 建立 Memory scope 的基础边界。
- 创建 Universe Portal 前端壳。
- 创建 Study Workspace 前端壳。

## 未做

- 未实现完整学习流程。
- 未实现 AI Core。
- 未实现 RAG、Knowledge、Memory 智能能力。

## 对应提交

- `feat: implement milestone 1 foundation`

---

# 4. Milestone 2 Study Learning Workflow

## 目标

实现 Study Planet 的基础学习闭环。

## 已完成操作

- 增加 Study Goal 管理。
- 增加 Learning Plan、Daily Task 服务和 API。
- 增加 Study Session 开始和结束记录。
- 增加 Study Home 进度聚合。
- 增加前端 Home / Plan 基础工作流。
- 增加数据库迁移：
  - `002_study_learning_workflow.sql`
- 增加测试覆盖：
  - Goal 创建
  - 当前 Goal 获取
  - Plan 创建
  - Task 更新
  - Task 完成
  - Session 开始 / 完成
  - Study Home 进度计算

## 关键边界

- Knowledge、Tutor、Review、Analytics 保持占位。
- 不实现 AI Core、RAG、Embedding、Knowledge Graph。

## 对应提交

- `feat(study): implement learning workflow foundation`

---

# 5. Milestone 3 AI Core + Study Tutor Foundation

## 目标

建立共享 AI Core，并让 Study Tutor 作为 AI Core 消费者工作。

## 已完成操作

- 增加 AI Core service entry point。
- 增加 LLM Gateway interface。
- 增加 deterministic provider，保证本地和测试可重复。
- 增加 Prompt Manager。
- 增加 Context Manager。
- 增加 Agent Manager。
- 增加 Study Tutor service。
- 增加 Tutor API：
  - `POST /api/study/tutor/ask`
  - `GET /api/study/tutor/history`
- 增加 Tutor 前端页面。
- 将 Tutor 交互记录为 Learning Event。

## 关键边界

- Tutor 不作为独立 AI 系统。
- AI Core 不接入 RAG、Embedding、文档检索、来源引用。
- Tutor context 只使用当时允许的 Study workflow 数据。

## 对应提交

- `feat(ai): implement ai core and study tutor foundation`

---

# 6. Milestone 3.5 AI Core Generalization

## 目标

将 AI Core 从 Study Tutor 的硬编码路径重构为可扩展的 Agent / capability 系统。

## 已完成操作

- 引入 `AgentDefinition`：
  - `agent_id`
  - `capabilities`
  - `prompt_key`
  - `context_builder`
  - `allowed_tools`
- Agent Manager 改为解析注册定义。
- Context Manager 改为 Context Provider 架构。
- Study-specific context 移入 Study provider。
- Prompt Manager 改为使用 prompt key。
- LLM Gateway 保持 provider-only 边界。
- 增加 ToolRouter / Tool / Retriever interface 边界。

## 关键边界

- AI Core 不直接依赖 Study model、repository、entity。
- 没有实现 RAG。
- 没有实现 Tool execution 的业务能力。
- Dummy future agent 可以注册而不改核心分支。

## 对应提交

- `refactor(ai): generalize ai core architecture`

---

# 7. Milestone 4.1 Knowledge Foundation

## 目标

建立共享 Knowledge System 基础，支持文档注册、基础文本处理和 chunk 存储。

## 已完成操作

- 增加 Knowledge domain model：
  - Document
  - Document Chunk
  - Concept
- 增加 File service foundation。
- 支持 txt 和 markdown 文本处理。
- PDF 可保存 metadata，但不解析正文。
- 增加 Knowledge API：
  - document create / upload
  - processing
  - listing
  - detail
- 用真实 Knowledge 页面替换占位 UI。
- 增加数据库迁移：
  - `004_knowledge_foundation.sql`

## 关键边界

- Knowledge 是共享系统服务。
- Study Planet 只消费 Knowledge API。
- 不实现 AI summary。
- 不实现 Embedding、Vector、RAG、Tutor integration。

## 对应提交

- `feat(knowledge): implement knowledge foundation`

---

# 8. Milestone 4.2 Retrieval Foundation

## 目标

建立 Retrieval 基础设施接口和 embedding 准备层，但不接入 Tutor。

## 已完成操作

- 增加 EmbeddingProvider abstraction。
- 增加 deterministic embedding provider。
- 增加 VectorStore abstraction。
- 增加 in-memory test vector store。
- 增加 chunk embedding metadata / status 记录。
- 增加 RetrievalService。
- 增加 retrieval API：
  - embedding preparation
  - embedding status
  - chunk-only search
- 增加数据库迁移：
  - `005_retrieval_foundation.sql`

## 关键边界

- 不使用真实 vector database。
- 不使用 pgvector。
- 不增加 vector columns 或 production vector index。
- Retrieval 返回 chunk、metadata、score、identifier，不生成答案。
- 不接入 Tutor，不改变 AI Core 行为。

## 对应提交

- `feat(retrieval): implement retrieval foundation`

---

# 9. Milestone 4.3 Tutor Retrieval Integration

## 目标

通过 AI Core ToolRouter 将 Retrieval 接入 Study Tutor，形成 grounded Tutor 基础。

## 已完成操作

- 增加 AI Core ToolRouter execution flow。
- 增加 RetrieverTool adapter。
- Study Tutor 通过 AI Core ToolRouter 调用 Retrieval。
- 将检索到的 Knowledge chunks 注入 Tutor context。
- 在 Learning Event 中记录 retrieval metadata。
- Tutor UI 展示 grounding chunks。

## 关键边界

- 禁止 Tutor 直接调用 RetrievalService。
- RetrieverTool 不生成答案、不改 prompt、不调用 LLM。
- 没有实现 Knowledge Graph。
- 没有实现自动摘要。
- 没有新增 Agent。

## 对应提交

- `feat(rag): integrate retrieval with tutor through ai core`

---

# 10. Milestone 5 Memory Intelligence Foundation

## 目标

建立共享 Memory System 基础。

## 已完成操作

- 增加 Memory Manager。
- 增加 Memory repository / service boundary。
- 保持 canonical scope：
  - `global`
  - `planet`
  - `session`
- Memory entry 保持 user-owned。
- 增加 lifecycle：
  - `active`
  - `archived`
  - `expired`
- 增加 scoped retrieval。
- retrieval 时更新 access timestamp。
- 增加 active memory context preparation。
- 增加 Memory API：
  - create
  - list
  - update
  - archive
  - context
- Tutor 通过 AI Core payload 接收 prepared memory context。

## 关键边界

- Planet 不直接拥有独立 Memory storage。
- AI Core 不直接访问 Memory DB。
- Tutor 不直接查 Memory repository。
- 不做 autonomous extraction。
- 不做人格推断或心理画像。

## 对应提交

- `feat(memory): implement memory intelligence foundation`

---

# 11. Milestone 6 Study Intelligence Foundation

## 目标

基于已有 Study workflow、Knowledge、Retrieval、Memory，建立 Study Analytics / Analyst 能力。

## 已完成操作

- 将 Study Analyst 作为 Study Agent capability 注册。
- 增加 Analytics service。
- 增加 progress metrics：
  - task completion
  - study minutes
  - finished sessions
  - learning events
  - subject progress
- 增加 structured Study report。
- 增加 Analytics API。
- 用 Study Intelligence 页面替换 Analytics 占位。
- Analyst 可使用：
  - Study workflow data
  - prepared Memory context
  - optional Knowledge retrieval context

## 关键边界

- Analytics 是用户可见模块。
- Analyst 是内部 AI capability。
- 不创建 analytics persistence table。
- 不自动修改计划。
- 不做 autonomous decision。
- 不做 personality inference。

## 对应提交

- `feat(study): implement study intelligence foundation`

---

# 12. Frontend Vite / TypeScript Foundation Fix

## 目标

修复前端 Vue / Vite TypeScript 项目配置不完整导致的 build 失败。

## 已完成操作

- 检查 `frontend/package.json`。
- 补齐 Vite / Vue TypeScript 配置。
- 增加或修正：
  - `tsconfig.json`
  - `tsconfig.app.json`
  - `tsconfig.node.json`
  - `vite.config.ts`
  - `env.d.ts`
- 确认 `vue-tsc --noEmit` 可运行。
- 确认 `npm run build` 成功。
- 确认 `.gitignore` 覆盖 node_modules / dist。

## 对应提交

- `chore(frontend): complete vite typescript configuration`

---

# 13. Milestone 7 Study Product Loop

## 目标

将 Study Planet 从能力集合推进成可实际体验的学习闭环。

## 已完成操作

- 增加 Study onboarding。
- 新用户无 Goal 时进入创建目标流程。
- 使用现有 `study_goals` 表创建 Goal。
- 产品化手动 Plan workflow。
- Study Home 改为日常控制中心。
- 增加 Study Session execution wrapper。
- 支持从 Task 启动 Session。
- Session 结束时保存：
  - start time
  - end time
  - duration minutes
  - notes
  - feeling
- 通过 Memory Service 写入事实型 Memory。
- 在 Study Home 展示 existing Analytics / Analyst insight。
- 增加前端：
  - Onboarding
  - Session
  - Home product loop

## 关键边界

- 不新增 AI Core 能力。
- 不新增 Agent。
- 不新增 Planet。
- 不实现自动规划。
- 不实现 Knowledge Graph。

## 对应提交

- `feat(study): implement product learning loop`

---

# 14. 本地浏览器运行链路

## 目标

让 Universe OS 可以在本地浏览器完整体验。

## 已完成操作

- 配置 Vite dev server 代理 `/api` 到 FastAPI backend。
- 当时 README 增加本地启动说明：
  - backend: `uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`
  - frontend: `npm run dev -- --host 127.0.0.1 --port 5173`（历史入口，现已退役）
- 确认浏览器可访问：
  - Universe Portal
  - Study onboarding
  - Plan
  - Session
  - Knowledge
  - Tutor
  - Analytics

## 对应提交

- `chore(dev): enable local browser run`

---

# 15. Study Workspace Experience Update

## 目标

修复 Study Planet 主入口、文件上传、Goal 过度绑定考试等体验问题。

## 已完成操作

- 增加 Universe Home 返回入口。
- Study Workspace 显示当前 Planet 和用户位置。
- 扩展 Study Goal：
  - `goal_type`
  - nullable `deadline`
  - `description`
  - optional `exam_name`
- 支持目标类型：
  - exam
  - learning
  - reading
  - growth
- 重构 onboarding：
  - 先选目标类型
  - 再填目标名称、描述、可选截止时间
- Knowledge upload 改成真实文件选择。
- 支持：
  - txt
  - markdown
  - PDF metadata
- 增加 Home response aliases：
  - `progress`
  - `knowledgeOverview`
  - `analyticsInsight`
- 增加数据库迁移：
  - `007_study_goal_model_expansion.sql`

## 关键边界

- 不修改 AI Core。
- 不新增 Planet。
- 不引入 RAG。
- 不引入 Knowledge Graph。

## 对应提交

- `feat(study): improve goal model and workspace experience`

---

# 16. Milestone 8 RAGFlow Migration Planning

## 目标

规划将自建 Knowledge processing pipeline 迁移到 RAGFlow，作为架构计划，不实施代码。

## 已完成操作

- 新增文档：
  - `docs/05_RAGFLOW_MIGRATION_PLAN.md`
- 分析当前 Knowledge / Retrieval / AI Core / Tutor 边界。
- 设计未来 KnowledgeProvider interface：
  - `upload_document()`
  - `get_document_status()`
  - `delete_document()`
  - `search()`
  - `get_document_info()`
- 规划 provider adapter：
  - `providers/base.py`
  - `providers/ragflow.py`
- 规划 database strategy：
  - `documents` 保留业务 metadata 和 provider reference。
  - 不立即删除旧表。
- 规划迁移里程碑：
  - 8.1 RAGFlow Provider Adapter
  - 8.2 Knowledge Service Migration
  - 8.3 Retrieval Migration
  - 8.4 Tutor Grounded Knowledge Validation

## 关键边界

- 本阶段没有改生产代码。
- 没有创建 migration。
- 没有改 frontend。
- 没有实现 RAGFlow integration。
- RAGFlow 被定义为 infrastructure，不进入 Study Planet 或 AI Core。

## 对应提交

- `docs: add ragflow migration architecture plan`

---

# 17. Milestone 7.5 Study Domain Model Refinement

## 目标

让 Study domain model 支持更真实的个人学习空间，而不是单目标、单计划模型。

## 已完成操作

- 规范迁移编号。
- 增加 `008_study_domain_refinement.sql`。
- 增加 `reading` goal type。
- 支持多个 Goals。
- 支持 Goal switching。
- 支持多个 Plans per Goal。
- 增加 plan type separation：
  - long-term
  - monthly
  - weekly
- Knowledge document 支持 optional `goal_id`。
- Knowledge 可独立存在，也可绑定 Goal。
- 增加兼容性测试：
  - multiple Goals
  - Goal switching
  - nullable deadline
  - multiple Plans
  - plan type separation
  - Knowledge with / without Goal
  - Tutor compatibility
  - Analytics compatibility

## 关键边界

- 不改 AI Core。
- 不改 Agent registration。
- 不集成 RAGFlow。
- 不实现 Knowledge Graph。
- 不做自动规划。

## 对应提交

- `feat(study): refine study domain model`

---

# 18. Milestone 7.6 Study Product Workspace UX

## 目标

让前端工作流匹配后端已具备的多 Goal、多 Plan、Goal switching 能力。

## 已完成操作

- 增加 Study Workspace aggregation API：
  - `GET /api/study/workspace`
- 返回：
  - `currentGoal`
  - `goals`
  - `plans`
  - `todayTasks`
  - `knowledgeSummary`
  - `analyticsSummary`
- 增加 Goals 页面：
  - list goals
  - create goal
  - switch goal
- Home 围绕 Current Goal 展示：
  - current Goal
  - plan hierarchy
  - today tasks
  - learning summary
  - Analytics-only insight
- Plan 页面改为 current-Goal plan tree。
- Knowledge 页面增加 Goal filter。
- 保持 existing APIs 不破坏。

## 关键边界

- 不改 AI Core。
- 不改 RAG。
- 不扩展 Memory。
- 不引入 Knowledge Graph。

## 对应提交

- `feat(study): refactor study product workspace UX`

---

# 19. Milestone 7.7 Product Architecture Review

## 目标

在继续开发前，分析 Study Planet 产品架构和后续方向。

## 已完成操作

- 新增文档：
  - `docs/07_7_STUDY_PRODUCT_ARCHITECTURE_REVIEW.md`
- 分析当前层级：
  - User
  - Planet
  - Goal
  - Plan
  - Task
  - Session
  - Knowledge
  - Memory
  - Intelligence
- 明确 Goal 是 Study Planet 内部 top-level workspace context。
- 建议 exam / reading / general learning 共用 Goal model。
- 建议 Knowledge 可以独立存在，也可以绑定 Goal。
- 建议 Plans 可以手动创建，未来可增加 AI assist，但不能自动修改。
- 分析 UI 信息层级和导航问题。
- 确认 AI boundary：
  - Study Workflow → AI Core → Study Capability → Structured Insight
  - Knowledge Service → Retrieval → AI Core ToolRouter
  - Memory Service → Context Preparation → AI Core

## 关键边界

- 本阶段只做分析。
- 不改代码。
- 不改数据库。
- 不改 frontend。
- 不改 tests。

---

# 20. Milestone 7.8.1 Study Workspace IA Refactor

## 目标

将 Study Planet 从功能集合页面重构为以 Current Goal 为中心的学习工作空间。

## 已完成操作

- Header 增加 Current Goal 展示和切换。
- 主导航保持：
  - Home
  - Plan
  - Knowledge
  - Tutor
  - Review
  - Analytics
- Goals 降级为管理入口。
- Home 重构为：
  - Current Goal
  - Today Mission
  - Primary Action
  - Recent Progress
  - AI Insight
- Plan 页面使用一个 `Create Plan Structure` 入口。
- Plan 展示 Goal → Long Term → Monthly → Weekly → Daily Tasks 的层级。
- Workspace API 增加 `planSummary`。
- 修复 Knowledge upload enablement。
- 增加 IA tests。

## 关键边界

- 不改 AI Core。
- 不改 Retrieval。
- 不改 Memory。
- 不改数据库 schema。
- 不集成 RAGFlow。
- 不做自动规划。

## 对应提交

- `feat(study): refine workspace information architecture`

---

# 21. Post-7.8.1 PRD Smoke-Test Fixes

## 当前状态

已实现并通过验证，但截至本文档创建时，这批改动仍处于当前工作区变更中，尚未形成 Git commit。

## 已完成操作

- 将 Home / Workspace 的下一步行动统一为后端返回的 `primaryAction`。
- Frontend Home 只展示后端 service 决策，不再复制判断逻辑。
- `GET /api/study/home` 同时返回：
  - `primaryNextAction`
  - `primaryAction`
- `GET /api/study/workspace` 返回：
  - `primaryAction`
- Plan 页面中 completed task 不再显示 Start Session。
- completed task 改为 View Progress / Review 方向的动作。
- PDF Knowledge upload 明确显示 metadata-only 状态。
- PDF parser 未启用时不展示可误解的 Process 行为。
- Tutor 空问题时禁用 Ask Tutor。
- Study header 减少 Current Goal 重复展示。
- Goals 页面分组为：
  - Current Goal
  - Other Goals
  - Create Goal
- Analytics 文案从工程指标改为用户可读语言。
- 右侧静态 AI Recommendation 改名为 Study Context。
- Review / Wrong Questions 标记为 Coming Later。

## 已验证

- `python3 -m unittest discover -s tests`
  - 99 tests passed
- `python3 -m compileall backend`
  - passed
- `npm run build`
  - passed
- `git diff --check`
  - passed
- 本地接口验证：
  - `/api/study/workspace`
  - `/api/study/home`

## 注意

本地后端仍使用 in-memory repository。服务重启后测试数据会丢失，这是当前阶段的已知限制。

---

# 22. Milestone 7.9 Study Plan Productization Refactor

## 当前状态

已收到 Implementation Specification，但尚未开始实现。

## 目标

将 Plan 页面从暴露内部数据对象的计划层级，重构为用户理解的 Learning Roadmap 体验。

## 计划方向

当前内部结构仍保持：

```text
Goal
→ Long Term Plan
→ Monthly Plan
→ Weekly Plan
→ Daily Task
```

前端产品语言将调整为：

```text
Goal
→ Learning Roadmap
→ Current Stage
→ Current Objectives
→ Weekly Focus
→ Today's Mission
```

## 预期改动

- 重构 `frontend/src/planets/study/plan/`。
- 推荐组件：
  - `RoadmapPage.vue`
  - `StageCard.vue`
  - `ObjectiveList.vue`
  - `WeeklyFocus.vue`
  - `TodayTaskList.vue`
  - `RoadmapProgress.vue`
  - `RoadmapWizard.vue`
  - `TaskEditor.vue`
- 可选新增后端聚合 API：
  - `GET /api/study/goals/{goal_id}/roadmap`
- 不改数据库 schema。
- 不改 AI Core。
- 不做 AI-generated planning。

---

# 23. 2026-08 空间交付增量

## 已完成操作

- 将正常本地入口收敛到 5180 的 React/Three.js 空间房间；旧 Vue 启动路径退役，但源码保留给迁移和契约测试。
- 用显示器、计划桌、书架、黑板和作品展墙承载模块入口，并提供可分享的空间路由和底部快捷导航。
- 将 Knowledge 文档与 Wordbook tag 映射为实体书；阅读器支持封面开启、无滚动双页、翻页、页码跳转和本地书签。
- 将划线笔记与知识卡片保持为原资料归属对象；黑板只读取这些对象，不创建平行数据存储。
- 为 Wordbook 增加英语正面/个人释义背面的记忆卡，以及可持久化的背过/记错状态。
- 明确 RAGFlow 处理中可展示已返回 chunks；截至本段空间交付时，真实 TXT、Markdown、PDF 的 `processed` 验收仍未完成，后续 F1 运行时验收见本文件的 2026-08-13 补充记录。

## 对应交付依据

- `3241ada`：交互式 Knowledge/Wordbook 书架与阅读器。
- `f41c815`、`1dd1079`：空间、黑板、卡片/笔记与书架整合。
- `f83c6c1`、`1d98abb`：5180 唯一入口收敛与 main 集成。

# 24. 当前系统能力总览

## 已具备能力

- Universe Portal。
- Study Workspace。
- 多类型 Goal：
  - exam
  - learning
  - reading
  - growth
- 多 Goal 支持。
- Goal switching。
- 多 Plan per Goal。
- Plan type separation。
- Daily Tasks。
- Study Session start / finish。
- Learning Events。
- Knowledge document upload / registration。
- txt / markdown processing。
- PDF metadata upload。
- RAGFlow provider adapter for Knowledge processing and retrieval。
- Project-local RAGFlow Docker Compose stack。
- Retrieval foundation。
- Tutor through AI Core。
- Tutor grounded retrieval through ToolRouter。
- Memory foundation。
- Analytics / Study Analyst。
- Study Home daily control center。
- Local browser run chain。

## 仍未完成能力

- PostgreSQL 持久化 adapter。
- Object / file storage。
- Production RAGFlow runtime validation / status polling / retry handling。
- Provider-backed Tutor citation formatting。
- Full Plan Builder editing。
- Wrong Questions。
- Review queue。
- Autonomous Memory extraction。
- Future Planets。

---

# 25. 当前技术边界

## 保持不变

- AI Core 是唯一共享 AI 系统。
- Study Tutor 和 Study Analyst 均通过 AI Core。
- Retrieval 通过 ToolRouter 进入 AI Core。
- Knowledge 是共享服务，不在 Study Planet 内部实现业务逻辑。
- Memory 是共享服务，不由 Planet 或 Tutor 直接访问 repository。
- Study Planet 只负责学习 workflow。

## 明确禁止

- 新增独立 AI 系统。
- Tutor 直接调用 RAGFlow 或 RetrievalService。
- AI Core 依赖 RAGFlow。
- Planet 绕过 shared service 直接访问底层基础设施。
- Frontend 直接调用 RAGFlow。
- 自动修改用户计划。
- 自动推断人格或心理画像。

---

# 26. Milestone 8.1 RAGFlow Knowledge Provider Adapter

## 状态

已完成 provider adapter 和 mocked integration tests。

## 已实现

- 新增 `KnowledgeProvider` protocol。
- 新增 `RAGFlowKnowledgeProvider` 与 `RAGFlowClient`。
- 新增 `docker/ragflow/` local runtime stack。
- 新增 `docs/06_RAGFLOW_INSTALLATION.md` 安装文档。
- 新增 migration `009_ragflow_provider_metadata.sql`，为 Knowledge documents 保存 provider metadata。
- `KnowledgeService` 在 `KNOWLEDGE_PROVIDER=ragflow` 时通过 RAGFlow 上传、解析和读取 chunks。
- `RetrievalService` 在 provider 模式下调用 RAGFlow retrieval API，并把结果归一化回 Universe document metadata。
- Study Knowledge UI 展示 provider 状态。
- Local provider 仍是默认路径，现有 txt / markdown 本地处理保持可用。

## 未改变

- AI Core 不依赖 RAGFlow。
- Tutor 不直接调用 RAGFlow。
- Frontend 不直接调用 RAGFlow。
- Study Planet 不拥有 provider lifecycle。
- RAGFlow 镜像下载和真实 API key runtime validation、状态轮询、重试队列和 citation formatting 仍是后续工作。

---

# 26. 当前仓库状态说明

截至本文档创建时：

- 最新已提交 commit：
  - `feat(study): refine workspace information architecture`
- 当前工作区包含 Post-7.8.1 PRD smoke-test fixes、Figma-style frontend rebuild、Goal/Plan editing fix，以及 Milestone 8.1 RAGFlow provider adapter work。
- RAGFlow 已完成 backend provider adapter、mocked tests、本地 Docker Compose runtime stack 与安装文档；真实 API key runtime validation、status polling、retry handling 和 Tutor citation formatting 仍待后续实施。

建议下一步：

1. 运行完整 backend/frontend 验证。
2. 提交当前已完成的 Study Workspace polish 与 RAGFlow provider adapter。
3. 再进入生产 RAGFlow runtime validation 或 Milestone 7.9 Plan Builder。

## 27.1 四阶段执行中的 RAGFlow Runtime 状态

本次执行已补齐 RAGFlow runtime contract：health check、异步 status refresh、Study Knowledge 前端轮询、失败 retry 和删除同步。完整测试及 frontend build 已通过。

这是首次 runtime 的历史失败记录：当时真实文档解析在 embedding provider 阶段因 `InvalidApiKey` 失败。该问题随后由部署配置修复；2026-08-13 的 F1 受控 TXT、Markdown 与新 PDF 均已达到 `processed`、非零 provider chunk、检索/Tutor 来源回链和 5180 阅读器验收。该结果不推定此前两份历史长 PDF 已完成或应被重试。

## 27.2 四阶段产品闭环

- Shared persistence 阶段补齐 SQLite migration runner、repository adapters、唯一 Study current context，并保持现有 service boundaries。
- RAGFlow runtime 阶段补齐 health/status polling/retry/delete contract；随后完成受控 TXT、Markdown、PDF 的有效 embedding runtime acceptance。历史长文档仍需按单文档状态单独判断。
- Citation/Evidence 阶段补齐 Tutor scope、统一 source shape、quote preview、Knowledge click-through 和保存 Learning Event。
- Review 阶段补齐 Wrong Question、1/3/7/30 review items、幂等完成和 Analytics summary；Review 不依赖 AI。
- Session execution finish 会在首次结束时同步关联 Task、Learning Event 和 Memory write point，重复 finish 不重复计数。

---

# 27. Shared Persistence Foundation

已完成本地共享持久化基础：

- 新增 shared SQLite persistence、schema migration runner 和 transaction boundary。
- 当时的生产 API 曾默认使用 `database/universe.sqlite3`；现已改为 PostgreSQL runtime，SQLite 仅保留为显式本地兼容 adapter。
- Study、Knowledge、Memory、Work repository 通过 adapter 共享同一个 persistence connection。
- 新增 `user_planet_context`，作为 Study `current_goal` 的唯一来源。
- Goal switch 不再依赖 Memory 中的 `active_goal_id`，也不会归档其他 active Goal。
- 新增 restart integration tests，覆盖 Goal、Plan、Task、Session、Document、Memory 的重启读取。

本阶段仍未完成：

- PostgreSQL adapter。
- Session finish 的统一 application transaction。
- RAGFlow runtime acceptance、status polling、retry、delete sync 和 Citation。
- Wrong Questions 与 Review 闭环。

---

# 28. Focus Reader 与目标关联复习卡

## 已完成

- Knowledge Reader 以资料为唯一归属：划线生成的笔记与知识卡片均绑定 `document_id`、用户和可选 `goal_id`，不新增独立 Notes 系统。
- 新增 `knowledge_annotations` 的 PostgreSQL / SQLite migration、repository、API contract 与重启持久化测试。
- 翻开的书页不再提供内层滚动；资料文字会拆分为纸页，阅读时根据可用纸面高度自动调整排版，保留翻页操作。
- 划线后可选择“添加到笔记”或“制成知识卡”，并可覆盖资料默认的关联学习目标。
- 知识卡片在正面随机遮住关键词，点击“翻到背面”显示答案；“背过了”仅在首次状态转换时写入一个 Goal-linked Learning Event。
- Wordbook 以英文正面、个人释义背面提供记忆卡，支持“背过了”和“记错了”；后者会增加 `mistakeCount` 并记录最近复习时间。
- Study Workspace 的当前目标进度新增 `progress.masteredItems`，统计关联目标的首次知识卡/笔记/单词背过事件，避免重复点击造成虚高。

## 未改变

- Knowledge 仍是共享服务；Study 只负责 Goal、Learning Event 和学习进度聚合。
- 未引入新的 AI Core、Agent、独立卡片库或自动判分逻辑。

---

# 29. 当前 Study Knowledge 空间实现

本节覆盖当前可交付交互，并替代此前空间原型中“词汇植物/实体词典架”的表述。

## 已实现

- 学习电脑仅通过显示器屏幕进入 Study Home / Goals / Tutor；原先包围书桌区域的白色热点框已移除。
- 墙面黑板直接进入 `/study/cards`，页面只展示现有 Knowledge 资料生成的知识卡片与学习笔记；卡片/笔记可以在画廊中展开，返回房间与底部快捷导航保持可用。
- 每份上传资料对应书架中的一本书。书架使用三本一页的参考构图，超过三本可切换书架页，并保留学科筛选、Goal 关联、编辑与删除操作。
- 书籍需先选中再点击封面进入双页阅读器。阅读器无书页内滚动，提供前后翻页、指定页跳转和浏览器本地书签；当 RAGFlow 仍在处理时，会读取已返回的 chunks 并标注持续解析状态，不重提解析任务。
- 划线生成的笔记和知识卡片持续绑定原资料；知识卡可隐藏关键词、翻面揭示并将首次“背过了”计入关联 Goal 的 `progress.masteredItems`。
- Wordbook 的 tag 展示为同样的实体词汇书。单词页面展示词典与个人字段；记忆卡保持英文正面、学习者释义背面，并记录“背过了”或“记错了”。

## 架构边界

- 空间层只消费 Study、Knowledge 与 Wordbook 的既有 API，不复制 Knowledge document、annotation 或 Wordbook persistence。
- Knowledge 卡片/笔记不是新的独立系统；其归属关系仍是 `document_id`、用户和可选 `goal_id`。
- 该功能未新增 AI Core、Agent、RAGFlow 调用入口或自动判分逻辑。
