# Universe OS 代码优化与功能新增计划

日期：2026-08-12
状态：O1、F1、O2 已完成；其余阶段待按顺序实施
依据：当前代码审计、`docs/10_PLATFORM_CAPABILITIES_AND_GAPS.md` 与现有 Git 历史

## 0. 审计结论与边界

当前产品的正常入口是 5180 空间房间。房间使用 React Three Fiber/Three.js；当前
Knowledge/Wordbook 书架是参考站点 HTML 驱动的 DOM/CSS 3D 阅读器，而不是 WebGL
书架。两种技术不应混称，也不能在优化时误删任一层。

本轮已完成一项低风险收敛：`room-portfolio/src/Experience.jsx` 以
`KNOWLEDGE_RESOURCES` 统一 Study/Work Knowledge 的列表、详情、刷新、创建、处理与
缓存选择，保留原 API、路由和 Work 不可编辑/删除的限制。

暂不删除的内容：

- `frontend/` Vue 源码：它仍被迁移/契约测试读取。
- `SpatialModuleScene.jsx`：它仍承载非书架模块世界，不是可直接删除的“旧 3D 书架”。
- RAGFlow 的 local fallback 与兼容表：F1 只验证了受控本地样本，仍不能删除兼容路径或推定所有历史资料已完成。

所有实施阶段都必须保持：一个 AI Core、资料的原始所有权、前端仅经 Universe API
访问、以及 5180 是唯一正常用户入口。

## 1. 功能优化计划

| 阶段 | 目标与主要文件 | 数据库/API | 风险 | 验收标准 |
| --- | --- | --- | --- | --- |
| O1：运行时与回归基线 | 建立 5180 核心路由 smoke suite；涉及 `room-portfolio/src/Experience.jsx`、`api.js`、路由测试与运行文档。 | 无 schema 变更；不得改变现有 API 合同。 | Three 场景加载慢会导致脆弱测试。 | `/`、Study、Plan、Knowledge、Wordbook、Cards、Work、Novel 可加载；API health 与现有后端测试通过。 |
| O2：空间客户端职责拆分 | 将 `DeployedBooks.jsx` 拆为参考场景桥接、书架目录、阅读器、注释桥接；将 `SpatialModuleScene.jsx` 按模块展示拆分。 | 无 schema 变更；维持 `postMessage` 事件名与 API 形状。 | 拆分可能损坏封面开启、翻页、书签或深链接。 | 书架分页/筛选/编辑/删除、阅读器翻页/跳页/书签、卡片和 Wordbook 记忆卡逐项回归。 |
| O3：样式与资产治理 | 把 `style.css` 中书架、黑板、房间 shell 的样式域分离；为共享色彩、间距和 z-index 建立变量。 | 无。 | CSS 层叠、移动端和 iframe 样式回归。 | 无重复全局选择器；桌面与窄屏截图基线通过；`prefers-reduced-motion` 不被破坏。 |
| O4：参考书架可靠性 | 先核验 `thebuggeddev/books` 的实际源码、许可和部署差异；仅在可复用条件满足时，将必要资源本地化并保留 attribution。 | 无；保持现有书架数据映射。 | 未经许可复制、外部依赖替换造成视觉/动作偏差。 | 离线或参考站点不可达时有可读降级；视觉/封面/翻页与已确认参考一致；来源说明完整。 |
| O5：后端边界与事务 | 评估 Study Session 完成的 unit-of-work，整理路由中重复的请求校验/错误映射。主要涉及 `backend/app/api/`、Study repository/service、persistence adapters。 | 可能新增迁移或 transaction adapter；实施前先提交 schema/API 设计。 | 原子性改动影响任务、Learning Event、Memory 计数。 | 成功与故障注入测试证明不出现部分写入；既有 174+ 测试与 API 回归通过。 |

### O1 的实施顺序

1. 固定开发环境、入口和 API health 检查，不重启或重新解析已有 RAGFlow 长文档。
2. 增加路由和关键交互 smoke 测试；测试只使用夹具或现有测试数据。
3. 在这条基线通过后，才分别提交 O2、O3、O4、O5；每阶段一个逻辑提交。

### O1 交付记录（2026-08-12）

- **目标：** 为 5180 的正常入口和核心空间路由建立可重复回归基线。
- **受影响文件：** `scripts/smoke_spatial_routes.py`、`tests/test_spatial_route_smoke_contract.py`、`README.md`、`TODO.md`、`CHANGELOG.md`。
- **数据库/API：** 无 schema 或 API 合同变更；脚本只读取 SPA 路由和经 Vite 代理的 `GET /api/health`。
- **风险：** HTTP 成功只能证明 SPA fallback 与代理可达，不能单独证明 Three.js 场景已经挂载或视觉正确。
- **验收结果：** 脚本覆盖 `/`、`/study`、`/study/plan`、`/study/knowledge`、`/study/wordbook`、`/study/cards`、`/work`、`/novel` 及 `/api/health`；真实本地服务全部通过。浏览器级抽查确认每条路由的 React 根节点已挂载，Knowledge/Wordbook 包含书架 iframe，且未捕获运行时 error。
- **后续门槛：** O2/O3 拆分前必须先运行此脚本、路由合同测试、完整后端测试和浏览器级核心路径抽查。

