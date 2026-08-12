# F2：资料阅读进度与书签同步设计

日期：2026-08-13  
状态：已批准设计，尚未实施

## 1. 目标与非目标

目标是在不替换现有实体书阅读器的前提下，为同一用户、同一 Knowledge document 保存一份**可选**的服务器阅读位置。它应让用户在另一台设备或浏览器中回到上次阅读的双页 spread，并保留一个可命名书签。

本阶段不做：

- 不将阅读页码记为 Study Goal 完成、背过或学习时长。
- 不同步 Wordbook 记忆卡状态；其复习事实和 schedule 已有独立数据模型。
- 不同步未登录用户数据，也不读取或上传浏览器之外的历史 localStorage。
- 不把 Work 授权资料的进度写回 Work；进度只归属于源 Study document 与用户。

## 2. 当前边界

当前书架阅读器使用浏览器 `localStorage` key `universe-books:reader-bookmarks`。它保存以 `documentId` 为 key 的对象，并在 iframe 的 `save-bookmark` 消息抵达时立即本地更新。该行为在 API 不可用时仍可工作，必须保持。

Knowledge document 现在可关联多个 Goal，但阅读进度不是 Goal 关系，也不跟随每个 Goal 拆分。一份 document 对一个 user 仅有一条同步进度；该记录引用 Universe `document_id`，不复制 RAGFlow 文档、chunks 或书页文本。

## 3. 拟议数据模型

新增 `reading_progress` 表，唯一性为 `(user_id, document_id)`：

| 字段 | 含义 |
| --- | --- |
| `id` | 稳定 UUID。 |
| `user_id` | 进度所属用户。 |
| `document_id` | 仅允许源 Knowledge document。删除资料时级联删除。 |
| `spread_index` | 零基双页位置，用于真实翻页模型，而非 PDF 原始页号。 |
| `page_number` | 面向界面与兼容书签的 1 基左页页码。 |
| `bookmark_label` | 可空、用户可编辑的短标签；默认可由客户端显示“书签第 N 页”。 |
| `client_updated_at` | 客户端写入时的 ISO 时间，仅用于冲突比较。 |
| `updated_at` | 服务端接收写入的时间。 |
| `payload` | 与现有 SQLite/PostgreSQL repository 的可移植 payload。 |

`spread_index` 是权威恢复值；页内容因 chunk 增加而重排时，客户端必须将它 clamp 到当前总 spread 范围。`page_number` 仅用于可读提示，不能反向解释为 provider PDF 页码。

## 4. API 合同

```text
GET /api/study/knowledge/documents/{document_id}/reading-progress
PUT /api/study/knowledge/documents/{document_id}/reading-progress
```

`PUT` 请求体：

```json
{
  "spreadIndex": 4,
  "pageNumber": 9,
  "bookmarkLabel": "数据治理框架",
  "clientUpdatedAt": "2026-08-13T10:20:30+08:00"
}
```

响应包含规范化后的所有字段与 `conflictResolution`：`accepted`、`server_newer` 或 `clamped`。服务端必须验证 document 归属；Work 读取授权资料时只能读取该用户的源 document 进度，不得创建 Work-owned 副本。

## 5. 合并与离线语义

1. 打开书本时，客户端先立即使用 localStorage 恢复，不能等待网络。
2. 若 GET 成功，比较本地 `updatedAt`（F2 实施时补写）与服务器 `updatedAt`：较新的有效位置覆盖当前 reader；相同或缺失时保留本地。
3. 用户点击“添加书签”或离开 reader 时，先写 localStorage，再 best-effort PUT 服务器；PUT 失败不显示为资料处理失败，只保留本地并提示“仅保存在本设备”。
4. 对两个不同设备的同时写入采用 last-write-wins，以 `clientUpdatedAt` 为首要比较、`updated_at` 为次要比较；服务端较新时返回其值，客户端不应静默覆盖。
5. 没有可用身份或文档被删除时返回明确错误；客户端继续本地模式并清理无效远端引用。

## 6. 迁移与删除策略

- PostgreSQL 与 SQLite 各新增一份 migration；不会回填现有 localStorage，因为浏览器私有数据不可安全枚举。
- `documents` 删除时删除相应 reading progress；无需单独调用 provider。
- user 删除时级联删除；Goal 链接增删、F4 Work grant 撤销、RAGFlow 状态刷新均不删除进度。
- 不记录完整阅读历史、选中文字或内容摘要，避免把阅读位置扩大为行为追踪。

## 7. 实施文件与验收

实施时预计涉及 `models/knowledge.py`、Knowledge repository/persistence、SQLite/PostgreSQL migrations、API contracts/routes/main、`room-portfolio/src/{api,DeployedBooks,bookshelf/useBookshelfBridge,bookshelf/readerModel}.js` 及测试。

验收：

1. 同一 user/document 的 PUT/GET 在 SQLite 与 PostgreSQL 重启后保持最新 position。
2. 无 API 或 API 返回失败时，本地书签照常恢复且不阻塞翻页。
3. 本地比远端新、远端比本地新、相同时间和越界 spread 都有确定结果。
4. 删除 document 后进度不可读；删除 Goal link、撤销 Work grant 后源 document 进度仍存在。
5. 5180 阅读器在断网模拟下仍可保存本地书签，在恢复 API 后可同步；不产生任何 Goal mastery 或新的 RAGFlow 任务。
