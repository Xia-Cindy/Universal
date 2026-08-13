# Universe OS 代码优化与功能新增计划

日期：2026-08-12
状态：O1、F1、O2、O3、O5、F3、F4、F5、F2、F6 已完成；O4 因来源许可与实际实现核验要求保持未开始。
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

### O3 交付记录（2026-08-13）

- **目标：** 将 Knowledge 书架和知识黑板的 CSS 从空间房间 shell 中分离，避免后续模块优化时出现跨模块层叠误改。
- **受影响文件：** `room-portfolio/src/style.css`、`room-portfolio/src/styles/bookshelf.css`、`knowledgeBoard.css`。
- **数据库/API：** 无。CSS 选择器、数值、响应式规则和 iframe 内参考样式均未改变；root 只新增表达既有书架层级的共享 z-index token。
- **风险与控制：** 导入顺序会影响层叠结果，因此两个模块在原全局字体 import 后加载，保留相同 specificity 和实际 z-index。
- **验收：** eslint、Vite build、5180 核心路由 smoke 通过；浏览器确认 `/study/knowledge` 的 iframe 与 `/study/cards` 的知识黑板均挂载且无 console error。

### O5 实施记录（2026-08-13）

- **目标：** 明确 Study Session 完成时 Session、Task、Learning Event 与两条 Memory 的 application unit-of-work，消除“各 repository 各自提交”造成的部分写入风险。
- **受影响文件：** `backend/app/planets/study/execution/{service,unit_of_work}.py`、sessions service、Study/Memory persistence adapters 与故障注入测试。
- **数据库/API：** 不需要 migration；保留现有 execution finish API 形状。稳定 session ID、event ID 与 memory ID 已足以作为幂等边界。
- **设计结论：** 在 shared persistence 的一个 transaction 内，以 Session `in_progress -> finished` 条件更新作为并发线性化点；Task、Event 和两条 Memory 只在同一 transaction 内写入。不得通过嵌套现有 repository transaction 实现。
- **实施结果：** SQLite 与 in-memory 覆盖成功、重复、五个写入点故障注入、failure 后 retry 与并发 finish；全量后端 205 通过，5180 路由/API proxy 回归通过。PostgreSQL 在一次性独立 schema 中实际覆盖故障回滚与 retry，测试后 schema 已删除且未触碰用户数据。旧半完成数据仍必须单独、可审计地修复，普通 finish 不会静默补写。完整设计与边界见 `docs/13_STUDY_SESSION_UNIT_OF_WORK_DESIGN_2026-08-13.md`。

### O4 许可证与实际实现核验记录（2026-08-13，阻止本地化）

- **核验目标：** 判断 `thebuggeddev/books` 与 `books-sigma-ashen.vercel.app` 是否提供可合法本地化的实际参考实现；本次不改产品代码、不复制源文件、不改变数据库或 API。
- **实际实现证据：** 上游默认分支为 `main`，核验提交为 `22ee800461780f6b70205e37445ab2ecc6b35dac`。仓库完整树只有 `.gitignore`、`index.html`、`package*.json`、`public/` 和 `src/`；实际书架实现在根 `index.html`，而不是 Vite `src/main.js` 占位模板。该文件使用 CDN `three.js r128`、`THREE.WebGLRenderer`、raycast/slots/spring 动画和 `requestAnimationFrame`；与部署页 `https://books-sigma-ashen.vercel.app/` 的 SHA-256 均为 `c9ebdab5dea82fd78d08c36ff2d94688eb2abced21c368e97eb34d849ba66f38`（79,756 bytes），因此确认部署页确实来自该实际实现。
- **许可证证据：** GitHub 仓库元数据 `license` 为 `null`，递归文件树没有 `LICENSE`、`COPYING` 或等价授权文件，仓库页面也未声明许可证。公开可见和可 fork 不等于获得复制、修改或分发的授权；在无许可证情况下，默认版权规则适用。
- **结论与范围：** O4 的“将必要资源本地化”前置条件未满足，**不得**将该 `index.html`、Three.js 场景、程序化封面、动画或资源复制进 Universe，也不得以视觉相似重写来规避该门槛。现有运行时 iframe 引用保持原样，不增加外部实现的本地副本；本次无 migration、API 变更、单元测试或 5180 行为变更。
- **恢复条件：** 只有在作者提供明确书面授权或向上游加入可核验、兼容的许可证并明确涵盖所需实现/资源后，才重新启动 O4；届时先记录许可证版本和 attribution，再以离线降级、封面/开启/翻页视觉对比、5180 路由回归和独立提交验收。

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

