# Universe OS
# 04_TECH_ARCHITECTURE.md

Version: 1.2

Document Type: Technical Architecture Specification

Product: Universe OS

Purpose: Define the technical architecture, service boundaries, data model, API direction and implementation principles.

Current runtime baseline: `room-portfolio/` on port 5180 is the only normal
user entry. It is a React/Three.js room client; its active Knowledge/Wordbook
bookshelf uses a DOM/CSS 3D reference scene injected into an iframe, rather
than a Three.js bookshelf. The Vue `frontend/` source is retained for
migration/contract tests and is not started by `startup.sh`.

---

# 1. Architecture Overview

Universe OS 是 AI Native Personal Operating System。

总体架构：

```text
Universe OS
└── Frontend Layer
    └── API Gateway / Backend API
        ├── Universe Core
        ├── Planet Engine
        ├── Study Planet Services
        ├── AI Core
        ├── Memory Service
        ├── Knowledge Service
        ├── File Processing Service
        └── Analytics Service
            └── Data Layer
```

当前运行时以 Study Planet 为核心，同时提供 Work 的业务工作区和 Novel 草稿服务；Life 与 Creator 仍为未来方向。不会为 Work 或 Novel 新建独立 AI Core。

---

# 2. Core Architecture Principles

## Principle 001: Planet Independent

每个 Planet 必须独立开发。

Planet 包含：

- UI identity。
- Workspace。
- Modules。
- Agent skills。
- Planet data model。
- Tools。

Planet 不能直接依赖另一个 Planet 的 UI 或业务数据。

## Principle 002: Shared AI Infrastructure

所有 Planet 共享：

- AI Core。
- Memory Service。
- Knowledge Service。
- File Service。
- User Service。
- Analytics foundation。

Study Planet 可以使用这些共享能力，但不能把 Study 专属逻辑写进 Universe Core。

## Principle 003: API First

Frontend 和 Backend 只能通过 API 通信。

禁止：

- Frontend 直接访问数据库。
- Frontend 直接读写 vector store。
- UI 组件内硬编码 AI prompt。
- 绕过 API 直接调用内部 service。

## Principle 004: MVP Boundary First

实现时必须先完成 Study Planet MVP 闭环。Work 与 Novel 的已交付受限能力必须复用
共享服务边界；Life 与 Creator 不得扩展为真实业务功能。

---

# 3. Canonical Module Mapping

| Product Module | Frontend Route | Backend Service | AI / Data Dependency |
| --- | --- | --- | --- |
| Universe Portal | / | universe | Planet Engine |
| Study Home | /study | study_dashboard | Goal, Plan, Record, Review, Analytics, Memory |
| Goal | /study/plan/goal | study_goal | Memory |
| Learning Plan | /study/plan | study_plan | Planner Agent, Goal, Records |
| Study Record | /study/session/:id | study_session | Memory, Analytics |
| File Upload | /study/knowledge/upload | file_service | File Processing |
| AI Summary | /study/knowledge/summary/:id | summary_service | AI Core, Knowledge |
| Knowledge | /study/knowledge | knowledge_service | Documents, Chunks, Concepts |
| RAG Q&A | /study/tutor | rag_service | Retriever, AI Core, Sources |
| Tutor | /study/tutor | tutor_service | Study Agent, Memory, Knowledge |
| Wrong Questions | /study/review/wrong-questions | wrong_question_service | Review, Knowledge |
| Review | /study/review | review_service | Wrong Questions, Concepts |
| Analytics | /study/analytics | analytics_service | Records, Tasks, Reviews |

---

# 4. Frontend Architecture

Current runtime technology:

- React + React Three Fiber + Three.js。
- Vite。
- Zustand for room interaction state。
- FastAPI-backed `/api` proxy。

The only user-facing local runtime is `room-portfolio/` on port 5180. The
existing `frontend/` Vue source remains for migration and contract-test
coverage, but `startup.sh` does not launch it as a product page.

## 4.1 Frontend Structure

```text
room-portfolio/
└── src/
    ├── Experience.jsx
    ├── RoomModel/
    ├── ModuleWorld.jsx
    ├── DeployedBooks.jsx
    ├── KnowledgeCardsGallery.jsx
    ├── SpatialModuleScene.jsx
    ├── spaces.js
    └── api.js
```

## 4.2 Routing Architecture

Current spatial routes:

```text
/                         Universe Portal
/study                    Study Home
/study/goals              Goals
/study/tutor              Tutor / RAG Q&A
/study/plan               Learning Plan
/study/review             Review
/study/analytics          Analytics
/study/knowledge          Knowledge bookshelf
/study/wordbook           Wordbook bookshelf
/study/cards              Knowledge cards and notes
/work                     Work Home
/work/tech-stack          Work Tech Stack
/work/knowledge           Work Knowledge
/work/projects            Work Projects
/work/resume              Work Resume
/novel                    Novel drafts
```

`/work` 提供已交付的受限 Work Workspace，`/novel` 提供持久化草稿空间；两者不得
创建独立 AI Core 或绕过 Shared Knowledge。`/life`、`/creator` 如需展示，仍只能是
coming-later 占位，不能进入空 Workspace。

## 4.3 Frontend Responsibilities

Frontend owns：

- Page layout。
- Interaction states。
- Form validation before submit。
- API calls。
- Loading / empty / success / failure states。
- Source citation display。
- Study Workspace visual identity。

Frontend does not own：

- AI prompt orchestration。
- Retrieval logic。
- Embedding generation。
- Memory writing rules。
- Analytics calculation truth。

---

# 5. Backend Architecture

Recommended technology:

- Python。
- FastAPI。
- PostgreSQL。
- pgvector for MVP vector storage。
- Redis。
- Celery or background worker。
- Local object storage for development, S3-compatible storage for production。

## 5.1 Backend Structure

```text
backend/
└── app/
    ├── core/
    ├── universe/
    ├── planet_engine/
    ├── planets/
    │   └── study/
    │       ├── dashboard/
    │       ├── goals/
    │       ├── plans/
    │       ├── sessions/
    │       ├── summaries/
    │       ├── tutor/
    │       ├── wrong_questions/
    │       ├── review/
    │       └── analytics/
    ├── ai/
    ├── memory/
    ├── knowledge/
    ├── files/
    ├── users/
    └── analytics/
```

---

# 6. Planet Engine

Purpose：管理 Planet lifecycle。

Responsibilities：

- Register Planet。
- Load Planet configuration。
- Validate Planet availability。
- Control Planet permission。
- Provide Portal metadata。

Planet configuration example：

