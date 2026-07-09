# Universe OS
# 05_RAGFLOW_MIGRATION_PLAN.md

Version: 0.1

Document Type: Architecture Review and Migration Plan

Status: Planning Only

Scope: RAGFlow Knowledge Infrastructure Migration

---

# 1. Current Architecture Analysis

Universe OS 当前已经形成了清晰的 Study Planet / AI Core / Knowledge / Retrieval 边界。

当前 Knowledge flow：

```text
User Upload
→ Universe Backend
→ Knowledge Service
→ Document
→ Document Chunk
→ Embedding Preparation
→ Vector Store Interface
→ Retrieval Service
→ AI Core ToolRouter
→ Tutor / Analyst
```

## 1.1 Current Knowledge Responsibilities

`backend/app/knowledge/` 当前承担：

- Document metadata 创建。
- file_type 校验。
- 调用 File Service 解析 txt / markdown / pdf metadata。
- 本地 chunking。
- 写入 `document_chunks`。
- 创建基础 `Concept`。
- Document processing status 状态转换。
- Knowledge overview 聚合。

这意味着 `KnowledgeService` 现在既包含业务 metadata，也包含基础设施级 processing 逻辑。

## 1.2 Current Retrieval Responsibilities

`backend/app/retrieval/` 当前承担：

- `EmbeddingProvider` abstraction。
- deterministic embedding provider。
- `VectorStore` abstraction。
- in-memory vector store。
- `chunk_embeddings` metadata/status records。
- chunk embedding preparation。
- chunk-only retrieval search。
- `RetrieverTool` adapter。

这层已经比较接近未来 Provider Adapter 边界，但 embedding 与 vector search 仍由 Universe OS 内部实现。

## 1.3 Current AI Core Boundary

`backend/app/ai/` 当前保持 generic：

```text
AI Core
→ AgentDefinition
→ Context Provider
→ Prompt Manager
→ ToolRouter
→ LLM Gateway
```

AI Core 通过 `ToolRouter` 调用 `retrieval.search`，不直接知道 Knowledge repository、vector store 或 Study Planet。

该边界应保留。

## 1.4 Current Tutor Boundary

`backend/app/planets/study/tutor/` 当前流程：

```text
TutorService
→ AICoreService.run()
→ ToolRouter
→ RetrieverTool
→ RetrievalService
```

Tutor 不直接调用 RetrievalService，也不直接访问 Knowledge provider。

该边界符合 RAGFlow 迁移目标，应保留。

## 1.5 Current Frontend Knowledge Boundary

`frontend/src/planets/study/knowledge/StudyKnowledge.vue` 当前通过 Universe Backend API：

- 上传 txt / markdown / pdf metadata。
- 查看 processing status。
- 查看 document list。
- 查看 chunks。

Frontend 没有直接调用内部 processing 或 retrieval 服务。

未来接入 RAGFlow 后，Frontend 仍只能调用 Universe Backend API，不暴露 RAGFlow API。

---

# 2. Migration Target Architecture

RAGFlow 应作为 Knowledge Infrastructure provider，而不是 Universe OS 业务系统。

目标架构：

```text
Frontend
→ Universe Backend API
→ Knowledge Service
→ Knowledge Provider Interface
→ RAGFlow Provider Adapter
→ RAGFlow
   ├── File Storage
   ├── Document Parser
   ├── Chunking
   ├── Embedding
   ├── Vector Index
   └── Retrieval
→ Retrieval Service
→ Retriever Tool
→ AI Core ToolRouter
→ Tutor / Analyst
```

正确边界：

```text
AI Core
→ Retriever Tool
→ Retrieval Service
→ Knowledge Provider Interface
→ RAGFlow
```

禁止边界：

```text
Frontend → RAGFlow
Tutor → RAGFlow
Study Planet → RAGFlow
AI Core → RAGFlow
```

## 2.1 Knowledge Provider Interface

未来新增 provider boundary：

```text
backend/app/knowledge/providers/
├── base.py
└── ragflow.py
```

建议 interface：

```python
class KnowledgeProvider(Protocol):
    def upload_document(self, *, user_id: str, document: dict, file_payload: dict) -> dict:
        ...

    def get_document_status(self, *, user_id: str, provider_document_id: str) -> dict:
        ...

    def delete_document(self, *, user_id: str, provider_document_id: str) -> dict:
        ...

    def search(self, *, user_id: str, query: str, filters: dict, limit: int) -> dict:
        ...

    def get_document_info(self, *, user_id: str, provider_document_id: str) -> dict:
        ...
```