### F1 上传前运行时探针实施记录（2026-08-13）

- **目标：** 将 embedding 配置从“health API 可达”提升为可执行的上传前 runtime acceptance，避免在 provider 已失效时继续创建资料、数据集或解析队列。
- **受影响文件：** `backend/app/knowledge/providers/{base,ragflow}.py`、`backend/app/knowledge/service.py`、`backend/app/api/{routes,contracts}.py`、`backend/app/main.py`、`room-portfolio/src/{api,Experience}.jsx`、相关测试与运行文档。
- **数据库/API：** 无 migration、无写操作；新增 `POST /api/knowledge/provider/runtime-verification`。响应只含 `provider`、`status`（`verified`/`failed`）、`verified`、`checkedAt`、`errorCode` 和脱敏 `message`，不含 RAGFlow 原始响应、资料 ID、数据集 ID 或凭据。
- **实现：** provider 对一个当前用户已有的 `processed` RAGFlow 资料执行固定文本的 `/api/v1/retrieval` 请求。该请求让 RAGFlow 做 query embedding 和 document retrieval；代码不调用 datasets、documents upload 或 chunks parse API，也不会新建或修改 Universe 数据。
- **失败语义：** 无已完成资料时返回 `RAGFLOW_RUNTIME_NO_PROCESSED_SOURCE`；embedding 凭据、模型绑定、连接、超时和空检索分别映射为稳定且无秘密的错误代码与提示。书架只在 RAGFlow provider 返回 `verified` 时继续上传。
- **验收结果：** provider adapter 测试证明唯一 upstream 调用为固定 retrieval；服务测试证明不上传/解析且不泄漏 provider 错误。使用与正常运行相同环境的临时 API 实例，在 `2026-08-13T18:47:28+08:00` 收到真实 `200 / verified`；实例随后立即停止。书架测试、Vite build 与 5180 核心路由 smoke 也通过。

### F3 交付记录（2026-08-13）

- **目标：** 在既有“背过/记错”事实层之上，为资料归属知识卡和 Wordbook 词条提供同一份可解释、可手动覆盖的间隔复习日程；不把笔记混入复习队列。
- **受影响文件：** `backend/app/models/study.py`、`backend/app/planets/study/recall/service.py`、Study repository 与 SQLite/PostgreSQL persistence、`backend/app/api/{contracts,routes}.py`、`backend/app/main.py`、空间书架的 `api.js`、`Experience.jsx`、`readerModel.js`、`useBookshelfBridge.js`、`DeployedBooks.jsx` 及相应测试。
- **数据库/API：** 新增 PostgreSQL `020_study_recall_schedules.sql` 和 SQLite `008_study_recall_schedules.sql`；以 `(user_id, source_type, source_id)` 唯一约束保存 source-owned schedule。新增 `GET /api/study/recall/schedules`、`GET /api/study/recall/schedules/{source_type}/{source_id}` 与 `PATCH` 同路径手动调整合同；不改变原卡片、词条或 Goal API 形状。
- **调度与风险控制：** 背过依序采用 1/3/7/14/30 天，记错立即回到当天且理由明确说明不会把一次记错当作永久能力判断。完全相同的同日结果只保存一次，既不重复增加 Wordbook 错误数，也不重复写 Goal mastery；首次背过的 Goal 事实仍由既有 Learning Event 逻辑处理。笔记可以保留原有背过事实，但不会显示或调整间隔日程。
- **验收：** 新增 `tests/test_study_recall_v2.py` 覆盖卡片创建、背过、记错、同日幂等、Wordbook 手动调整、SQLite 重启、Goal 过滤与公开合同；完整后端 `unittest discover` 为 183 通过。书架纯模型测试、eslint 与生产构建均通过。实际 8000 API 重启后新 schedule 路由返回 200，项目 `scripts/smoke_spatial_routes.py` 对 5180 的所有核心路径和 API proxy 全部通过。