```json
{
  "name": "study",
  "displayName": "Study Planet",
  "status": "active",
  "version": "1.0",
  "modules": [
    "dashboard",
    "goal",
    "plan",
    "study_record",
    "file_upload",
    "ai_summary",
    "knowledge",
    "rag_qa",
    "tutor",
    "wrong_questions",
    "review",
    "analytics"
  ]
}
```

Future Planet configuration example：

```json
{
  "name": "work",
  "displayName": "Work Planet",
  "status": "coming_later",
  "version": null,
  "modules": []
}
```

---

# 7. AI Core Architecture

AI Core 是 Universe OS 的共享智能层。

Responsibilities：

```text
Understand User
→ Build Context
→ Select Agent / Tool
→ Retrieve Knowledge
→ Generate Response
→ Return Sources
→ Update Memory
```

AI Core components：

```text
AI Core
├── LLM Gateway
├── Prompt Manager
├── Context Manager
├── Tool Router
├── Retriever
├── Memory Manager
└── Agent Manager
```

Rules：

- Prompt 必须由 backend 管理。
- AI response 涉及 Knowledge 时必须返回 source citations。
- Memory 更新必须通过 Memory Service。
- AI Core 不能直接写 Study 业务表，必须调用对应 service。

---

# 8. Agent Architecture

Agent 是专门执行任务的 AI worker。

结构：

```text
Agent
├── Role
├── Prompt
├── Tools
├── Memory Access
├── Knowledge Access
└── Workflow
```

Study Agent includes：

- Planner Agent。
- Tutor Agent。
- Review Agent。
- Analyst Agent。
- Coach Agent。

Example flow：

```text
User: 帮我安排这个月学习计划
→ AI Core
→ Planner Agent
→ Read Goal
→ Read Study Records
→ Read Planet Memory
→ Generate Plan
→ Save via Plan Service
→ Return plan summary
```

---

# 9. Memory Architecture

Memory 不是 chat history。Memory 存储用户长期上下文。

三层结构：

```text
Memory
├── Global Memory
├── Planet Memory
└── Session Memory
```

Global Memory：

- user preferences。
- long-term interests。
- language preference。

Planet Memory：

- active_goal_id。
- weak_subjects。
- preferred_study_time。
- learning habits。

Session Memory：

- current_session_id。
- subject。
- topic。
- recent questions。

Write rules：

- Study Record saved → update Planet Memory。
- Wrong Question created → update weak concepts。
- Review completed → update mastery signal。
- RAG Q&A saved → create Learning Event。

---

# 10. Knowledge Architecture

Knowledge system：

```text
Document
→ Chunk
→ Embedding
→ Vector Store
→ Concept / Metadata
→ Knowledge Relationship
→ Retrieval
```

Knowledge objects：

- Document。
- Chunk。
- Concept。
- Subject。
- Topic。
- Summary。
- Wrong Question。
- Review Item。

Knowledge must support：

- File-based retrieval。
- Subject/topic filtering。
- Source citation。
- Relationship with Wrong Questions and Review。

---

# 11. RAG Architecture

RAG pipeline：

```text
User Question
→ Build Study Context
→ Retrieve relevant chunks
→ Rank / filter sources
→ Generate answer with citations
→ Return related concepts
→ Save Learning Event if user chooses or policy requires
```

RAG response contract：

```json
{
  "answer": "string",
  "sources": [
    {
      "document_id": "string",
      "chunk_id": "string",
      "file_name": "string",
      "quote_preview": "string"
    }
  ],
  "related_concepts": ["string"],
  "suggested_next_action": "string"
}
```

If retrieval finds no reliable source, response must say Knowledge is insufficient and recommend uploading or selecting relevant material.

---

# 12. File Processing Architecture

MVP supported file types：

- PDF。
- Markdown。
- TXT。

Later version：

- Word。
- Images with OCR。
- Video subtitles。
- Audio transcription。

Processing flow：

```text
File Upload
→ Store original file
→ Extract text
→ Create Document record
→ Split into chunks
→ Generate embeddings
→ Store chunks in vector store
→ Extract metadata / concepts
→ Mark processed
```

Processing statuses：

- uploaded。
- parsing。
- chunking。
- embedding。
- processed。
- failed。

Failure must preserve original file record and error reason.

---

# 13. Analytics Architecture

Data sources：

- Study Records。
- Daily Tasks。
- Wrong Questions。
- Review Results。
- AI Interactions。
- Knowledge activity。

Processing：

```text
Raw Events
→ Analytics Service
→ Metrics
→ Weakness Signals
→ AI Recommendation
→ Study Home / Analytics display
```

MVP metrics：

- today_study_minutes。
- week_study_minutes。
- study_streak_days。
- task_completion_rate。
- subject_distribution。
- wrong_question_count。
- error_type_distribution。
- review_completion_rate。
- weak_concepts。

Analytics Service owns metric calculation. Frontend only renders results.

---

# 14. Data Architecture

## 14.1 PostgreSQL

Purpose：主业务数据库。

Tables / entities：

- users。
- planets。
- planet_memberships。
- study_goals。
- study_plans。
- study_tasks。
- study_sessions。
- study_records。
- documents。
- document_chunks。
- ai_summaries。
- concepts。
- knowledge_relationships。
- wrong_questions。
- review_items。
- learning_events。
- memory_entries。
- analytics_snapshots。

## 14.2 Vector Store

MVP recommendation：pgvector。

Stores：

- chunk embedding。
- document_id。
- chunk_id。
- subject。
- topic。
- metadata。

## 14.3 Redis

Used for：

- session cache。
- AI context cache。
- background job state。
- rate limiting if needed。

## 14.4 Object Storage

Development：local storage。

Production：S3-compatible storage。

Stores：

- original files。
- processed text artifacts if needed。

---

# 15. Core Data Models

## 15.1 Study Goal

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "goal_type": "exam | learning | growth",
  "goal_name": "成为 AI 工程师",
  "description": "长期能力建设目标",
  "exam_name": null,
  "deadline": null,
  "subjects": ["machine learning", "systems", "product engineering"],
  "current_level": "basic",
  "daily_available_minutes": 90,
  "priority": "high",
  "status": "active"
}
```

## 15.2 Daily Task

```json
{
  "id": "uuid",
  "goal_id": "uuid",
  "subject": "math",
  "topic": "permutation",
  "task_date": "2026-07-08",
  "estimated_minutes": 40,
  "status": "pending"
}
```

## 15.3 Study Record

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "task_id": "uuid",
  "subject": "math",
  "topic": "permutation",
  "duration_minutes": 45,
  "start_time": "2026-07-08T20:00:00+08:00",
  "end_time": "2026-07-08T20:45:00+08:00",
  "notes": "string",
  "feeling": "focused"
}
```