### O2 交付记录（2026-08-13）

- **目标：** 在不改变已确认的参考书架画面、实体翻页、API 或 iframe 通信事件的条件下，降低 `DeployedBooks.jsx` 的职责耦合。
- **受影响文件：** `room-portfolio/src/DeployedBooks.jsx`、`room-portfolio/src/bookshelf/shelfCatalog.js`、`readerModel.js`、`useBookshelfBridge.js`、`bookshelfModels.test.mjs`、`room-portfolio/package.json`。
- **数据库/API：** 无 migration、后端 API 或 `postMessage` event/payload 变更。新模块只承接既有目录计算、真实 chunk 到阅读页的映射，以及父窗口的消息分派。
- **风险与控制：** 参考书架仍来自受控 iframe 文档，事件桥接是高风险边界；保留原始事件名、回调和书签 localStorage key，未移动 iframe 内已验收的 CSS/动画脚本。
- **验收：** `npm run test:bookshelf` 覆盖三册分页、筛选、真实 chunk、注释与书签模型；eslint、Vite build、5180 核心 route smoke 通过。浏览器重新打开已处理 PDF，封面展开后仍显示原始 chunk 和 `第 1 / 1 页`，无 console error。

## 2. 新增功能计划

| 阶段 | 用户价值与范围 | 数据库/API | 前置条件与风险 | 验收标准 |
| --- | --- | --- | --- | --- |
| F1：RAGFlow 真实资料验收 | 让用户能够判断一份 TXT、Markdown、PDF 是否真正可问答、可阅读。只补验收与可观测性，不重复提交已有大文件。 | 必要时扩展 provider 诊断字段；不暴露 RAGFlow 原始响应。 | 有效 embedding provider、可控样本与运行资源。 | 三类文件各有一次 `processed` 记录、非零 chunks、书架页面可读、Tutor 来源可回链；失败显示明确原因。 |
| F2：阅读来源与书签同步 | 将“本地书签”升级为可选的用户级、资料归属阅读进度，同时保持离线本地书签。 | 新 migration：reading_progress；`GET/PUT` 文档进度 API。 | 需要用户身份与多设备语义，不能覆盖本地未同步状态。 | 同一用户重启后保持页码/书签；无登录或 API 不可用时安全退回本地。 |
| F3：间隔重复 V2 | 在现有背过/记错事实之上提供可解释、可手动覆盖的复习调度。 | 新 review schedule 字段或表；Review queue 合同扩展。 | 算法不应把一次“记错”误当永久能力判断。 | 卡片和单词都有下次复习日期、理由和手动调整；幂等完成和 Goal 统计保持正确。 |
| F4：知识空间授权 | 让用户显式决定某个 Goal 的资料是否可被 Work 引用，并可撤销。 | 可能新增 `knowledge_share_grants`；Work Knowledge 查询加入 grant 过滤。 | 关系与权限变更需要迁移、审计与删除策略。 | 未授权资料不出现在 Work；授权/撤销即时生效且不复制原资料。 |
| F5：Goal 多对多资料关联 | 支持同一资料服务多个 Goal，同时不破坏现有可空 `documents.goal_id` 的单 Goal/独立资料。 | 新 link table、迁移和查询合同；先设计回填规则。 | 高风险：检索 scope、书架筛选、删除语义与 Goal 进度都受影响。 | 单资料可关联多个 Goal；默认 scope 与全局查看明确；删除和检索不会串 Goal。 |
| F6：计划与学习反馈闭环 | 在用户确认下由 Analytics 把任务完成、Review 和资料阅读转化为可解释的计划建议。 | 先只增加 read-only recommendation API；不自动改计划。 | 不得产生虚假学习记录或擅自调整任务。 | 建议可追溯到用户事实，用户明确确认后才变更计划；无 AI 时基础计划仍可用。 |

### F1 只读预检记录（2026-08-12）

