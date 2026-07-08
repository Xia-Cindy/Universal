# Universe OS
# 04_TECH_ARCHITECTURE.md

Version: 1.1

Document Type: Technical Architecture Specification

Product: Universe OS

Purpose: Define the technical architecture, service boundaries, data model, API direction and implementation principles.

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

MVP 只实现 Universe Portal 和 Study Planet。Future Planets 只作为 Portal placeholders。

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

实现时必须先完成 Study Planet MVP 闭环。Future Planet 不得扩展为真实业务功能。

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

Recommended technology:

- Vue 3。
- TypeScript。
- Vite。
- Pinia。
- Vue Router。
- TailwindCSS。

## 4.1 Frontend Structure

```text
frontend/
└── src/
    ├── universe/
    │   ├── portal/
    │   └── planet-loader/
    ├── planets/
    │   └── study/
    │       ├── home/
    │       ├── plan/
    │       ├── session/
    │       ├── knowledge/
    │       ├── tutor/
    │       ├── review/
    │       └── analytics/
    ├── components/
    ├── services/
    ├── stores/
    └── router/
```

## 4.2 Routing Architecture

MVP routes：

```text
/                         Universe Portal
/study                    Study Home
/study/plan               Learning Plan
/study/plan/goal          Goal
/study/session/:id        Study Session / Study Record
/study/knowledge          Knowledge
/study/knowledge/upload   File Upload
/study/knowledge/summary/:id AI Summary
/study/tutor              Tutor / RAG Q&A
/study/review             Review
/study/review/wrong-questions Wrong Questions
/study/analytics          Analytics
```

Future placeholder routes such as `/work`、`/novel`、`/life`、`/creator` can show coming later only if needed. They must not contain real Workspace implementation in MVP.

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
  "goal_name": "2027 MEM",
  "exam_name": "MEM",
  "deadline": "2026-12-26",
  "subjects": ["math", "english", "logic", "writing"],
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
- Study Planet 是 MVP 唯一可进入 Planet。
- Future Planets 只能作为 Portal placeholders。
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

---

# End