Provider 返回值必须被 Universe OS adapter normalized，不能把 RAGFlow raw response 泄漏给 frontend、Tutor 或 AI Core。

## 2.2 Provider Selection

短期建议只支持一个 active provider：

```text
KNOWLEDGE_PROVIDER=local | ragflow
```

但 data model 应从第一天支持 per-document provider：

- `provider`
- `provider_dataset_id`
- `provider_document_id`
- `provider_status`

这样可以灰度迁移，也可以允许旧本地文档继续可读。

---

# 3. Component Replacement Map

| Current Component | Current Responsibility | Future With RAGFlow | Boundary After Migration |
| --- | --- | --- | --- |
| `FileService.extract_text()` | txt/markdown extraction, PDF unsupported parser notice | RAGFlow Document Parser | Knowledge Provider Adapter |
| Local Chunking | `FileProcessor.chunk_text()` creates local chunks | RAGFlow Chunking | RAGFlow infrastructure |
| `document_chunks` as source of truth | Stores local plain text chunks | Optional cache / compatibility view | Database compatibility layer |
| `EmbeddingProvider` | Deterministic local embeddings for tests | RAGFlow Embedding | Provider internals |
| `chunk_embeddings` | Embedding metadata/status | Provider reference metadata only or deprecated | Migration compatibility table |
| `VectorStore` | In-memory vector search | RAGFlow vector index / retrieval | Provider internals |
| `RetrievalService.search()` | Embeds query and searches vector store | Calls `KnowledgeProvider.search()` | Stable backend service |
| `RetrieverTool` | AI Core tool wrapper over RetrievalService | Same | No change |
| `TutorService` | AI Core consumer | Same | No direct RAGFlow dependency |
| `StudyKnowledge.vue` | Upload/status/list/chunk UI via backend API | Same backend API, provider-backed status/results | No direct RAGFlow dependency |

---

# 4. Database Migration Strategy

This milestone does not create migrations. The following is the future strategy.

## 4.1 Keep Existing Tables During Migration

Do not immediately delete:

- `documents`
- `document_chunks`
- `chunk_embeddings`
- `concepts`

Reasons:

- Existing local documents must remain readable.
- Tests and current frontend document detail depend on chunk detail.
- Rollback requires local metadata compatibility.
- RAGFlow adoption should be gradual, not big-bang.

## 4.2 Extend `documents` As Provider Metadata Source

Future `documents` should remain Universe OS business metadata and ownership source.

Recommended fields:

```text
documents
├── id
├── user_id
├── goal_id NULL
├── file_name
├── file_type
├── subject
├── topic
├── provider
├── provider_dataset_id
├── provider_document_id
├── provider_status
├── processing_status
├── error_message
├── created_at
└── updated_at
```

`documents.id` remains the Universe OS canonical document id.

`provider_document_id` is an external reference only.

## 4.3 `goal_id` Placement

Recommended future relation:

```text
Study Goal
→ Knowledge Space
→ Documents
```

`goal_id` should exist on `documents` as nullable:

- Exam goal: documents can be linked to subjects such as `408数据结构`、`数学基础`、`机器学习`。
- Reading goal: documents can be linked to one reading goal, e.g. `阅读 CSAPP` → `CSAPP.pdf`、`阅读笔记`。
- Growth goal: documents can either link to the active growth goal or remain unlinked but user-owned.

Recommended rule:

- `goal_id` is optional.
- Knowledge documents always require `user_id`.
- If `goal_id` exists, API must validate the goal belongs to the same user.
- Retrieval filters may include `goal_id`, `subject`, `topic`, and `document_id`.

This avoids forcing every Knowledge artifact into a single current Goal while still allowing goal-scoped Knowledge spaces.

## 4.4 Dataset Strategy

Potential RAGFlow dataset models:

### Option A: One dataset per user

Pros:

- Simple isolation.
- Easy user export/delete.

Cons:

- Goal-level filtering depends on metadata.

### Option B: One dataset per user + goal

Pros:

- Strong goal-scoped retrieval.
- Cleaner Study Goal Knowledge Space separation.

Cons:

- More datasets.
- More lifecycle coordination when goals archive.

Recommended default:

- Start with one dataset per user.
- Store `goal_id`, `subject`, `topic`, `document_id` as provider metadata filters.
- Revisit per-goal datasets only if retrieval quality or isolation requires it.

## 4.5 Migration Phases

