# Universe OS 当前能力与短板

版本：0.1  
状态：Implementation Review  
更新时间：2026-07-24

本文记录四阶段执行后的真实平台边界。已实现代码、测试和本地 runtime 结果优先于产品宣传文案。

## 一、四阶段完成情况

### 阶段 1：共享持久化与 Study 上下文

- 通过既有 repository interface 接入 shared SQLite persistence 和 migration runner。
- User、Study Goal、Plan、Task、Session、Learning Event、Knowledge Document/Chunk、Memory、Work records 可跨 API 重启读取。
- `user_planet_context(user_id, planet_type, current_goal_id)` 是 Study Current Goal 的唯一来源。
- Goal switch 只切换 Study Planet context，不删除其他 Goals。
- Session finish 首次完成时同步关联 Task、Learning Event 和 Memory write point，重复 finish 不重复计数。

当前边界：SQLite 是本地开发实现，PostgreSQL adapter 和跨 repository 的真正数据库事务仍未完成。

### 阶段 2：RAGFlow Knowledge runtime

- 已完成 KnowledgeProvider health check、异步 status refresh、前端轮询、retry 和 provider delete synchronization。
- Study Goal 使用隔离的 RAGFlow dataset scope；Work Tech Stack 也使用独立 scope。
- RAGFlow API key 不经过前端，也不写入仓库。

真实验收结果：RAGFlow health/API 可访问，但当前 embedding model provider 返回 `InvalidApiKey`，所以 TXT、Markdown、PDF 尚未真实达到 `processed`。在 embedding provider key/model 修复前，RAGFlow 能力必须标记为实验性。

### 阶段 3：Citation / Evidence 与 Tutor 合同

- Tutor 支持 `current_goal` / `all_study` Knowledge scope。
- 检索结果统一为 `sourceId`、`documentId`、`chunkId`、`title`、`quote`、`score`、`metadata`、`sourceUrl`。
- 无匹配 Knowledge 时明确显示无来源状态，不生成 fake citation。
- Tutor UI 支持来源 quote preview、回到 Knowledge 文档和保存为 Learning Event。
- Knowledge 文档可通过 Evidence API 返回同形状来源对象。

当前边界：来源回源依赖 Universe 文档详情和 RAGFlow chunk preview；RAGFlow 尚未完成真实 processed 验收，因此不能宣称生产级 grounding。

### 阶段 4：Wrong Question → Review → Analytics

- Wrong Question 作为 Study 业务事实保存，并自动生成 1、3、7、30 天四个 Review item。
- Review completion 幂等，重复完成不重复计数。
- Review summary 进入 Analytics progress summary 和推荐来源。
- Study Review 页面支持记录错题、查看节奏和完成复习。
- 没有新增 AI Agent；Review 不依赖 AI。

## 二、当前平台可实现功能

### Universe 与 Planet

- Universe Portal 展示 Study Planet、Work Planet 和未来 Planet 占位入口。
- 用户可以进入 Study Workspace 或 Work Workspace，并从 Planet 返回 Universe Home。

### Study Planet

- 创建 exam、learning、reading、growth Goal，deadline 可为空。
- 多 Goal 管理、切换 Current Goal、归档 Goal。
- 按 Goal 建立 Long Term、Monthly、Weekly Plan 和 Daily Tasks。
- 查看今日任务、编辑任务优先级、完成任务、执行 Study Session、记录时长、笔记和感受。
- Study Home 汇总当前 Goal、Today Mission、progress、Knowledge overview、Analytics insight。
- Tutor 可基于 Study context、Memory context 和可用 Knowledge chunks 返回结构化回答。
- 保存 Wrong Question，并按 1/3/7/30 节奏复习。
- Analytics 可展示任务完成、学习时长、学习事件、Review summary、weak areas 和 next actions。
- Study Knowledge 可写 Markdown 文章或登记 txt/markdown；PDF 当前支持 metadata-only 或 provider-backed 实验路径。

### Knowledge、Retrieval、Memory

- Knowledge 是共享服务，可按 user、Planet、Goal、Work Tech Stack 和 tags 组织资料。
- 文档、chunk、concept、provider metadata 均有 repository/API 边界。
- Retrieval 可使用本地 deterministic embedding/in-memory vector store 测试路径，也可通过 RAGFlow provider 访问外部检索基础设施。
- Memory 支持 global、planet、session scope 以及 active、archived、expired lifecycle，并向 AI Core 提供 prepared context。

### Work Planet

- Tech Stack 目录、详情、文章/学习记录、项目 evidence、Dynamic Resume draft。
- Work Knowledge 独立归属 Work，并可通过 shared Knowledge Service 引用 Study Knowledge 摘要或 evidence refs。
- CSDN 社区内容用于发现和 inline 阅读，不自动写入用户 Knowledge。

## 三、当前短板与风险

1. **RAGFlow 还没有通过真实文件验收。** 当前问题是 RAGFlow 配置的 embedding provider key 无效；需要用 TXT、Markdown、PDF 各一份完成 upload、异步 polling、processed、失败重试和删除同步。
2. **SQLite 仍是本地开发持久化。** 尚无 PostgreSQL adapter、对象存储和生产备份策略。
3. **Citation 目前是 Evidence contract，不是完整出版级引用系统。** 已有来源 id、quote 和回源 URL，但还缺跨 provider 的稳定页码/段落定位、版本化和失效来源处理。
4. **Session finish 是幂等 application workflow，但还不是覆盖 Task、Event、Memory、Analytics input 的单一数据库事务。** 跨 repository 事务需要 shared unit-of-work 或 PostgreSQL transaction adapter。
5. **本地用户模型仍是默认 local user。** 尚未形成多用户认证、权限、租户隔离和并发冲突处理。
6. **Plan 仍偏 scaffold + task editing。** 还不是完整的可重排 Plan Builder，也没有自动规划能力。
7. **Study 文章编辑器仍是 Markdown 入口。** Work 文章编辑器更丰富，Study 侧尚未统一到同等的正文编辑体验。
8. **Review 是可靠事实闭环的第一版。** 目前复习结果是手工标记，没有间隔算法、遗忘曲线、错题相似度或 AI 辅助解释。
9. **Analytics 目前是规则指标 + 可选 deterministic Analyst。** 缺少长期趋势、可解释的时间序列、用户确认后的建议反馈和跨 Goal 比较。
10. **Work 与 Study 的共享仍需要明确 consent。** 目前通过 shared Knowledge/evidence refs 共享，后续需要让用户明确选择哪些 Goal Knowledge 可以被 Work 引用。

## 四、短期验收顺序

1. 修复 RAGFlow embedding provider 配置，完成三种真实文件 processed 验收。
2. 验证重启不丢数据、不同 user/Goal/Planet scope 不串数据。
3. 让一个 Tutor answer 从 `sources[0]` 回到具体 document/chunk，并在 UI 保存 Learning Event。
4. 创建一道 Wrong Question，按 1/3/7/30 四个 item 完成，确认 Analytics summary 更新。
5. 验证 Work 只能通过 shared Knowledge API 和 evidence refs 引用 Study，不得直接依赖 Study repository。