### F4 交付记录（2026-08-13）

- **目标：** 让用户从已关联 Study Goal 的资料阅读器中，向指定且未归档的 Work Tech Stack 授予可撤销的只读引用；无授权的 Study 资料不能由 Work 列表、详情、首页统计或 Tech Stack 详情读取。
- **受影响文件：** Knowledge model/repository/service、SQLite/PostgreSQL persistence、`backend/app/api/{contracts,routes}.py`、`backend/app/main.py`、Work service、空间书架 API/iframe bridge/Study 授权对话框与相应测试。
- **数据库/API：** 新增 PostgreSQL `021_knowledge_share_grants.sql` 与 SQLite `009_knowledge_share_grants.sql`，唯一约束为 `(user_id, document_id, tech_stack_id)`。新增 `GET/POST /api/study/knowledge/documents/{document_id}/share-grants` 与 `DELETE /api/study/knowledge/share-grants/{grant_id}`；Work documents API 改为仅返回 Work-owned 或授权资料，并附 `accessMode` 与授权元数据。
- **风险与控制：** 授权记录不拥有文件、chunk、provider 数据或注释，只保存原 document ID、源 Goal、目标 Tech Stack。Work 对授权资料不可编辑、删除、重解析或刷新；撤销、Tech Stack 归档、删除授权所指的源 Goal 链接和源资料删除均删除/失效授权。Work 自己上传的资料不受此过滤影响。
- **验收：** `tests/test_knowledge_share_grants.py` 覆盖默认拒绝、授权可见、详情只读、撤销、Tech Stack 归档、源资料删除、源 Goal 链接移除、Tech Stack 详情与 SQLite 重启；完整后端回归为 190 通过。空间客户端 eslint、书架模型测试、生产构建与重启后 5180 核心路由/API proxy smoke 均通过；浏览器确认 Study 实体书读者出现“授权 Work”入口，Work 书架仍无编辑/授权控制。

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

### F5 2026-08-13 实施记录

- **完成内容：** 新增 PostgreSQL `022_document_goal_links.sql` 与 SQLite `010_document_goal_links.sql`，回填历史 Study `documents.goal_id`。资料响应同时保留兼容主关联 `goalId` 与完整 `goalIds`；新增 `GET/PUT /api/study/knowledge/documents/{id}/goal-links`。书架编辑器改为可多选学习目标。
- **边界：** 主关联继续用于既有 RAGFlow dataset scope；新增目标关联不复制 document、chunk、annotation 或 provider document，也不重复提交/解析。检索先从链接表限定允许的 Universe document ID，再进入本地向量或 provider 查询。
- **F4 兼容：** Work 授权仍显式记录 `sourceGoalId`，可来自主或次关联；只有移除该具体链接才撤销对应授权。
- **验收：** `tests/test_document_goal_links.py` 覆盖创建/列表/API、检索隔离、替换不重解析与 SQLite 重启；`tests/test_knowledge_share_grants.py` 覆盖次关联授权；与检索基础共 20 项通过。

### F2 2026-08-13 设计记录