- **目标：** 在不上传、重试或重新解析既有长 PDF 的前提下，确认 provider 是否已经具备一次真实资料验收的条件。
- **受影响文件：** 无产品代码或数据库变更；仅读取 Universe provider health、既有文档详情和 5180 阅读器。
- **API/数据库：** 只读 `GET /api/knowledge/provider/health`、`GET /api/study/knowledge/documents` 及单份资料详情；未调用 process、retry、upload、delete 或 Tutor 写入接口。
- **观察结果：** provider health 返回 `ragflow / ok`，这只证明 Universe 到 RAGFlow API 可达，且 Universe 未提供可验证的 embedding 模型标签。两份《张培基：英汉翻译教程》仍为 `chunking`（一份 provider 为 `running`、一份为 `cancel`）且无 chunks。DAMA PDF 也仍为 `chunking / running`，但详情已返回 527 个非空 chunks。
- **阅读器证据：** 在 `/study/knowledge` 按“数据治理”筛选并打开 DAMA 资料后，书页显示 635 页；翻页从第 1–2 页实际进入第 3–4 页，页面文本来自返回 chunks。这个结果证明“持续解析中先阅读已完成内容”的同步逻辑有效。
- **未满足的验收：** provider-backed retrieval 有意只过滤 `processing_status == processed` 的资料，因此上述 chunking 文档不能作为 Tutor 来源验收。API 可达、处于队列或已有 chunks 都不等于 F1 的 `processed` 成功。
- **继续条件：** 需要 RAGFlow 管理面确认一个可执行的 embedding provider，并由用户提供一个可控的新样本或明确授权使用哪一份非长文档样本。满足后才可各执行一次 TXT、Markdown、PDF 的端到端验收；不得拿现有长 PDF 重试凑结果。

### F1 交付记录（2026-08-13）

- **目标：** 使用用户授权的新建小型 TXT、Markdown、PDF 验证真实 RAGFlow embedding、索引、Universe chunk 同步、检索、Tutor 来源链接和 5180 阅读器；不重新提交既有长 PDF。
- **受影响文件：** `backend/app/knowledge/providers/ragflow.py`、`backend/app/core/settings.py`、`backend/app/api/routes.py`、`tests/test_ragflow_provider.py`、`docker/ragflow/universe.env.example`、`docs/06_RAGFLOW_INSTALLATION.md`、`README.md`、`TODO.md`、`CHANGELOG.md`。
- **数据库/API：** 无 migration 或公开 API 合同变更。RAGFlow client 将直接 socket timeout 归一为 provider 错误，Universe 因而写入 `failed` 而不是永久 `parsing`。新建 scoped dataset 默认 `Plain Text`、RAPTOR 关闭、GraphRAG 关闭；不覆盖既有 dataset 或自动重解析。
- **运行恢复：** 初次新 PDF 任务曾继承旧数据集的 DeepDOC/高级处理并使 amd64 仿真 worker 无进度。仅取消该新任务，重启本地 RAGFlow worker，确认同一 PDF 的单文档基础配置后恢复一次。既有两份历史 PDF 和其它长资料均未重新提交。
- **处理证据：** TXT、Markdown、PDF 分别成为 Universe `processed`，各有一个 provider-backed nonzero chunk。PDF 的 executor 记录了解析、embedding 与 Elasticsearch indexing，完成时为 65 tokens/1 chunk；未在文档中保留 API key、数据集 ID 或 provider document ID。
- **检索与 Tutor：** Universe RetrievalService 对 PDF 的精确查询返回其 Universe document/chunk 映射。`all_study` Tutor 调用返回了 TXT、Markdown 和 PDF 三条稳定 Knowledge source URL；当前 Study Tutor 回答仍是既有规则式学习建议，F1 只以真实检索和来源回链为验收，不把它表述为自由生成问答质量。
- **5180 验收：** `/study/knowledge?documentId=…` 载入书架 iframe，展开 PDF 后显示真实 chunk 文本和 `第 1 / 1 页`，上一页/下一页均正确禁用，浏览器无 error。
- **测试：** `python3 -m unittest tests.test_ragflow_provider tests.test_knowledge_upload_flow`：16 通过；`python3 -m unittest discover -s tests`：178 通过；`room-portfolio npm run build` 通过；`scripts/smoke_spatial_routes.py` 覆盖的 5180 核心路由和 API proxy 全部通过。
- **风险与限制：** Apple Silicon 上的 amd64 RAGFlow 冷启动约五分钟；这不是对任意大型 PDF、历史队列或其他 embedding provider 的完成承诺。后续只在单独授权下处理遗留长资料。

## 3. 优先级与依赖

```text
O1 回归基线
 ├── O2/O3 代码与样式拆分
 ├── F1 RAGFlow 真实验收
 │    └── F2 阅读进度同步
 └── O5 事务设计
      ├── F3 间隔重复 V2
      └── F6 反馈建议

F4 授权 ──> F5 多 Goal 资料关联
```

建议执行顺序：**O1 → F1 → O2 → O3 → O5 → F3 → F4 → F5 → F2 → F6**。
O4 必须在来源许可与实际参考实现确认后再开始，不能以“外观类似”为依据自行重写。

## 4. 每个阶段的交付要求

每个阶段开始前必须记录：目标、受影响文件、数据库变更、API 变更、风险、验收样例。
完成后必须提供：迁移（如需要）、单元/集成测试、5180 回归结果、文档同步、`TODO.md`、
`CHANGELOG.md` 和独立逻辑提交。外部服务不可用时，报告阻塞证据，不以健康检查或表单成功替代端到端验收。