## 15.4 Document

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "file_name": "math.pdf",
  "file_type": "pdf",
  "subject": "math",
  "topic": "permutation",
  "processing_status": "processed",
  "error_message": null
}
```

## 15.5 Wrong Question

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "question": "string",
  "subject": "math",
  "topic": "permutation",
  "error_type": "method_mistake",
  "correct_answer": "string",
  "user_answer": "string",
  "ai_analysis": "string",
  "review_date": "2026-07-09",
  "master_status": "not_mastered"
}
```

---

# 16. API Direction

API names can change during implementation, but capability boundaries must remain.

Universe：

- `GET /api/planets`
- `GET /api/planets/{planet_name}`

Study Home：

- `GET /api/study/home`

Goal and Plan：

- `POST /api/study/goals`
- `GET /api/study/goals/active`
- `POST /api/study/plans/generate`
- `GET /api/study/plans/current`
- `PATCH /api/study/tasks/{task_id}`

Study Record：

- `POST /api/study/sessions`
- `PATCH /api/study/sessions/{session_id}/finish`
- `GET /api/study/records`

Knowledge and File：

- `POST /api/study/files`
- `GET /api/study/files/{file_id}`
- `POST /api/study/files/{file_id}/process`
- `GET /api/study/knowledge`

AI Summary：

- `POST /api/study/summaries`
- `GET /api/study/summaries/{summary_id}`

Tutor / RAG：

- `POST /api/study/tutor/ask`

Wrong Questions and Review：

- `POST /api/study/wrong-questions`
- `GET /api/study/wrong-questions`
- `PATCH /api/study/wrong-questions/{id}`
- `GET /api/study/review`
- `PATCH /api/study/review/{id}/complete`

Analytics：

- `GET /api/study/analytics`

---

# 17. Study Planet Technical Flows

## 17.1 Enter Study Planet

```text
Frontend click Study Planet
→ GET /api/planets/study
→ load route /study
→ GET /api/study/home
→ render Study Home
```

## 17.2 Generate Learning Plan

```text
Create Goal
→ POST /api/study/plans/generate
→ Planner Agent reads Goal + Memory + Records
→ Plan Service saves plan/tasks
→ Memory Service stores active goal signal
→ Study Home receives updated next action
```

## 17.3 Save Study Record

```text
Start Session
→ Finish Session
→ Save Study Record
→ Update task status
→ Update Memory
→ Update Analytics
→ Generate Review candidates if needed
```

## 17.4 Upload and Ask

```text
Upload File
→ File Processing
→ Knowledge chunks + embeddings
→ Generate Summary
→ User asks question
→ Retriever finds chunks
→ Tutor answers with citations
```

## 17.5 Wrong Question Review

```text
Create Wrong Question
→ Generate Review Item for +1 day
→ User completes Review
→ Update master_status
→ Schedule next Review
→ Update Analytics weak concepts
```

---

# 18. Security Architecture

Authentication：

- MVP can use email login or local user session depending on implementation context。
- OAuth can be later version。

Authorization：

```text
User
→ Planet Permission
→ Resource Ownership
```

Data protection：

- user_id required on all user-owned rows。
- API must validate resource ownership。
- File access must be signed or proxied through backend。
- User must be able to export and delete personal data in later version。

---

# 19. Deployment Architecture

Development：

```text
Mac
└── Docker Compose
    ├── frontend
    ├── backend
    ├── postgres + pgvector
    ├── redis
    ├── worker
    └── object storage
```

Production：

```text
Load Balancer
├── Frontend Container
├── Backend Container
├── Worker
├── PostgreSQL
├── Redis
├── Vector Store
└── Object Storage
```

---

# 20. MVP Technical Scope

Must implement：

Universe Core：

- Planet registry。
- Universe Portal API metadata。
- Study Planet active state。
- Future Planet placeholder state。

Study Planet：

- Study Home aggregation。
- Goal CRUD minimal。
- Learning Plan generation and task management。
- Study Session and Study Record。
- File Upload and processing statuses。
- AI Summary generation。
- Knowledge browsing。
- RAG Q&A with citations。
- Tutor response using context。
- Wrong Questions CRUD。
- Review queue。
- Analytics metrics。

May stub carefully：

- Future Planet routes as coming later。
- Advanced Knowledge Graph visualization。
- Complex notification system。
- OAuth。
- OCR / video / audio processing。

Must not stub：

- Source citations for RAG Q&A。
- User data isolation。
- Study Home primary next action。
- Wrong Question to Review scheduling。
- Basic Analytics metrics。

---

# 21. Testing Expectations

Backend tests：

- Goal validation。
- Plan generation service contract。
- Study Session start/finish。
- File processing status transitions。
- RAG response includes sources when chunks exist。
- Wrong Question creates Review item。
- Review completion schedules next date。
- Analytics metrics from records。
- User ownership checks。

Frontend tests：

- Study Home empty/loading/success/failure states。
- Plan flow with and without Goal。
- File Upload processing states。
- Tutor answer renders sources。
- Wrong Questions form validation。
- Review completion state。
- Analytics empty state。

Integration tests：

- Create Goal → Generate Plan → Start Session → Finish Record → Analytics updates。
- Upload File → Process → Generate Summary → Ask RAG question with citation。
- Create Wrong Question → Review due → Complete Review → Next review date。

---

# 22. Future Expansion

Future Planets：

- Work Planet。
- Novel Planet。
- Life Planet。
- Creator Planet。

Future Planet development must reuse：

- Planet Engine。
- AI Core。
- Memory Service。
- Knowledge Service。
- File Service。
- User Service。

No future Planet should require rewriting Study Planet or Universe Core.

---

# 23. Final Architecture Vision

```text
User
→ Universe Portal
→ Planet Engine
→ Study Planet
→ Study Workspace
→ AI Core
→ Memory + Knowledge
→ Data Layer
```

Universe OS 的架构目标是让每个 Planet 都像一个独立智能空间，同时共享稳定的 AI、Memory、Knowledge 和数据基础设施。

---

# 24. Implementation Instructions for Codex

## Files to Read First

Codex 在实现前必须先阅读：

1. `docs/01_PRD.md`
2. `docs/02_INFORMATION_ARCHITECTURE.md`
3. `docs/03_UI_DESIGN_SPEC.md`
4. `docs/04_TECH_ARCHITECTURE.md`

如果仓库中存在实际代码，还必须先查看：

- package / dependency files。
- frontend router。
- backend app entry。
- existing API structure。
- existing data models / migrations。
- existing AI / RAG / Memory utilities。