1. Add provider metadata fields while keeping local flow.
2. New uploads write `provider='ragflow'` and provider ids.
3. Existing local documents remain `provider='local'`.
4. RetrievalService searches provider based on document/provider metadata.
5. Optional backfill: re-upload local documents to RAGFlow when original file/content is available.
6. After stable operation, deprecate local chunk embedding pipeline but keep read compatibility.

## 4.6 Migration Numbering Risk

Milestone 7.5 normalized the previously duplicated `006_*` prefix by moving Study Goal expansion to:

- `007_study_goal_model_expansion.sql`
- `008_study_domain_refinement.sql`

Before adding RAGFlow migrations, continue using a monotonic sequence or switch to a timestamp convention to avoid ambiguous execution order.

---

# 5. API Impact

Frontend API should remain Universe Backend API.

## 5.1 Stable API Surface

Keep current frontend-facing routes stable where possible:

- `POST /api/study/knowledge/documents`
- `GET /api/study/knowledge`
- `GET /api/study/knowledge/documents`
- `GET /api/study/knowledge/documents/{document_id}`
- `POST /api/study/knowledge/documents/{document_id}/process`
- `POST /api/study/knowledge/retrieval/search`

## 5.2 Upload API

Future upload route may internally call:

```text
KnowledgeService.create_document()
→ KnowledgeProvider.upload_document()
```

Response should remain normalized:

```json
{
  "id": "universe-document-id",
  "fileName": "CSAPP.pdf",
  "fileType": "pdf",
  "subject": "computer systems",
  "topic": "memory hierarchy",
  "provider": "ragflow",
  "processingStatus": "uploaded",
  "providerStatus": "queued"
}
```

## 5.3 Status API

`GET document detail` should refresh provider status through KnowledgeService, then return Universe-normalized status.

Do not expose:

- RAGFlow internal URLs.
- RAGFlow raw dataset/document ids unless specifically needed for debugging and access-controlled.
- Provider raw errors without normalization.

## 5.4 Retrieval API

`RetrievalService.search()` should continue returning:

- chunk content
- chunk metadata
- score
- identifiers

Provider-backed identifiers may include:

```json
{
  "provider": "ragflow",
  "documentId": "universe-document-id",
  "chunkId": "provider-chunk-id",
  "providerDocumentId": "ragflow-document-id"
}
```

Do not return generated answers from RetrievalService.

---

# 6. Frontend Impact

Frontend should not know about RAGFlow.

Expected frontend changes in future implementation:

- Display provider-backed processing status.
- Keep upload UI the same: file, subject, topic, optional goal/context.
- Show document status transitions from backend:
  - uploaded
  - parsing / processing
  - chunking
  - embedding / indexing
  - processed
  - failed
- If RAGFlow status names differ, backend maps them to Universe OS canonical statuses.
- Chunk detail may become provider-backed preview rather than locally stored full chunk rows.

No frontend direct calls to:

- RAGFlow upload API.
- RAGFlow dataset API.
- RAGFlow search API.

---

# 7. Implementation Milestones

## Milestone 8.1: RAGFlow Provider Adapter

Objective:

Add provider interface and RAGFlow adapter without changing user-facing behavior.

Scope:

- Add `KnowledgeProvider` protocol.
- Add `LocalKnowledgeProvider` adapter around current local behavior if useful.
- Add `RAGFlowKnowledgeProvider` skeleton/client boundary.
- Add provider config.
- Add tests with mocked RAGFlow responses.

Out of scope:

- Production RAGFlow calls from current upload flow.
- Database migration.
- Frontend change.
- Tutor change.

Acceptance criteria:

- KnowledgeService can be constructed with a provider.
- RAGFlow adapter normalizes upload/status/search responses.
- No AI Core import or dependency on RAGFlow.

## Milestone 8.2: Knowledge Service Migration

Objective:

Move document upload/status orchestration behind KnowledgeProvider.

Scope:

- Add database migration for provider metadata fields.
- Preserve existing documents.
- New documents can store provider references.
- Document detail refreshes provider status.
- PDF/txt/markdown upload flow works via provider abstraction.

Acceptance criteria:

- Existing local documents remain readable.
- New provider-backed documents show normalized status.
- User ownership is enforced before provider calls.
- Frontend API response remains stable.

## Milestone 8.3: Retrieval Migration

Objective:

Move retrieval search from local embedding/vector store to provider-backed search.

Scope:

- RetrievalService calls `KnowledgeProvider.search()`.
- Keep `RetrieverTool` unchanged.
- Keep AI Core ToolRouter unchanged.
- Support filters: user_id, goal_id, subject, topic, document_id.
- Keep local retrieval fallback during transition.

