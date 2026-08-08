# Universe OS 交付路线图与历史总结

日期：2026-08-09
状态：当前交付基线

本文件以 Git 提交、代码和通过的测试为依据，记录已完成操作与仍需验收的事项。它不是未来功能的承诺清单；未通过真实运行验收的能力会明确标注。

## 当前入口与交付原则

- 唯一产品入口：`http://127.0.0.1:5180/`。
- 正常启动仅运行 Universe API 与空间客户端；旧 Vue 页面不再随 `startup.sh` 启动。
- 空间层只调用现有 API，不复制 Study、Knowledge、Wordbook、Work 或 Novel 的持久化。
- 本地 `docker/universe.env` 只用于运行时配置，始终不提交。

## 已完成时间线

### 2026-07-23 · Work Knowledge 与内容工作流

- 交付 Work Knowledge 的共享 Knowledge 绑定、Tech Stack 范围、文章与学习记录。
- 将社区阅读保留为发现资料，不自动写入个人 Knowledge。
- 依据：`8c7efbc`、`cea7927`、`4c0d316`、`0b663a9`。

### 2026-07-24 · 学习闭环、证据与持久化基础

- 交付 Study Knowledge 写作、Tutor Evidence、错题与 1/3/7/30 Review 队列。
- 完成 Study、Knowledge、Memory、Work 的共享持久化基础；补齐 Plan Builder 与 Work 文章编辑能力。
- 依据：`f3f3580`、`6035354`、`815a558`、`da1a6bf`、`7d5f840`、`04cf69d`、`bdb4f48`。

### 2026-07-25 · RAGFlow 生命周期与 Work 体验修复

- 交付 RAGFlow 文档状态刷新、重试、删除同步与作用域数据集逻辑。
- 修复 Work 文章入口、Tech Stack 操作和社区阅读路径。
- 依据：`03e3795`、`e755a44`。

### 2026-07-26 · Goal-aware Wordbook 与运行时兼容

- 交付可关联 Study Goal 的 Wordbook：手动/批量录入、标签、个人释义、例句、笔记和复习字段。
- 修复 PostgreSQL JSONB 与保存/列表兼容性，稳定 Knowledge 资料状态显示。
- 依据：`ae581ed`、`872a41a`、`4d9cc8c`。

### 2026-08-08 · 实体知识书架与阅读交互

- 将 Knowledge 文档和 Wordbook tag 映射为实体书；书架每页三本并支持翻页、筛选、Goal 关联、编辑和删除。
- 阅读器采用点击封面后展开的双页纸张、无书页内滚动、翻页、指定页跳转和浏览器本地书签。
- 划线生成资料归属的笔记/知识卡；知识卡支持关键词遮挡、翻面与首次“背过了”计入 Goal 进度。
- 依据：`3241ada`。

### 2026-08-09 · 空间入口、知识黑板与当前同步

- 显示器屏幕是学习空间入口；移除覆盖桌面区域的白色热点框。
- 墙面黑板进入 `/study/cards`，仅展示资料归属的知识卡片与学习笔记，并保留返回房间和快捷导航。
- Wordbook 采用与 Knowledge 一致的实体书和双页阅读/记忆卡流程。
- 更新空间、后端迁移、文档和回归测试到统一交付提交。
- 依据：`f41c815`。

### 2026-08-09 · 唯一入口收敛

- 移除旧 Vue 页面在 `startup.sh` 与 `shutdown.sh` 中的启动/停止路径；正常本地运行只暴露 5180 的空间入口。
- 清理 README、RAGFlow 安装说明和空间客户端说明中的旧页面入口，保留 Vue 源码仅作迁移与契约测试资料。
- 依据：本轮入口收敛提交。

## 当前可验收范围

- 5180 空间入口、房间导航和所有分享路由可加载。
- Study Goal、Plan、Task、Session、Review、Analytics、Knowledge、Wordbook 通过既有 API 与空间界面使用。
- Knowledge、Wordbook、Work、Novel 的持久化仍由原服务和数据库迁移负责。
- Knowledge 阅读、卡片/笔记、Wordbook 记忆卡与 Goal 进度的关系不依赖旧 Vue 页面运行。

## 仍需真实运行验收

- RAGFlow 的真实 TXT、Markdown 与大 PDF 必须在有效 embedding provider 配置下到达 `processed`，并验证 chunk、引用位置和阅读页内容；当前代码只保证状态、重试与已返回 chunks 的处理逻辑。
- PostgreSQL、RAGFlow 与对象存储的生产备份、恢复演练和外部凭据管理仍需由部署环境完成。

## 本轮验收命令

```bash
python3 -m unittest discover -s tests
cd room-portfolio && npm run build
./startup.sh
```

启动后只检查 `http://127.0.0.1:5180/`；API 文档位于 `http://127.0.0.1:8000/docs`。