## Architecture Rules

- 保持 Universe Portal → Planet → Workspace → Module 层级。
- Study Planet 是当前产品主线；Work 与 Novel 仅可在已交付的受限路由内运行。
- Life 与 Creator 只能作为 Portal placeholders。
- Frontend 只能通过 API 访问 backend。
- AI prompt、RAG、Memory 写入和 embedding 逻辑必须在 backend / AI Core / service 层。
- Study 专属逻辑不能写进 Universe Core。
- RAG Q&A 必须返回 source citations。
- Study Home 必须以 primary next action 为首屏核心。

## Forbidden Changes

Codex 不得：

- 删除 Planet architecture。
- 删除 AI Core、Memory、Knowledge、RAG 概念。
- 把 Universe OS 改成普通 SaaS dashboard。
- 新增随机模块或扩大 MVP。
- 实现 Work/Novel/Life/Creator 的真实业务功能。
- 用 Statistics、Knowledge Base、AI Tutor 作为用户侧主命名。
- 用大表格或通用聊天页替代核心体验。
- 绕过 service/API 直接访问数据库或 vector store。

## MVP Implementation Order

推荐顺序：

1. Project baseline：确认技术栈、启动方式、路由和 API 结构。
2. Universe Portal：Planet registry、Study active、Future placeholders。
3. Study Workspace shell：Header、Navigation、Contextual AI Panel、routing。
4. Goal：创建 active Goal。
5. Learning Plan：生成和展示 Daily Tasks。
6. Study Home：聚合 Goal、Daily Task、Record、Review、Analytics。
7. Study Session / Study Record：开始、结束、保存学习记录。
8. File Upload：上传、processing_status、Document records。
9. Knowledge：chunks、metadata、基础浏览。
10. AI Summary：基于 processed file 生成 summary。
11. RAG Q&A / Tutor：检索、回答、sources、Learning Event。
12. Wrong Questions：CRUD 和 AI Analysis 字段。
13. Review：复习队列和下一次复习日期。
14. Analytics：MVP 指标和 AI Recommendation。
15. End-to-end polish：empty/loading/success/failure states and UX consistency。

## Testing Expectations

每完成一个 MVP 模块必须至少验证：

- 正常路径。
- Empty state。
- Loading state where relevant。
- Failure state。
- User data isolation。
- API contract。

AI / RAG 相关模块必须验证：

- 有 Knowledge 时返回 sources。
- 无 Knowledge 时不虚构来源。
- 失败时不创建空数据。

## Documentation Update Expectations

实现过程中如果出现架构或范围变化，Codex 必须同步更新文档：

- PRD 范围变化更新 `docs/01_PRD.md`。
- 导航、路由、模块归属变化更新 `docs/02_INFORMATION_ARCHITECTURE.md`。
- UI 状态、视觉规则、交互变化更新 `docs/03_UI_DESIGN_SPEC.md`。
- API、数据模型、service 边界变化更新 `docs/04_TECH_ARCHITECTURE.md`。

文档更新必须保持中文为主，保留必要 technical terms such as API、RAG、Agent、Memory、Knowledge、Workspace。

---

# 25. Implementation Status

## Milestone 1

Status: completed.

Implemented:

- Repository structure.
- Planet registry.
- Universe Portal shell.
- Study Workspace shell.
- Foundation database migration.
- Basic API contracts.

## Milestone 2

Status: completed.

Implemented:

- Study Goal service and API contracts.
- Learning Plan, Year Plan, Month Plan, Week Plan and Daily Task service contracts.
- Study Session start/finish recording.
- Study Home progress aggregation.
- Database migration `002_study_learning_workflow.sql`.
- Frontend Home and Plan workflow foundation.

Not implemented in Milestone 2:

- AI Core logic.
- Agent logic.
- RAG pipeline.
- Embeddings.
- Knowledge Graph.
- Tutor functionality.
- Review Agent.

## Milestone 3

Status: completed.

Implemented:

- Shared AI Core service entry point.
- LLM Gateway interface with deterministic local provider.
- Prompt Manager.
- Context Manager.
- Agent Manager.
- Study Tutor service as an AI Core consumer.
- Tutor API contracts.
- Tutor frontend page.
- Learning Events for Tutor interactions.

Not implemented in Milestone 3:

- RAG pipeline.
- Embeddings.
- Vector database.
- Knowledge Graph.
- Document retrieval.
- File processing.
- Source citation system.

## Milestone 3.5

Status: completed.

Implemented:

- AgentDefinition registration model.
- AgentManager registry-based resolution.
- ContextManager provider orchestration.
- Study Tutor context provider adapter.
- PromptManager prompt-key lookup.
- Provider-only LLM Gateway boundary.
- ToolRouter, Tool and Retriever interface boundaries only.

Not implemented in Milestone 3.5:

- RAG pipeline.
- Retriever implementation.
- Tool execution.
- Embeddings.
- Vector database.
- Knowledge Graph.
- Document processing.

## Milestone 4.1

Status: completed.

Implemented:

- Shared Knowledge service boundary.
- File service foundation for txt and markdown validation, extraction and chunking.
- Document, Document Chunk and Concept domain models.
- Database migration `004_knowledge_foundation.sql`.
- Knowledge API contracts for document registration, processing, listing, detail and metadata update.
- Study Knowledge frontend page for document registration, processing status, document list and chunk detail.
- Tests for document creation, file validation, text processing, chunk creation, status transitions, listing and detail.

Not implemented in Milestone 4.1:

- Embeddings.
- Vector database or vector indexes.
- Retriever implementation.
- RAG pipeline.
- Knowledge Graph.
- AI summary.
- Tutor integration.
- Source citations.

## Milestone 4.2

Status: completed.

Implemented:

- EmbeddingProvider abstraction.
- Deterministic embedding provider for local tests.
- VectorStore abstraction.
- In-memory vector store for tests only.
- Chunk embedding metadata records.
- Database migration `005_retrieval_foundation.sql`.
- RetrievalService for chunk embedding preparation and chunk-only retrieval.
- API contracts for embedding preparation, embedding status listing and chunk retrieval search.
- Tests for embedding determinism, vector store abstraction, chunk embedding pipeline, retrieval output and no Tutor/AI Core invocation.

Not implemented in Milestone 4.2:

- Real vector database deployment.
- PostgreSQL vector storage.
- pgvector.
- Production vector indexes.
- Tutor integration.
- RAG answer generation.
- Knowledge Graph.
- Source citations.

## Milestone 4.3

Status: completed.

Implemented:

- AI Core optional ToolRouter invocation flow.
- DefaultToolRouter for tool registration, lookup and invocation.
- RetrieverTool adapter over RetrievalService.
- Study Tutor retrieval access through AI Core ToolRouter only.
- Knowledge chunk context injection into Study Tutor context provider.
- Grounded Tutor response metadata.
- Learning Event retrieval metadata.
- Tutor frontend grounding chunk display.
- Tests for ToolRouter path, no direct Tutor retrieval call, empty retrieval fallback, grounded metadata and generic AI Core tool support.

Not implemented in Milestone 4.3:

- Knowledge Graph.
- Automatic summarization.
- Memory Intelligence.
- New Agents.
- Full source citation system.
- Separate RAG answer endpoint.

## Milestone 5

Status: completed.

Implemented:

- Shared Memory Manager boundary.
- MemoryRepository for storage abstraction.
- User-owned MemoryEntry lifecycle fields.
- Canonical memory scopes: global, planet and session.
- Memory lifecycle states: active, archived and expired.
- Scoped memory retrieval.
- Access timestamp updates during retrieval and context preparation.
- AI context preparation for active memory.
- Memory API contracts for create, list, update, archive and context preparation.
- Study Tutor memory context payload through AI Core context.
- Tests for scope isolation, lifecycle filtering, access time update, context preparation, Tutor memory context and no autonomous extraction or personality inference.

Not implemented in Milestone 5:

- Autonomous memory extraction.
- Personality inference.
- Psychological profiles.
- Knowledge Graph.
- Vector memory.
- Embeddings for memory.
- New Agents.
- New Planets.

## Milestone 6

Status: completed.

Implemented:

- Study Analyst as a Study Agent capability.
- Study Analytics service for progress metrics and learning insights.
- Study Analyst context provider.
- AI Core report generation through existing AgentDefinition, Prompt Manager, Context Provider, ToolRouter and LLM Gateway.
- Analytics API contracts for metrics and report generation.
- Study Analytics frontend page.
- Tests for Analyst capability registration, metric calculation, insufficient data handling, memory context injection, ToolRouter retrieval path, structured report output and no autonomous behavior.

Not implemented in Milestone 6:

- New AI system.
- New Planet.
- Autonomous decision making.
- Personality inference.
- Psychological profiles.
- Analytics persistence tables.
- Wrong Questions and Review.

## Milestone 7

Status: completed.

Implemented:

- Study onboarding service and API contracts for first active Goal creation.
- Study onboarding frontend page.
- Manual Plan productization using existing Goal, Year Plan, Month Plan, Week Plan and Daily Task data.
- Study Home daily control center backed by Goal, Daily Task, Study Session, Knowledge overview and existing Study Analytics output.
- Study execution service and API contracts for active Study Session start/finish.
- Learning Event creation on finished Study Sessions.
- Practical Memory write points through Memory Service for onboarding preferences and session learning history.
- Study Session frontend page.
- Product loop tests covering onboarding, Goal, Plan, Daily Task, Study Session, Home progress, Analytics insight, Memory write points and architecture guards.

Not implemented in Milestone 7:

- AI Core redesign.
- New AI system.
- New Agent.
- New Planet.
- Autonomous planning.
- Personality inference.
- Knowledge Graph.
- New Retrieval architecture.
- New database tables.

## Post-Milestone 7 Product Experience Update

Status: completed.

Implemented:

- Study Workspace Universe Home return entry.
- Study Workspace current Planet and user location display.
- Study Goal model expansion with `goal_type`, optional `deadline`, optional `exam_name` and `description`.
- Database migration `007_study_goal_model_expansion.sql`.
- Study onboarding goal type selection for exam, learning, reading and growth goals.
- Study Plan goal form updated for non-exam learning scenarios.
- Study Home response aliases: `progress`, `knowledgeOverview` and `analyticsInsight`.
- Knowledge upload UI with real file selection for txt, markdown and PDF metadata.
- Tests for goal types, navigation contract and Knowledge upload flow.

Not changed:

- AI Core architecture.
- Agent registration.
- RAG pipeline.
- Knowledge Graph.
- Future Planet implementation.

## Milestone 7.5 Study Domain Model Refinement

Status: completed.

Implemented:

- Normalized migration numbering before adding new Study domain migration.
- Database migration `008_study_domain_refinement.sql`.
- Added `reading` as a Study Goal type.
- Supported multiple Goals without automatically archiving previous Goals.
- Added Goal switching API contract.
- Supported multiple Plans per Goal without completing previous Plans.
- Added `plan_type` metadata for long-term, monthly and weekly plan records.
- Added optional `goal_id` relationship on Knowledge documents.
- Preserved Knowledge documents without Goal linkage.
- Added tests for multiple Goals, Goal switching, nullable deadline, multiple Plans, plan type separation, Knowledge with and without Goal, Tutor compatibility and Analytics compatibility.

Not changed:

- AI Core architecture.
- Agent registration.
- RAGFlow integration.
- RAG pipeline.
- Embeddings or vector database.
- Knowledge Graph.
- Autonomous planning.

## Milestone 7.6 Study Product Workspace UX

Status: completed.

Implemented:

- Added Study Workspace aggregation API `GET /api/study/workspace`.
- Aggregated existing Study Goal, Plan, Daily Task, Knowledge overview and Analytics output without duplicating business logic.
- Added Study Goal management UI for listing, creating and switching Goals.
- Refactored Study Home to use the current Goal, Goal switcher, plan hierarchy, Today Tasks, Knowledge count and Analytics-only insight.
- Refactored Study Plan UI into a current-Goal guided hierarchy for long-term, monthly, weekly and daily task layers.
- Added Knowledge Goal filtering while preserving independent Knowledge documents.
- Added tests for multiple Goals, Goal switching, plan hierarchy, task filtering and Knowledge goal relation.

Not changed:

- AI Core architecture.
- Agent registration.
- RAG pipeline.
- Retrieval architecture.
- Memory architecture.
- Knowledge Graph.
- Future Planet implementation.

## Milestone 7.8.1 Study Workspace IA Refactor

Status: completed.

Implemented:

- Kept Goal as Study Workspace context instead of a standalone primary navigation module.
- Added Current Goal display and switching to the Study Workspace header.
- Kept primary Study navigation focused on Home, Plan, Knowledge, Tutor, Review and Analytics.
- Preserved Goals as a management route for listing, creating and switching Goals.
- Refined Study Home around Current Goal, Today Mission, Primary Action, Recent Progress and AI Insight.
- Added `planSummary` to `GET /api/study/workspace` while preserving the existing `plans` payload.
- Refined Study Plan to use one `Create Plan Structure` action and display Goal → Long Term → Monthly → Weekly → Daily Tasks hierarchy.
- Fixed Knowledge upload enablement without changing Knowledge API behavior.
- Added IA tests for Current Goal, Home data filtering, Plan hierarchy, navigation and compatibility.

