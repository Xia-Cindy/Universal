# Universe OS 当前能力与短板

版本：0.2
状态：Current Capability Review
更新时间：2026-08-12

本文是当前交付基线的能力说明，不替代早期 PRD 和设计提案中的历史决策。代码、数据库迁移、自动化测试和已验证的本地运行结果优先于宣传文案；任何尚未完成真实运行验收的外部服务能力均不得视为已交付。

## 一、当前运行基线

- 唯一正常用户入口是 `http://127.0.0.1:5180/`。
- 入口客户端为 `room-portfolio/`：React、Vite、React Three Fiber 与 Three.js 渲染个人房间、家具热点和模块世界。
- Knowledge 与 Wordbook 的当前书架阅读器是参考书架 HTML 注入后的 DOM/CSS 3D 动效（iframe `srcDoc`），不是 Three.js/WebGL 书架；房间本身仍是 Three.js。
- `frontend/` 中的 Vue 源码保留给迁移与契约测试，不由 `startup.sh` 启动，也不是产品入口。
- Universe API 保持 Study、Knowledge、Wordbook、Work 与 Novel 的既有服务边界；空间客户端不创建第二套持久化或 AI 系统。

## 二、已可使用的能力

### Universe、Study 与复习

- Study 支持 exam、learning、reading、growth Goal 的创建、切换、归档和当前 Goal 聚合。
- 支持 Goal 下的长期、月、周计划和每日任务，以及学习 Session、Learning Event、Review 与 Analytics 汇总。
- Wrong Question 可生成 1/3/7/30 天 Review 项；完成操作具备幂等语义。
- Tutor 通过 AI Core、ToolRouter 与 Retrieval 边界获取可用 Knowledge 上下文；无来源时不得伪造 citation。

### Knowledge、书架与卡片

- Knowledge 文档可以独立存在或关联 Study Goal；资料以实体书形式显示，支持每页三本、更多书架页、学科筛选、编辑、确认删除和处理状态提示。
- 读者在点击实体封面后打开无内滚动的双页纸张，支持双页翻动、页码跳转和浏览器本地书签。
- 划线内容可保存为原资料归属的笔记或知识卡片；卡片可隐藏关键词、揭示答案并在首次“背过了”时一次性计入关联 Goal 进度。
- `/study/cards` 只展示上述资料归属的卡片和笔记；它们不会被复制到另一个数据模型。
- Wordbook 以标签为词汇书，保留词条的发音、个人释义、短语、例句和笔记，并支持正反面记忆卡、背过/记错结果及复习时间记录。

### Work、Novel 与持久化

- Work 提供 Tech Stack、关联 Knowledge、项目证据、文章、学习记录和简历草稿 API；社区内容仅作发现和站内阅读，不自动写入个人 Knowledge。
- Novel 提供持久化草稿的新建与编辑，不新增 Novel Agent。
- PostgreSQL 是正常运行时的持久化适配器；SQLite 是显式选择的本地/测试兼容方案。两者均经过 repository 边界访问。
- 本地对象存储与 S3 兼容对象存储均有边界；备份与受保护恢复脚本见 `docs/11_OPERATIONS_AND_RECOVERY.md`。

## 三、RAGFlow 的真实边界

- Provider adapter 支持上传、状态刷新、重试、删除同步与 provider-backed retrieval；Study Goal 和 Work Tech Stack 可保持隔离作用域。
- 处理中资料会显示真实状态，并在 provider 已返回 chunk 时先显示可读页面；这不表示完整解析已经结束。
- 2026-08-13 的受控 TXT、Markdown 和新 PDF 已在有效 embedding 配置下到达 `processed`，各有非零 provider chunk、阅读页内容和 Tutor 来源回链。该样本验收不代表所有历史长 PDF 已完成；每份长文档仍需单独核对 provider 状态与 chunks，且不得为验收而盲目重试。
- RAGFlow API key 与其他凭据仅存在本地运行时配置中，前端、Tutor、AI Core 都不能直接调用 RAGFlow。

## 四、已识别的短板与风险

1. **外部书架依赖。** 当前参考书架在运行时读取外部部署 HTML；网络不可用、参考站点变更或跨域策略变化会影响视觉层。应先确认源代码许可和实际实现后，再决定是否本地化可复用资源。
2. **历史长 PDF 仍需逐份验收。** 受控小型 TXT、Markdown 与新 PDF 已完成端到端 runtime 验收，但 Provider 连通、表单成功或进入队列都不等于其它文档完成；既有大 PDF 必须在不重试堆积队列的前提下单独核对状态、chunks 和可读页。
3. **空间客户端文件过大。** `SpatialModuleScene.jsx`、`DeployedBooks.jsx` 与全局样式文件职责过多，后续拆分必须覆盖分享路由、交互热点和阅读器回归。
4. **旧 Vue 代码仍是测试依赖。** 它不再是入口，不能在未迁移相应测试与契约前直接删除。
5. **事务与身份边界仍需生产化。** Session 完成尚无跨 Task、Event、Memory 的数据库级 unit-of-work；已在 `docs/13_STUDY_SESSION_UNIT_OF_WORK_DESIGN_2026-08-13.md` 固化不改 API/schema 的实施设计，但尚未写入生产代码。认证已经有注册/验证/登录 API 边界，但完整的多用户授权、冲突处理与部署运维尚未完成。
6. **复习和分析仍是第一版。** 当前状态记录可靠，但尚未引入经用户验证的间隔重复模型、长期趋势解释或跨 Goal 对比。
7. **跨 Planet 引用需要明确同意。** Work 通过 shared Knowledge/evidence 边界共享资料，但用户可见的授权与撤销流程仍未产品化。

## 五、建议验收顺序

1. 对既有长 PDF 逐份只读核对 provider 状态、已完成 chunk、阅读页与 Tutor 来源；仅在用户明确授权后重试单份失败资料，不把已完成的 F1 小型样本验收重复提交。
2. 建立 5180 的核心路由回归：`/`、`/study`、`/study/knowledge`、`/study/wordbook`、`/study/cards`、`/work`、`/novel`。
3. 在 PostgreSQL 环境验证 Goal、Knowledge、Wordbook、Review 与 Novel 的重启后读取和用户/Goal scope 隔离。
4. 先拆分空间客户端的展示层，再考虑任何视觉替换；每一个拆分都必须保持现有 API、路由与资料所有权。
5. 在数据库迁移和 API 合同明确后，再实施间隔重复、跨 Planet 授权或事务性 Session 完成等新增能力。