- **目标：** 将浏览器本地书签扩展为可选的 user/document 阅读位置同步，同时保证 API 不可用、未登录或离线时仍立即使用现有 localStorage。
- **受影响文件（实施时）：** Knowledge model/repository/persistence、SQLite/PostgreSQL migrations、API contracts/routes/main 与空间书架 bridge、reader model、API client。
- **数据库/API：** 拟新增 `reading_progress`，唯一键 `(user_id, document_id)`；拟新增 `GET/PUT /api/study/knowledge/documents/{id}/reading-progress`。`spreadIndex` 是可恢复的权威位置，`pageNumber` 仅为读者提示；不回填浏览器私有 localStorage。
- **风险与控制：** 不把页码当作 PDF/provider 页码、学习时长、Goal 完成或 Wordbook 复习事实。客户端先落 localStorage，再 best-effort 同步；跨设备用 `clientUpdatedAt` 与服务端时间解决 last-write-wins 冲突。资料删除清理进度，Goal link/Work grant 变化不影响源资料进度。
- **实施门槛与验收：** SQLite/PostgreSQL 重启、离线回退、双设备新旧冲突、页码 clamp、资料删除和 5180 断网/恢复均需覆盖；不得新增 RAGFlow 任务或 Goal mastery。完整设计见 `docs/14_READING_PROGRESS_SYNC_DESIGN_2026-08-13.md`。

### F2 2026-08-13 实施记录

- **完成内容：** 新增 PostgreSQL `023_reading_progress.sql` 与 SQLite `011_reading_progress.sql`，以 `(user_id, document_id)` 保存可选资料阅读位置。新增 `GET/PUT /api/study/knowledge/documents/{id}/reading-progress`；服务端验证资料归属，并在数据库 upsert 冲突条件中原子保留最新 `clientUpdatedAt`，过期客户端写入返回 `server_newer` 而不覆盖。
- **阅读器语义：** iframe 的书签仍立即写入 `universe-books:reader-bookmarks`；随后尽力 PUT。打开书本先用本地值，只有远端位置更新时才采用远端。同步失败只显示“仅保存在本设备”，不阻塞翻页或把 API 故障误报为资料失败。
- **边界：** 位置只包含双页 `spreadIndex`、显示页码和可选短标签；不保存内容、划线、阅读历史、Goal mastery、Wordbook 事实或 RAGFlow 任务。资料删除清理对应进度；Goal 链接与 Work 授权变动不会删除源资料进度。
- **验收：** 新增 `tests/test_reading_progress.py` 覆盖接受/拒绝过期写入、原子 upsert、字段校验、资料删除、无 Learning Event 与 SQLite 重启；完整后端回归 199 通过。书架模型覆盖本地/远端最新位置选择；eslint、书架测试和 Vite build 通过。重启 API 后，真实 5180 proxy PUT/GET 对现有资料返回 `accepted` 和相同的 page/spread/label，过期 PUT 返回 `server_newer`，未调用 parse/retry。

### F6 2026-08-13 实施记录

- **完成内容：** 新增只读 `GET /api/study/feedback/recommendations`。它只读取当前 Goal 的待完成任务、到期错题复习和 Knowledge 的同步阅读位置，返回 `recommendations`、`evidence`、`generatedFrom` 与数据充分性；不新增数据表。
- **可解释性与控制：** 每条建议有稳定 id、类型、跳转目标、文字理由和对应事实（task/review/document/page）。所有建议标注 `requiresConfirmation: true`；接口不调用 Analytics 的 AI report，不更新 task、plan、review、Learning Event、Memory、RAGFlow 或阅读进度。Analytics 空间只显示提示，不提供执行按钮。
- **验收：** 新增 `tests/test_study_feedback_recommendations.py` 覆盖到期复习/未完成任务/阅读位置证据、无 Goal 降级、合同与调用前后数据不变；完整后端回归 202 通过。eslint、书架模型测试、Vite build 通过；重启后 5180 proxy 返回 2 条全部要求确认的推荐，OpenAPI 路由存在，核心空间路由与 API proxy smoke 通过。
O4 必须在来源许可与实际参考实现确认后再开始，不能以“外观类似”为依据自行重写。

## 4. 每个阶段的交付要求

每个阶段开始前必须记录：目标、受影响文件、数据库变更、API 变更、风险、验收样例。
完成后必须提供：迁移（如需要）、单元/集成测试、5180 回归结果、文档同步、`TODO.md`、
`CHANGELOG.md` 和独立逻辑提交。外部服务不可用时，报告阻塞证据，不以健康检查或表单成功替代端到端验收。