Not changed:

- AI Core architecture.
- Agent registration.
- Retrieval architecture.
- Memory architecture.
- Database schema or migrations.
- RAGFlow integration.
- Autonomous planning.

## Milestone 8.1 RAGFlow Knowledge Provider Adapter

Status: completed for provider adapter and mocked integration tests.

Implemented:

- Added `KnowledgeProvider` as the backend boundary for external Knowledge infrastructure.
- Added `RAGFlowKnowledgeProvider` and `RAGFlowClient` for dataset creation, document upload, parsing, chunk listing and retrieval search.
- Added local RAGFlow Docker Compose runtime under `docker/ragflow/`.
- Added installation guide `docs/06_RAGFLOW_INSTALLATION.md`.
- Added provider metadata fields on Knowledge documents through migration `009_ragflow_provider_metadata.sql`.
- Kept `documents.id` as the Universe canonical document id and stored RAGFlow ids only as provider references.
- Routed Knowledge document processing through RAGFlow when `KNOWLEDGE_PROVIDER=ragflow`.
- Routed Retrieval search through the provider while normalizing results back to Universe document metadata.
- Preserved the local Knowledge and deterministic retrieval path when `KNOWLEDGE_PROVIDER=local`.
- Updated Study Knowledge UI to show provider status and allow provider-backed PDF processing through the backend.

Not changed:

- AI Core remains provider-agnostic.
- Tutor and Analyst still access Knowledge only through ToolRouter and RetrievalService.
- Frontend does not call RAGFlow directly.
- Study Planet does not own RAGFlow lifecycle or provider logic.
- Production status polling, retry queues, real API-key runtime validation and citation formatting remain future work.

## Post-7.8.1 PRD Smoke-Test Fixes

Status: completed.

Implemented:

- Made `primaryAction` a backend-owned decision in Study Home / Workspace service output.
- Kept the frontend Home as a renderer of the service-provided next action instead of duplicating next-action logic.
- Updated completed Daily Task UI so completed tasks do not offer a new Start Session action.
- Clarified PDF Knowledge uploads as metadata-only when PDF parsing is unavailable.
- Added Tutor empty-question validation before API submission.
- Reduced duplicate Current Goal display in the Study Workspace header.
- Grouped Goals UI into Current Goal, Other Goals and Create Goal sections.
- Converted Analytics copy from raw metric identifiers to user-facing learning language.
- Renamed static right-side guidance to Study Context so recommendations remain sourced from Analytics / Analyst.
- Marked Review / Wrong Questions as coming later until the closed loop is implemented.

Not changed:

- AI Core architecture.
- Agent registration.
- Retrieval architecture.
- Memory architecture.
- Database schema or migrations.
- RAGFlow integration.
- Autonomous planning.
- Full Plan Builder editing for long-term, monthly and weekly layers.

## Milestone 7.9 Study Goal and Plan Productization Slice

Status: completed for the first Study-side implementation slice.

Implemented:

- Added drilled Goal creation route `/study/goals/new`.
- Changed empty Study Home / Workspace primary action to route users into the Goal creation flow.
- Kept Goals page as a management surface for Current Goal, Other Goals and editing.
- Added Goal-type Knowledge Space preview for exam, reading, learning and growth goals.
- Added Daily Task priority to the Study domain model.
- Added migration `010_study_plan_calendar_priority.sql`.
- Added Study Plan Calendar visualization for current Goal tasks.
- Added task priority editing from Study Plan.
- Added tests for task priority and Plan Calendar source behavior.

Not changed:

- AI Core architecture.
- Agent registration.
- RAGFlow provider architecture.
- Retrieval architecture.
- Memory architecture.
- Work Planet implementation.
- Dynamic Resume implementation.
- Goal-aware Knowledge Spaces persistence for bookshelf/cards.

## Milestone 10.0 Work Planet Foundation

Status: completed for the first Work Planet foundation.

Implemented:

- Registered Work Planet as an active enterable Planet.
- Added Work modules for Home, Tech Stack, Projects and Dynamic Resume.
- Added Work-owned domain models:
  - `TechStack`
  - `WorkProject`
  - `ResumeVersion`
- Added Work repository and service boundaries under `backend/app/planets/work/`.
- Added API contracts and routes:
  - `GET /api/work/home`
  - `GET /api/work/tech-stacks`
  - `POST /api/work/tech-stacks`
  - `GET /api/work/tech-stacks/{tech_stack_id}`
  - `GET /api/work/projects`
  - `POST /api/work/projects`
  - `GET /api/work/resumes`
  - `POST /api/work/resumes/draft`
- Added migration `011_work_planet_foundation.sql`.
- Added Work Workspace frontend:
  - Work Home
  - Tech Stack directory
  - Tech Stack detail
  - Projects
  - Dynamic Resume
- Work reads Knowledge through the shared Knowledge Service, but Study Goal documents require an explicit, revocable `knowledge_share_grants` record for an active Work Tech Stack; Work-owned documents remain directly visible.
- Added tests for Work Planet enterability, API contracts, Tech Stack detail, Resume evidence refs and frontend routing.

Not changed:

- AI Core architecture.
- Agent registration.
- Retrieval architecture.
- RAGFlow provider architecture.
- Memory architecture.
- No Work Agent implementation.
- No autonomous resume generation.
- No direct Work Planet dependency on Study Planet repositories.

---

## Knowledge Space Metadata Refinement

Implemented after Work Planet foundation:

- Extended shared Knowledge documents with:
  - `planet_type`
  - `tech_stack_id`
  - `tags`
- Added migration `012_knowledge_space_metadata.sql`.
- Work Knowledge uploads can bind to a Work Tech Stack and user-defined tags.
- `goal_id` remains supported and is also represented as a normalized `goal:<goal_id>` tag.
- Tech Stack detail resolves related Knowledge by direct `tech_stack_id` before falling back to subject/topic/tag matching.
- RAGFlow provider dataset selection is now scope-aware:
  - each Study Goal gets a separate RAGFlow dataset;
  - each Work Tech Stack can get a separate RAGFlow dataset;
  - unscoped Work and global documents use their own provider dataset scope.
- Work Tech Stack now also owns:
  - `WorkArticle`
  - `WorkLearningRecord`
