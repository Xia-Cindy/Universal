# Study Session 完成事务设计

日期：2026-08-13
状态：O5 设计已确认；尚未实施
范围：仅覆盖 `PATCH /api/study/execution/sessions/{session_id}/finish` 的本地持久化写入边界。

## 1. 目标与非目标

一次 Study Session 完成会产生四组用户事实：

1. `study_sessions` 中的完成时间、时长、笔记、感受与状态；
2. 关联 `daily_tasks` 的完成状态（如果 Session 有 `task_id`）；
3. 一条稳定 ID 的 `study_session_finished` Learning Event；
4. 一条 session scope 和一条 study planet scope 的 Memory。

目标是在 SQLite 和 PostgreSQL adapter 中让这四组事实同提交或同回滚，并保持完成请求可安全重试。

本阶段不改变 Goal、Review、Analytics、RAGFlow 或 AI Core，不引入自动计划调整，也不发送外部消息。因此不需要 outbox、队列或 schema migration。

## 2. 当前状态与风险

当前 `StudyExecutionService.finish()` 先调用 `SessionService.finish_session()`，随后依次完成 Task、写 Learning Event、写两条 Memory。各 repository 的 `save_*` 都各自进入一次 persistence transaction。

确定 ID 已避免重复计数：Learning Event 使用 `study-session:{session_id}`，两条 Memory 使用 `study-session:{session_id}:session` 与 `study-session:{session_id}:planet`。重复 finish 还会保留首次的 `durationMinutes`。这解决了重试重复计数，但不能解决第二、三或四次写入抛错后留下部分事实的问题。

## 3. 目标边界

```text
ApiFacade / FastAPI route
        |
StudyExecutionService.finish(user_id, session_id, payload)
        |
StudySessionFinishUnitOfWork.finish(command)
        |
shared SQLitePersistence / PostgresPersistence.transaction()
        |
StudySession + DailyTask + LearningEvent + MemoryEntry
```

- Route 只负责认证、payload 解析和统一错误映射；它不直接写 repository。
- `StudyExecutionService` 继续拥有 Study 业务语义和 Memory write point，不把业务规则移入路由或 SQL 文件。
- 新的 `StudySessionFinishUnitOfWork` 是 application/persistence adapter 边界：它接收已验证的完成 command，并在同一连接、同一个 transaction 中协调三个 repository adapter。
- 不允许在已打开的 unit-of-work 内调用现有会自行 `transaction()` 的 `save_session`、`save_daily_task`、`save_learning_event` 或 `MemoryService.add`。实施时为 adapter 增加明确的 `*_in_transaction(connection, value)` 内部命令，避免嵌套 `BEGIN`。
- in-memory `StudyRepository`/`MemoryRepository` 仅用于隔离单元测试；它必须通过快照/恢复或等价 staged commit 保持同一失败语义，不能被当成生产事务证明。

## 4. 完成算法与幂等规则

1. 在 transaction 前读取 Session 和 Task 所有权，解析 `endTime`，验证时长至少 1 分钟，并构造不可变的 `FinishSessionCommand`。首次完成采用该命令中的时间、笔记和感受。
2. 开启 shared persistence transaction 后，以 `id + user_id + status = in_progress` 的条件更新 Session。若受影响行数为 0，则读取已保存的 finished Session 并返回它；不得用重试 payload 覆盖首次事实。
3. 对有 `task_id` 的 Session，在同一 transaction 内把 Task 转为 completed；若 Task 已是 completed，则保留已有 `completed_at`，不把手动完成时间改写成 Session 结束时间。
4. 在同一 transaction 内插入稳定 ID 的 Learning Event 和两条稳定 ID 的 Memory。重复冲突只读取/保留既有值，不增加计数。
5. 所有语句成功才 commit。任一异常必须 rollback；客户端收到失败时，不应看见本次 Session 已完成、Task 已完成、Event 或 Memory 的任何一部分。

并发 finish 的线性化点是第 2 步的条件更新。胜出的请求写入全部事实；其余请求读回该 Session 并返回相同完成结果。当前 session ID 已是该 API 的幂等键，因此本阶段不新增 `Idempotency-Key` header 或 API 字段。

## 5. 旧数据与恢复

新实现部署后，事务中断不会产生新的半完成 Session，因此普通 retry 只重试完整 transaction。对部署前已经存在的“finished Session 但缺 Event/Memory”的历史数据，不在正常 finish endpoint 中静默补写；应在备份后用一次显式、可审计的维护脚本或 migration 处理，以免把历史数据修复误记为新的学习行为。

## 6. API、数据库与错误合同

- **API：** 保持 `PATCH /api/study/execution/sessions/{session_id}/finish` 的路径、请求体和响应形状不变。
- **数据库：** 无新增表、字段或 migration。现有 `study_sessions`、`daily_tasks`、`learning_events` 与 `memory_entries` 已有稳定主键，足以表达此事务。
- **错误：** 业务校验继续映射为客户端可修正的 4xx（无归属、无效时间、时长不足）；连接/事务异常映射为可重试的 5xx，并记录 request/session correlation。不能把 persistence 错误伪装成完成成功。
- **可观测性：** 记录 `session_id`、用户 ID（按现有日志脱敏规则）、adapter backend、阶段和 rollback 结果；不记录笔记正文或 Memory value。

## 7. 实施文件与验收

预计修改：

- `backend/app/planets/study/execution/service.py`
- `backend/app/planets/study/sessions/service.py`
- `backend/app/persistence/study.py`
- `backend/app/persistence/memory.py`
- `backend/app/persistence/sqlite.py`
- `backend/app/persistence/postgres.py`
- `backend/app/api/routes.py` 与 FastAPI 错误映射（仅去重现有校验/错误处理）
- `tests/test_study_execution_idempotency.py`，以及 SQLite、PostgreSQL adapter 的故障注入测试。

验收矩阵：

| 场景 | 必须证明的结果 |
| --- | --- |
| 首次完成 | Session、Task、1 Event、2 Memory 一次 commit 后同时可见。 |
| 相同请求重试 | 返回首次完成结果；仍只有 1 Event 和 2 Memory。 |
| 每个写入点故障注入 | transaction rollback 后没有本次部分事实；移除故障后重试得到完整单份事实。 |
| 两个并发 finish | 只有一个请求赢得状态转换；两者读取同一已完成 Session。 |
| PostgreSQL 与 SQLite | 各自运行真实 persistence integration；不能只用 in-memory repository 声称事务成功。 |
| API 回归 | 完成路径、Study Home、Analytics、Tutor 上下文和现有 178+ 后端测试通过。 |

实施提交必须先加入这些测试，再修改生产代码；没有故障注入和 PostgreSQL adapter 证据时，不得将 O5 标记为已实现。
