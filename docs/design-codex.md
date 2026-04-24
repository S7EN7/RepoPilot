# RepoPilot 完整设计文档（Codex 版）

## 1. 目标

RepoPilot 是一个面向 GitHub 仓库的智能分析工具，用来快速回答三个问题：
- 这个项目做什么
- 这个项目做到什么程度
- 复刻它需要什么能力

本项目优先交付 CLI MVP，再逐步扩展到 Web。核心价值是把仓库信息、RAG 检索和 LLM 结构化分析串成稳定流程，而不是堆叠复杂功能。

## 2. 设计原则

- 先可用，再增强
- 先结构化，再美化
- 先单体 CLI，再 Web 化
- 先最小必要数据，再可选扩展
- 所有 LLM 输出都必须可校验

## 3. 当前约束

- Python 3.12+
- uv 作为依赖管理工具
- 已有依赖包括 FastAPI、Typer、Rich、ChromaDB、LangChain、PyGithub、SQLAlchemy
- 仓库当前入口在根目录 `main.py`，但 `pyproject.toml` 已经按 `src/` 布局配置

结论：实现时应统一迁移到 `src/` 布局，避免入口和包路径冲突。

## 4. 范围定义

### Phase 1: CLI MVP

必须包含：
- GitHub 仓库采集
- 基础清洗与标准化
- 可选 RAG 检索
- LLM 结构化分析
- 等级映射
- SQLite 持久化
- Rich 终端报告

### Phase 2: RAG 增强

可选增强：
- 增量 embedding
- repo 级向量检索优化
- 分析结果缓存
- 更细粒度文件切块策略

### Phase 3: Web

后置能力：
- FastAPI API
- Jinja2 页面
- 异步任务与进度展示

## 5. 用户场景

1. 输入一个 GitHub 仓库 URL，得到一份结构化分析报告。
2. 重复分析同一仓库时，优先复用历史结果或缓存。
3. 查看历史分析记录，比较不同仓库。

## 6. 总体架构

```text
CLI / Web
  -> config
  -> github_fetcher
  -> normalize
  -> vectorstore (optional)
  -> analyzer
  -> grading
  -> database
  -> report
```

## 7. 建议目录结构

```text
repopilot/
├── src/
│   └── repopilot/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   └── commands/
│       │       ├── analyze.py
│       │       └── history.py
│       ├── web/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   ├── routes.py
│       │   └── templates/
│       ├── api/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   └── routes/
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── orchestrator.py
│       │   ├── prompts.py
│       │   └── tools.py
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── chunking.py
│       │   ├── embeddings.py
│       │   ├── retriever.py
│       │   └── vectorstore.py
│       ├── database/
│       │   ├── __init__.py
│       │   ├── session.py
│       │   ├── models.py
│       │   └── repository.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── repo.py
│       │   ├── analysis.py
│       │   └── grade.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── github_service.py
│       │   ├── analysis_service.py
│       │   ├── grading_service.py
│       │   └── report_service.py
│       ├── integrations/
│       │   ├── __init__.py
│       │   ├── github_client.py
│       │   └── llm_client.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── logging.py
│       │   ├── validators.py
│       │   └── formatting.py
│       └── core/
│           ├── __init__.py
│           ├── constants.py
│           ├── exceptions.py
│           └── types.py
├── docs/
│   ├── design.md
│   └── design-codex.md
├── .env.example
├── pyproject.toml
└── CLAUDE.md
```

说明：
- `cli`、`web`、`api` 是入口层
- `services` 是业务编排层
- `agents`、`rag`、`database`、`integrations` 是可复用能力层
- `schemas`、`core`、`utils` 提供跨模块共享能力
- `main.py` 只负责统一入口分发，不写业务细节

## 8. 核心数据模型

### 8.1 RepoData

仓库采集后的标准输入。

字段建议：
- `repo_url`
- `repo_name`
- `owner`
- `name`
- `description`
- `language`
- `topics`
- `stars`
- `forks`
- `open_issues`
- `license`
- `default_branch`
- `tree_text`
- `readme_text`
- `key_files`
- `recent_commits`
- `issue_stats`
- `pr_stats`