- Tech Stack detail can create and list articles and learning records.
- Work articles are typed as `knowledge` or `note`.
- Tech Stack directory navigation uses actual Tech Stack names in creation order.
- Work Community tab reads public CSDN topic articles as discovery material only.
- Tech Stack directory navigation is now two-level:
  - first row: category scope such as `全部`, `社区`, or user-created categories;
  - second row: concrete Tech Stacks under the selected category.
- Add Tech Stack opens a modal form and only requires name and category.
- If live CSDN fetching is unavailable, the backend returns 30 CSDN discovery fallback items instead of exposing an unavailable state to the user.
- Work Community article detail reading is exposed through `GET /api/work/community/csdn/article` and rendered inline in the Work frontend.
- Community loading is non-blocking so users can return to `全部` or another category without waiting for CSDN.
- Tech Stack management now supports update and soft archive through Work Service.
- Tech Stack article authoring uses the existing `WorkArticle.content` field and renders a focused editor with an auto-generated left outline plus a compact title-level toolbar that inserts image, editable table and code content directly into the article body with basic text formatting and cell merge/split; no new Knowledge, Retrieval, AI Core or RAG behavior is introduced.
- Dynamic Resume evidence refs can include articles and learning records.

Not changed:

- Knowledge remains a shared system service.
- Work Planet does not own a separate Knowledge implementation.
- Study Planet and Work Planet do not call RAGFlow directly.
- AI Core, ToolRouter, Retrieval and Memory architecture remain unchanged.

---

# 27. Shared Persistence Foundation

## 状态

已完成本地开发 persistence foundation。

## 已实现

- 增加 shared SQLite connection、事务边界和 migration runner。
- SQLite 仅保留为显式本地开发/测试 adapter；Universe runtime 使用 PostgreSQL。
- Study、Knowledge、Memory、Work repository 继续保持原有 service contract，底层可切换为 SQLite adapter。
- `current_goal` 的唯一来源为 `user_planet_context(user_id, planet_type, current_goal_id)`。
- 多个 Study Goal 可以同时保持 active，Goal switch 只更新 Study Planet context。
- User、Goal、Plan、Task、Session、Learning Event、Document、Chunk、Memory、Work records 可以跨 API 重启读取。
- 增加 restart persistence integration tests。
- PostgreSQL adapter 在操作前检查连接状态；连接中断后只自动重试 SELECT / SHOW / WITH 等只读语句，写入不盲目重放，以避免重复业务事实。

## 约束与未完成项

- SQLite 是本地开发实现，不是最终生产数据库。
- PostgreSQL adapter 已复用相同 repository interfaces；运行环境仍必须保证 PostgreSQL 服务和备份策略可用。
- Retrieval 的 in-memory vector store 不属于本阶段持久化范围；RAGFlow provider 通过后续 runtime acceptance 负责生产检索状态。
- Session finish 的跨 Task、Learning Event、Memory、Analytics 统一 application transaction 仍是下一阶段工作。

## 28. RAGFlow Runtime Acceptance Status

已完成代码合同与本地验证：

- `KnowledgeProvider` 提供 health check、document status、retry 和 delete boundary。
- RAGFlow-backed Knowledge 文档支持异步 status refresh；Study Knowledge UI 在 `parsing` / `chunking` 状态下轮询。
- RAGFlow-backed PDF 与 TXT/Markdown 走同一处理入口；只有 `local` provider 的 PDF 保持 metadata-only，避免把旧的本地限制误用到已配置的 provider。
- Provider 删除会先同步删除 RAGFlow document，再删除 Universe metadata 和本地 chunk preview。
- Provider retrieval 只提交当前 Universe scope 内、已 `processed` 的 provider document id，避免处于索引中、失败或陈旧的 provider 文档成为 Tutor Evidence。

当前外部验收边界：

- 2026-08-13 已使用新的受控 TXT、Markdown、PDF runtime samples 确认有效 embedding 后均可到达 `processed`；Universe 不缓存或暴露 provider 凭据。
- 该样本证明 RAGFlow-backed Knowledge 的最小 runtime 闭环，不代表所有历史资料或生产容量验收完成；大 PDF、恢复演练和跨 provider 行为仍需逐项记录。
- Citation / source click-through 已在该受控验收中回链到 Universe Knowledge source；跨 provider 的位置语义仍需按 provider 单独验证。

## 30. Current Platform Foundation Status

本轮实现状态：

- 增加 `PostgresPersistence` 与 Study、Knowledge、Memory、Work repository adapter；通过 `PERSISTENCE_BACKEND=postgres` 和同一组 repository contract 接入，未重写 Planet service。
- 增加本地/S3-compatible ObjectStorage boundary，Knowledge 文档元数据继续保存在数据库，文件内容按环境进入对象存储。
- 增加 SQLite/PostgreSQL backup、受保护的 PostgreSQL restore 脚本；生产排程、异地保留、加密和恢复演练仍需由部署环境完成。
- 增加邮箱验证码注册和 SMTP sender boundary；AI Core、Agent、Tutor 不依赖认证实现。
- Plan Builder 已支持 Goal -> Long Term -> Monthly -> Weekly -> Daily 的父级校验、节点创建和同日任务排序。自动规划仍未实现。
- Study Knowledge 已从 Markdown-only textarea 升级为正文编辑器，支持标题、加粗、颜色、图片、表格、代码块、对齐、行列操作、合并和拆分单元格。
- Work Tech Stack 详情默认展示文章/笔记库；Work Home、技术栈目录和详情页提供显式写文章入口，只有用户主动进入后才展开同类正文编辑器。
- RAGFlow embedding、LLM、rerank 仍由 RAGFlow 管理；Universe health endpoint 只报告 API 可达性和可选标签，不伪造模型运行成功。受控 TXT、Markdown、PDF 已通过 runtime samples；其它历史或大文件仍必须逐份核对。
- RAGFlow dataset scope implementation status：Study 使用 `Universe OS Knowledge / Study / {goal name} ({goal id prefix})`，Work 使用 `Universe OS Knowledge / Work / {tech stack name} ({tech stack id prefix})`；上传前会按完整名称查找并复用已有 dataset，避免服务重启或重复上传生成重复作用域。
- RAGFlow 异步失败状态会保留 `providerErrorCode`；包括 `InvalidApiKey` 在内的历史或新错误都会在 UI 显示可执行的 retry / provider 检查提示。该处理不绕过 RAGFlow，也不把外部凭证写入 Universe。

## 29. Citation / Evidence 与 Review Loop

已完成：