Acceptance criteria:

- Tutor and Analyst still call retrieval through ToolRouter.
- RetrievalService returns normalized chunk results only.
- No Tutor direct provider call.
- No generated answers from RetrievalService.

## Milestone 8.4: Tutor Grounded Knowledge Validation

Objective:

Validate Tutor grounded responses work with provider-backed retrieval.

Scope:

- Add integration tests using mocked RAGFlow search results.
- Verify grounding metadata includes provider-backed identifiers.
- Verify no-source path remains explicit.
- Verify no fake citations.

Acceptance criteria:

- Tutor behavior remains structured.
- AI Core remains generic.
- ToolRouter path is preserved.
- When provider is unavailable, Tutor still answers with clear Knowledge limitation.

---

# 8. Risks

## 8.1 Provider Lock-In

Risk:

RAGFlow response shapes, dataset model, and status names may leak into Universe OS business logic.

Mitigation:

- Keep `KnowledgeProvider` interface stable.
- Normalize all provider responses.
- Store provider refs as metadata, not canonical business ids.
- Add adapter contract tests.

## 8.2 RAGFlow Availability

Risk:

Upload, processing, or retrieval may fail when RAGFlow is unavailable.

Mitigation:

- Keep document records in Universe DB before provider calls.
- Track provider status and error message.
- Keep local compatibility/fallback during migration.
- Return explicit Knowledge unavailable state to Tutor.

## 8.3 Data Synchronization

Risk:

Universe `documents.processing_status` and RAGFlow status may drift.

Mitigation:

- Treat Universe DB as metadata/ownership source.
- Refresh provider status on document detail and background polling.
- Record `provider_updated_at`.
- Avoid assuming provider success until status confirms processed/indexed.

## 8.4 User Ownership Isolation

Risk:

Provider dataset or search results might leak cross-user documents if metadata filters are wrong.

Mitigation:

- Validate user ownership before every provider operation.
- Include user-scoped dataset or mandatory `user_id` metadata filters.
- Add tests proving user A cannot retrieve user B documents.
- Prefer one dataset per user initially if RAGFlow operationally supports it.

## 8.5 Migration Compatibility

Risk:

Existing local documents/chunks/embeddings may become inaccessible after switching provider.

Mitigation:

- Keep `provider='local'` path.
- Do not drop `document_chunks` or `chunk_embeddings` initially.
- Backfill provider documents incrementally.
- Add compatibility tests for local and provider-backed documents.

## 8.6 Retrieval Quality Regression

Risk:

RAGFlow chunking/embedding behavior differs from current local deterministic pipeline.

Mitigation:

- Compare retrieval results on the same sample documents.
- Keep user-visible source metadata.
- Validate no-source and low-confidence behavior.
- Use acceptance tests with expected subject/topic/document filters.

## 8.7 Migration Ordering

Risk:

Existing duplicate migration prefix `006_*` can cause execution ambiguity.

Mitigation:

- Establish migration naming convention before adding RAGFlow migrations.
- Prefer monotonic sequence or timestamp prefix.
- Document applied migration order.

---

# 9. Open Decisions

1. RAGFlow dataset strategy:
   - one dataset per user
   - one dataset per user + goal
   - one global dataset with strict metadata filters

2. Original file storage ownership:
   - Universe OS stores original files and uploads copies to RAGFlow
   - RAGFlow stores originals and Universe OS stores references only

3. Chunk visibility:
   - keep local chunk cache for UI preview
   - fetch chunk previews from RAGFlow on demand

4. Provider fallback:
   - local fallback only for existing documents
   - local fallback also for new documents when RAGFlow is down

5. Status mapping:
   - exact RAGFlow status names must be mapped to Universe canonical statuses after adapter spike.

---

# 10. Final Recommendation

Proceed with RAGFlow migration only through a provider abstraction.

Do not change AI Core, Tutor, or frontend API contracts first.

Recommended sequence:

```text
Provider Interface
→ RAGFlow Adapter
→ Document Provider Metadata
→ KnowledgeService Upload/Status Migration
→ RetrievalService Provider Search
→ Tutor Grounding Validation
→ Local Pipeline Deprecation
```

RAGFlow should replace infrastructure responsibilities:

- file parsing
- chunking
- embedding
- vector indexing
- retrieval

Universe OS should keep business responsibilities:

- user ownership
- Study Goal relationship
- subject/topic metadata
- Memory relationship
- frontend API contract
- AI Core / ToolRouter boundary
- Tutor structured response policy

---

# End