### 8.2 AnalysisResult

LLM 输出的结构化分析结果。

字段建议：
- `summary`
- `positioning`
- `tech_stack`
- `strengths`
- `weaknesses`
- `suggestions`
- `target_audience`
- `career_value`
- `confidence`
- `overall_score`
- `maturity_score`
- `difficulty_score`

### 8.3 GradeResult

纯逻辑映射结果。

字段建议：
- `maturity_level` 例如 L1-L5
- `difficulty_level` 例如 D1-D5
- `maturity_reason`
- `difficulty_reason`

### 8.4 AnalysisRecord

SQLite 持久化记录。

建议字段：
- `id`
- `repo_url`
- `repo_name`
- `analyzed_at`
- `summary`
- `positioning`
- `maturity_level`
- `difficulty_level`
- `overall_score`
- `analysis_json`
- `raw_response_json`

建议约束：
- `repo_url` 唯一
- `repo_name` 建索引
- `analyzed_at` 使用 UTC

## 9. 分层与依赖关系

建议依赖方向如下：

`cli/web/api -> services -> agents/rag/database/integrations -> schemas/core/utils`

约束：
- 上层可以调用下层
- 下层不能反向依赖入口层
- `utils` 和 `core` 只能放无业务副作用的通用能力
- `agents` 负责推理编排，不直接操作 Web 请求对象
- `database` 只负责持久化，不负责分析逻辑
- `rag` 只负责上下文构建，不负责最终结论生成

这样做的目的，是让 CLI、Web、API 共享同一套业务内核，避免三套逻辑各写一遍。

## 10. 数据采集设计

### 9.1 输入

只接受 GitHub 仓库 URL，支持如下形式：
- `https://github.com/owner/repo`
- `git@github.com:owner/repo.git` 可选支持

### 9.2 最小采集集

优先采集：
- 仓库元数据
- README
- 目录树
- 关键配置文件
- 最近少量 commit 摘要

关键配置文件示例：
- `package.json`
- `requirements.txt`
- `pyproject.toml`
- `go.mod`
- `Cargo.toml`
- `Dockerfile`
- `Makefile`

### 9.3 边界条件

- 私有仓库直接报错并提示权限不足
- API 限流时返回可读错误
- README 缺失时降级使用仓库描述和目录树
- 大仓库只采样关键文件，不全量拉取
- 单文件过大时截断并保留头部和尾部摘要

## 11. RAG 设计

RAG 不是必需的第一优先级，但保留接口。

### 10.1 切块策略

- README 按标题切块
- 配置文件按自然段或固定长度切块
- 代码文件默认只取高信号片段，例如入口、导出、配置、测试

### 10.2 向量库

- 使用 ChromaDB 本地存储
- 每个 repo 一个 collection，或按 repo_name + hash 命名
- 相同内容不重复 embedding

### 10.3 检索接口

- `embed_repo(repo_data)`
- `query_context(repo_name, query)`

## 12. LLM 设计

### 11.1 原则

- 不接受自由文本输出
- 强制 JSON schema
- 输出失败可重试
- 所有数值字段必须可解析

### 11.2 Prompt 输入

包含三部分：
- 仓库元数据
- 采集到的文件摘要
- RAG 检索上下文

### 11.3 输出 schema

建议字段：
- `summary`
- `positioning`
- `tech_stack`
- `strengths`
- `weaknesses`
- `suggestions`
- `target_audience`
- `career_value`
- `overall_score`
- `maturity_score`
- `difficulty_score`
- `confidence`

### 11.4 失败处理

- JSON 解析失败时重试一次
- 仍失败则返回简化结果
- 简化结果至少包含 summary 和基础评分

## 13. 等级映射

### 12.1 工程成熟度 L1-L5

依据：
- 目录组织
- 文档完整度
- 测试覆盖
- CI/CD
- 错误处理
- 配置管理
- 安全实践