- `backend/app/services/evidence.py` 提供共享 Evidence source normalization。
- Tutor 通过 AI Core ToolRouter 得到检索结果后，Study Tutor 将结果映射为 `sourceId`、`documentId`、`chunkId`、`title`、`quote`、`score`、`metadata` 和 `sourceUrl`。
- Knowledge Evidence API 和 Tutor response 使用同一来源形状；无结果时保持明确的 no-source 状态。
- Wrong Question 和 Review item 属于 Study 业务事实，由 ReviewService 管理；Analytics 只读取 summary，不创建 analytics persistence table。
- Review 不创建 Agent，不调用 AI Core，不修改 Retrieval、Memory 或 Knowledge architecture。

未完成：

- 真实 RAGFlow processed 文档和跨 provider 稳定位置引用的 runtime acceptance。
- 跨 repository 的 PostgreSQL unit-of-work transaction。

## 31. Study Wordbook

- Wordbook 是 Study Planet 的领域数据，不复制共享 Knowledge、Memory 或 AI Core。
- `WordEntry` 归属用户，可选关联当前 Study Goal；保存语言、单词、释义、音标、标签、词组、例句、个人笔记和只读 dictionary reference payload。
- `EnglishDictionaryService` 属于共享 Knowledge 层：它为 Study 用户建立一个 `English-English Dictionary` 参考 Document，并把已查到的音标和用法作为该 Document 的 Chunk。它可替换远程 provider，并保留少量离线 continuity reference；未知或服务不可用时返回明确状态，不伪造词典内容。
- `WordbookService` 通过 Study repository 提供按 Goal / 语言 / 标签筛选、手动创建、TXT/CSV 批量导入、同 scope 去重、详情读取与更新。创建、导入或手动刷新英语词条时只消费 `EnglishDictionaryService` 的 reference payload；个人释义、词组、例句和笔记不会被词典同步覆盖。
- SQLite 与 PostgreSQL migration 各自创建 `study_word_entries`，保持当前 repository adapter contract。
- Study Workspace 通过 `/study/wordbook` 提供列表、个人用法编辑和词典刷新；空间 Wordbook 将 tag 映射为实体词汇书，沿用 Knowledge 的书架和双页阅读流程，并显示词典参考与个人字段。前端不直接处理持久化、AI Core 或 RAGFlow。

## 32. Universe Workspace Visual Layer

- Universe Portal、Study Workspace 与 Work Workspace 共享前端视觉层：行星入口、紧凑 breadcrumb、左侧模块轨道和可降低动画的星点/流星背景。
- 视觉层只组织现有路由与 API 返回数据；Study Home 的 `primaryAction`、Goal context、Plan、Knowledge、Wordbook 及 Work 的 Tech Stack、Knowledge、Projects、Resume 仍由既有服务提供。
- 该更新不改变 AI Core、Retrieval、RAGFlow、Memory、数据库或 Planet service 边界。

## 33. Spatial Universe Room

- `room-portfolio/` 提供独立的 Three.js 空间入口。Study、Work 与 Novel 的 14 个模块分别进入独立 3D 装置，通过现有 API 聚合契约把真实数据映射为日期轨道、Goal 行星、Tutor Core、Review 晶体、Analytics 柱体、Knowledge 书籍、Work 工件和 Novel 稿纸；不使用中央网页显示面、固定抽屉或静态路由嵌入，也不复制 Planet 业务逻辑。
- 扩容资产由 `scripts/expand_room_model.py` 从原始 `RoomModel.glb` 生成；脚本只拉伸原墙面和原地板几何，保持原模型材质、墙高和地板基线。
- Knowledge 书架、Work Bench 和作品展墙是空间导航热点。书架采用原书桌的暖木配色，作品展墙只提供小说草稿写作入口。
- 空间入口与模块分组保持一一映射：学习电脑的显示器屏幕承载 Home / Goals / Tutor，计划桌承载 Plan / Review / Analytics，知识书架承载 Knowledge / Wordbook，墙面黑板承载 `/study/cards`。点击入口后相机先聚焦家具，再在近场坐标展开 3D 模块；不再使用统一的远端 `z=-50` 舞台，也不显示覆盖家具的大型白色热点框。进入模块时主房间暂时隐藏以避免墙体穿插，返回时恢复原房间与默认相机。
- Wordbook 3D 空间只消费既有 Wordbook API：每个 tag 映射为一本词汇书；书页映射 pronunciation、meaning、tags、phrases、examples 与 notes，记忆卡从英文翻至学习者释义。场景内新建台调用既有 `/api/study/wordbook/entries`，TXT/CSV 导入台调用 `/api/study/wordbook/import`，不复制 Wordbook service、持久化或 Memory 规则。
- Plan 的静态主体由 `scripts/build_plan_orbit_model.py` 在 Blender 中生成，并保留 `room-portfolio/blender/PlanOrbit.blend` 作为可编辑源文件、导出 `public/assets/PlanOrbit.glb` 供 Three.js 使用。模型使用 6 条周轨道和 42 个具名日期节点；运行时只映射日期、任务状态与点击行为，选中节点沿前轴升起并展开 Blender 任务纸带。Goal 切换、Knowledge 文档打开、Tutor 回答、Review 完成与 Novel 草稿动作仍由原 Study / Work / Novel service 和 API 完成。
- 小说草稿通过 shared persistence repository 保存；未增加 Novel Agent、AI Core 实例、RAG、Retrieval 或 Memory 架构。
- 默认相机按画布纵横比调整距离；模块世界直接复用原房间的墙面、边饰、暖木、纸张、青色、粉色和金色材质语言，移动端使用避开底部空间导航的紧凑视角。

### 33.1 当前 Study Knowledge 空间交互

- 学习电脑只以显示器屏幕作为 Study Home / Goals / Tutor 的点击入口；不使用覆盖书桌、椅子或墙面的白色选择框。
- Knowledge 文档一对一映射为书架中的实体书。书架保留每页三本书的参考场景构图，超过三本后以书架页切换；文档可按学科筛选，上传/编辑时可关联 Study Goal，并沿用既有删除 API。
- 选中书籍后必须点击封面才进入双页阅读器。页面按纸张可用高度拆分，不设置书页内滚动；提供前后翻页、页码跳转与浏览器本地书签。RAGFlow 未结束时继续显示处理状态，并展示已返回的 chunks，不重复发起解析。
- 阅读划线生成的笔记与知识卡片继续归属原 `document_id`，可选关联 `goal_id`；知识卡支持关键词隐藏、答案揭示和首次“背过了”写入学习进度。`/study/cards` 只呈现这些笔记和卡片，墙面黑板为直接入口，页面保留返回房间与底部空间导航。
- Wordbook 的 tag 一对一映射为词汇书，沿用同一实体书/双页阅读流程。记忆卡正面为英文，翻面显示学习者释义；“背过了”和“记错了”只更新既有 Wordbook 复习数据。

# End