### 12.2 复刻难度 D1-D5

依据：
- 技术栈数量
- 架构复杂度
- 外部依赖数量
- 领域知识门槛
- 状态管理和并发复杂度

### 12.3 规则

评分映射必须是纯函数，不依赖 LLM 临时表述。

## 14. CLI 设计

### 13.1 命令

- `repopilot analyze <github_url>`
- `repopilot history`
- `repopilot show <repo_name or id>`

### 13.2 行为

`analyze` 的标准流程：
1. 校验 URL
2. 采集仓库
3. 可选 embedding
4. 构建 prompt
5. 调用 LLM
6. 解析结果
7. 映射等级
8. 持久化
9. 渲染报告

## 15. Web / API 设计

### 15.1 Web

`web` 用于页面展示，主要职责是：
- 表单输入
- 分析进度展示
- 报告页面展示
- 历史记录列表

### 15.2 API

`api` 用于程序化访问，主要职责是：
- 提供仓库分析接口
- 提供历史记录接口
- 提供单条结果查询接口

### 15.3 路由建议

- `POST /api/v1/analyze`
- `GET /api/v1/history`
- `GET /api/v1/reports/{id}`
- `GET /healthz`

## 16. 报告设计

报告应包含：
- 一句话概述
- 项目定位
- 工程成熟度
- 复刻难度
- 综合评分
- 技术栈摘要
- 亮点
- 不足
- 建议
- 适合人群
- 求职参考价值

终端输出使用 Rich，目标是可读，不追求花哨。

## 17. 配置设计

建议 `.env` 变量：
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `GITHUB_TOKEN`
- `REPOPILOT_DB_PATH`
- `REPOPILOT_CHROMA_PATH`

## 18. 日志设计

日志分两类：
- 系统日志：结构化、可定位问题
- 业务日志：用于展示分析进度

建议记录：
- 请求开始和结束
- GitHub 拉取状态
- embedding 状态
- LLM 调用状态
- 解析失败和重试
- 入库结果

## 19. 错误处理

必须覆盖：
- URL 非法
- 仓库不存在
- 私有仓库无权限
- GitHub API 限流
- 网络超时
- LLM 超时
- JSON 解析失败
- SQLite 写入失败

原则：
- 对用户友好
- 对开发者可定位
- 不让单点失败吞掉整个流程

## 20. 性能与缓存

- 结果按 repo_url 或 repo_sha 缓存
- 已分析仓库优先读取历史记录
- embedding 只对变更内容重算
- 大文件截断后再分析

## 21. 安全设计

- API Key 仅来自环境变量
- 不在日志中打印密钥
- 私有仓库内容不外泄
- 对外部输入做基本校验
- 对 LLM 输出做 schema 校验

## 22. 实施顺序

### Phase 1

1. 统一 `src/repopilot/` 布局
2. 做 config、core、utils
3. 实现 database、schemas
4. 实现 GitHub 采集与 service 层
5. 实现分析链、grading、report
6. 串起 CLI 入口

### Phase 2

1. 加 RAG
2. 加缓存
3. 优化 prompt
4. 增强错误处理

### Phase 3

1. FastAPI API
2. Jinja2 页面
3. 异步任务
4. 进度展示

## 23. 验收标准

CLI MVP 完成时应满足：
- 输入一个公开 GitHub 仓库 URL 可以跑通全流程
- 输出一份稳定的结构化报告
- 结果写入 SQLite
- 历史记录可查询
- LLM 输出失败有兜底
- 关键错误有清晰提示

## 24. 风险

- GitHub API 限流
- 仓库内容过大
- LLM JSON 不稳定
- RAG 带来额外调试复杂度
- Web 版过早引入会稀释 MVP 资源

## 25. 结论

RepoPilot 的最佳路径是先做一个稳定的 CLI 分析器，再逐步增强检索和 Web 能力。这个版本的设计重点不是“功能最多”，而是“链路稳定、结构清晰、可持续迭代”。
