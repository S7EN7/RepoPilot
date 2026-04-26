# RepoPilot 设计方案与开发计划

## Context

RepoPilot 是一个面向 GitHub 仓库的智能分析助手，目标是帮助开发者快速判断一个开源项目的价值、难度和成熟度。这是一个求职作品，需要快速完成、代码易于理解，同时展示 LLM + RAG + 全栈工程能力。

**技术栈：** FastAPI + Jinja2 + ChromaDB + LangChain + PyGithub + SQLAlchemy + SQLite + aiosqlite + Typer + Rich + logging + uv

**LLM：** OpenAI 兼容代理（api.timebackward.com），Chat + Embedding 双接口，API Key 通过环境变量传入

---

## 一、项目目录结构

### Phase 1: CLI MVP

```
src/repopilot/
├── __init__.py
├── main.py                      # 统一入口，分发 CLI/Web
├── config.py                    # 配置 + 环境变量
│
├── utils/                       # 通用工具函数
│   ├── __init__.py
│   └── logger.py                # 日志配置（输出到 logs/ 目录 + 终端）
│
├── github/                      # GitHub 数据采集
│   ├── __init__.py
│   ├── schemas.py               # RepoData 数据模型
│   └── service.py               # GitHub 采集（URL 校验 + PyGithub 采集 + 日志）
│
├── rag/                         # RAG 检索增强
│   ├── __init__.py
│   ├── vectorstore.py           # ChromaDB embedding + 检索
│   └── service.py               # RAG 业务编排（分块、入库、查询）
│
├── agent/                       # LLM Agent 编排
│   ├── __init__.py
│   ├── analyzer.py              # LangChain 分析链（Prompt + Chain）
│   ├── prompts.py               # Prompt 模板定义
│   └── tools.py                 # Agent 工具函数（可扩展）
│
├── analysis/                    # 分析评级与持久化
│   ├── __init__.py
│   ├── grading.py               # 等级映射（纯逻辑）
│   ├── schemas.py               # AnalysisResult, GradeResult
│   ├── repository.py            # 分析记录 CRUD 操作
│   └── service.py               # 分析业务编排（串联 fetch→embed→analyze→grade→save）
│
├── database/                    # 数据库基础设施
│   ├── __init__.py
│   ├── sqlite.py                # SQLAlchemy 引擎、会话管理、ORM 模型
│   └── chroma.py                # ChromaDB 客户端初始化、collection 管理
│
└── cli/                         # CLI 表现层
    ├── __init__.py
    ├── app.py                   # Typer 命令定义
    └── report.py                # Rich 终端渲染
```

运行时目录（自动创建，已加入 .gitignore）：
```
database/                        # 运行时数据存储
├── repopilot.db                 # SQLite 数据库文件
└── chroma/                      # ChromaDB 向量数据

logs/                            # 日志文件
└── repopilot.log                # 运行日志（按日期轮转）
```

### Phase 2 新增

```
src/repopilot/
└── web/                         # Web 服务（页面 + 接口）
    ├── __init__.py
    ├── app.py                   # FastAPI 实例、中间件、挂载路由
    ├── views.py                 # 页面路由（返回 Jinja2 HTML）
    ├── api.py                   # REST 接口（返回 JSON）
    ├── static/                  # 静态资源（CSS/JS/图片）
    └── templates/               # Jinja2 模板
        ├── base.html
        ├── index.html
        └── report.html
```

说明：
- `utils/` 放通用工具函数（日志等），不含业务逻辑
- `github/`、`rag/`、`database/` 是可复用能力层，CLI 和 Web/API 共享
- `agent/` 负责 LLM 交互编排（Prompt、Chain、Tools），不直接操作数据库
- `analysis/` 负责评级逻辑、数据模型和持久化，调用 `agent/` 获取 LLM 分析结果
- `cli/` 是 Phase 1 入口层
- `web/` 是 Phase 2 入口层，包含 FastAPI 实例、页面路由、REST 接口、模板和静态资源，全部在一个包内
- `main.py` 负责统一入口分发，不写业务细节
- `logs/` 存放运行日志文件，按日期轮转

---

## 二、等级体系设计

### 维度 A：工程成熟度（Project Maturity Level）

衡量项目本身的完成度、代码质量、架构规范程度。

| 等级 | 英文名 | 中文名 | 说明 |
|------|--------|--------|------|
| L1 | Prototype | 原型级 | 概念验证，代码零散，无工程规范 |
| L2 | Basic | 基础级 | 能运行，有基本结构，缺少规范约束 |
| L3 | Standard | 标准级 | 模块清晰，有文档和错误处理 |
| L4 | Production | 生产级 | 测试完备、CI/CD、日志、配置管理齐全 |
| L5 | Enterprise | 企业级 | 高可用、可观测、安全合规、团队协作规范 |

### 维度 B：复刻难度（Replication Difficulty）

衡量开发者理解并复刻该项目所需的能力水平。

| 等级 | 英文名 | 中文名 | 说明 |
|------|--------|--------|------|
| D1 | Beginner | 新手级 | 掌握语言基础即可上手 |
| D2 | Junior | 初级级 | 需熟悉框架和常见设计模式 |
| D3 | Intermediate | 中级级 | 需要扎实工程经验和系统设计能力 |
| D4 | Senior | 高级级 | 需要深入领域知识或分布式经验 |
| D5 | Expert | 专家级 | 需要稀缺专业技能 |

### 评估指标

LLM 将根据以下指标综合评定等级：

**成熟度评估依据：**
- 代码组织结构（目录、模块划分）
- 依赖管理（是否有 lock 文件、版本约束）
- 文档完整度（README、API 文档、注释）
- 测试覆盖（是否有测试目录、测试框架）
- CI/CD 配置（GitHub Actions 等）
- 错误处理和日志
- 安全实践

**复刻难度评估依据：**
- 技术栈复杂度（涉及多少领域）
- 代码量级（文件数、估算行数）
- 架构复杂度（微服务/单体、依赖关系）
- 领域知识门槛（是否需要专业背景）
- 外部依赖复杂度（第三方服务、API 数量）

---

## 三、核心数据流

```
用户输入 GitHub URL
       │
       ▼
┌─────────────────┐
│ github_fetcher   │  PyGithub 获取：
│                  │  - repo 元数据（stars, forks, language, topics）
│                  │  - 目录结构树
│                  │  - README.md 内容
│                  │  - 关键文件（package.json, requirements.txt, Dockerfile 等）
│                  │  - 最近 commits 摘要
│                  │  - Issues/PR 统计
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ vectorstore      │  ChromaDB：
│                  │  - 将 README + 关键文件分块 embedding
│                  │  - 存入本地 ChromaDB
│                  │  - 为 LLM 分析提供检索上下文
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ analyzer         │  LangChain：
│                  │  - 构建分析 Prompt（含 repo 元数据 + RAG 检索结果）
│                  │  - 调用 LLM 生成结构化分析 JSON
│                  │  - 包含：概述、定位、亮点、不足、建议等
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ grading          │  等级评定：
│                  │  - 解析 LLM 返回的评分
│                  │  - 映射到 L1-L5 和 D1-D5 等级
└────────┬────────┘
         │
         ▼
┌────────┴────────┐
│ database         │  SQLite 持久化：
│                  │  - 存储分析记录
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ report           │  Rich 渲染：
│                  │  - 终端美化输出完整分析报告
└─────────────────┘
```

---

## 四、分析报告输出格式

```
╔══════════════════════════════════════════════════════╗
║  RepoPilot 分析报告                                   ║
╚══════════════════════════════════════════════════════╝

📌 一句话概述
  用 Go 编写的高性能 API 网关，支持插件化中间件

🎯 项目定位
  基础设施工具 / API Gateway

📊 项目评级
  ┌──────────────┬──────────────┐
  │ 工程成熟度    │ L4 生产级    │
  │ 复刻难度      │ D3 中级级    │
  └──────────────┴──────────────┘

⭐ 综合评分: 8.2 / 10

🏗️ 技术架构
  语言: Go 1.21  |  架构: 插件化单体
  核心依赖: net/http, gRPC, etcd
  ...

✅ 项目亮点
  • 插件系统设计优雅，扩展性强
  • 完整的集成测试覆盖
  • ...

⚠️ 项目不足
  • 缺少 API 文档
  • 日志格式不统一
  • ...

💡 优化建议
  [入门开发者] 可以从补充单元测试入手...
  [中级开发者] 建议重构配置管理模块...
  [高级开发者] 可引入链路追踪和熔断机制...

👥 适合人群
  • 有 1-2 年 Go 经验的后端开发者
  • 对 API 网关/微服务感兴趣的工程师

💼 求职参考价值
  适合作为后端工程师求职作品参考，展示了...
```

---

## 五、数据库 Schema

```python
# models.py

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: int                    # 主键自增
    repo_url: str              # GitHub 仓库 URL（唯一约束）
    repo_name: str             # owner/repo（建索引）
    analyzed_at: datetime      # 分析时间（UTC）
    summary: str               # 一句话概述
    maturity_level: str        # L1-L5
    difficulty_level: str      # D1-D5
    overall_score: float       # 综合评分 0-10
    analysis_json: str         # 完整分析结果 (JSON，含 positioning/highlights/weaknesses/suggestions/target_audience/career_value/tech_stack/confidence)
    raw_response: str          # LLM 原始返回 (JSON，用于调试和回溯)
```

设计说明：只保留需要查询和排序的字段作为独立列，其余 LLM 生成内容统一存入 `analysis_json`，避免每次调整 Prompt 都要改 schema。

---

## 六、模块职责详解

### `config.py`
- 从 `.env` 加载配置：
  - `OPENAI_API_KEY` — LLM 和 Embedding 的 API 密钥
  - `OPENAI_BASE_URL` — API 代理地址（默认 `https://api.timebackward.com/v1`）
  - `OPENAI_MODEL` — Chat 模型名称（可配置，默认 `gpt-4o-mini`）
  - `OPENAI_EMBEDDING_MODEL` — Embedding 模型名称（可配置，默认 `text-embedding-3-small`）
  - `GITHUB_TOKEN` — GitHub API 访问令牌
  - `REPOPILOT_DB_PATH` — SQLite 数据库路径（默认 `database/repopilot.db`）
  - `REPOPILOT_CHROMA_PATH` — ChromaDB 持久化路径（默认 `database/chroma`）

### `utils/logger.py`
- 工厂模式：`get_logger(name)` 为每个模块创建独立 logger 实例
- 日志格式：`时间 | 日志级别 | 模块名 | 文件名:行号 | 消息`
  - 示例：`2026-04-24 16:10:32 | INFO     | repopilot.github.service | service.py:42 | 开始采集仓库`
  - 异常：`2026-04-24 16:11:20 | ERROR    | repopilot.github.service | service.py:58 | 仓库克隆失败 | error=Permission denied`
- 终端输出（stderr）+ 文件输出（`logs/` 目录）双通道
- 日志文件按模块名 + 日期命名（如 `repopilot.github.service_20260424.log`），按大小轮转（5MB，保留 3 个备份）
- 终端默认 INFO 级别，文件始终 DEBUG 级别
- 使用方式：`from repopilot.utils.logger import get_logger; logger = get_logger(__name__)`
- 五级日志使用规范：
  - `INFO` — 用户提交仓库、开始克隆、开始分析、分析完成等正常业务流程
  - `WARNING` — token 缺失、仓库过大、部分文件无法解析等非致命异常
  - `ERROR` — 克隆失败、LLM 调用失败、向量库写入失败等可恢复错误
  - `CRITICAL` — 数据库无法连接、核心配置缺失等不可恢复错误
  - `DEBUG` — prompt 内容、RAG 检索结果、工具调用参数等调试信息

### `github/service.py`
- `GithubService` — GitHub 采集服务
- URL 格式校验（支持 https://github.com/owner/repo、.git 后缀等）
- 调用 PyGithub API 采集仓库数据，返回 `RepoData`
- 边界处理：私有仓库报错提示权限不足、大文件截断保留头尾摘要
- 日志记录采集进度

### `github/schemas.py`
- `RepoData` Pydantic BaseModel，字段包括：
  - `repo_url`, `repo_name`, `owner`, `name`
  - `description`, `language`, `topics`
  - `stars`, `forks`, `open_issues`, `license`
  - `default_branch`, `tree_text`（目录结构）
  - `readme_text`（README 内容，缺失时降级为仓库描述）
  - `key_files`（关键配置文件：package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml, Dockerfile, Makefile 等）
  - `recent_commits`（最近 commit 摘要）
  - `issue_stats`, `pr_stats`

### `rag/vectorstore.py`
- `embed_repo(repo_data: RepoData) -> Collection` — 将 repo 文件内容 embedding 入库
- `query_context(collection, query: str) -> str` — 检索相关上下文
- 使用 LangChain 的 `OpenAIEmbeddings` + ChromaDB
- 每个 repo 一个 collection（以 repo 全名命名）

### `rag/service.py`
- `RagService` — RAG 业务编排
- 协调文件分块、embedding 入库、检索查询的完整流程

### `agent/analyzer.py`
- `analyze_repo(repo_data: RepoData, rag_context: str) -> AnalysisResult`
- 构建包含 repo 元数据和 RAG 上下文的 Prompt
- 使用 `ChatOpenAI` + `StrOutputParser`，要求 LLM 返回结构化 JSON
- Prompt 中内置等级定义和评分标准
- JSON 解析失败时自动重试一次，仍失败则返回简化结果（至少包含 summary 和基础评分）
- AnalysisResult 包含 `confidence` 字段（LLM 自评置信度 0-1），用于报告展示

### `agent/prompts.py`
- 分析 Prompt 模板定义
- 系统角色设定、等级定义说明、评分标准
- 输出 JSON schema 要求、字段说明

### `agent/tools.py`
- Agent 工具函数定义（可扩展）
- 为后续 Agent 能力扩展预留接口

### `analysis/grading.py`
- `grade(analysis: AnalysisResult) -> GradeResult`
- 将 LLM 返回的数值评分映射到 L1-L5 / D1-D5 等级
- 纯逻辑，不调用 LLM

### `analysis/schemas.py`
- `AnalysisResult` — LLM 分析结果数据模型（含 confidence）
- `GradeResult` — 等级映射结果（maturity_level, difficulty_level, 及对应 reason）

### `database/sqlite.py`
- SQLAlchemy ORM 模型定义（Base、AnalysisRecord）
- 数据库引擎创建、会话管理
- SQLite 文件路径：`database/repopilot.db`（项目根目录下）

### `database/chroma.py`
- ChromaDB 持久化客户端初始化
- collection 创建/获取/删除
- ChromaDB 数据路径：`database/chroma/`（项目根目录下）

### `analysis/repository.py`
- 分析记录的 CRUD 操作
- `save_analysis(result)` / `get_history()` / `get_by_repo(repo_name)`

### `analysis/service.py`
- `AnalysisService` — 核心业务编排
- 串联完整流程：fetch → embed → analyze → grade → save
- CLI 和 Web 都调用这个 service，不重复编排逻辑

### `cli/app.py`
- Typer 命令定义
- `repopilot analyze <github_url>` — 主命令
- `repopilot history` — 查看历史分析记录
- 串联整个流程：fetch → embed → analyze → grade → save → render

### `cli/report.py`
- `render_report(result: AnalysisResult, grade: GradeResult)` — Rich 终端输出
- 使用 Rich 的 Panel, Table, Markdown 组件美化输出

### `web/`（Phase 2）
- `app.py` — FastAPI 实例创建、中间件配置、挂载 static 目录
- `views.py` — 页面渲染路由：GET /（首页）、GET /report/{id}（报告页）、GET /history（历史页）
- `api.py` — REST JSON 接口：POST /api/v1/analyze、GET /api/v1/history、GET /api/v1/reports/{id}
- `templates/` — Jinja2 模板
- `static/` — CSS/JS/图片

---

## 七、开发计划

### Phase 1: CLI MVP（预计 27 小时）

#### 一、项目骨架与配置

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 1 | 创建 `src/repopilot/` 完整目录结构，所有子包的 `__init__.py` | 0.5h | `tree src/` 显示完整目录 |
| 2 | 实现 `config.py` — pydantic-settings 加载 `.env`，定义全部配置项（API Key、Base URL、模型名、DB 路径、ChromaDB 路径） | 1h | `from repopilot.config import settings` 能读取环境变量 |
| 3 | 实现 `utils/logger.py` — 五级日志规范（INFO/WARNING/ERROR/CRITICAL/DEBUG），终端 + 文件双输出，按日期轮转 | 0.5h | 日志输出格式符合预期 |
| 4 | 创建 `.env.example` 模板，包含所有必需环境变量和注释说明 | 0.5h | 文件内容完整 |
| 5 | 更新 `pyproject.toml` — 入口点改为 `src/repopilot`，script 指向 `repopilot.cli.app:app` | 0.5h | `repopilot --help` 正常显示 |

#### 二、GitHub 数据采集

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 6 | 定义 `github/schemas.py` — `RepoData` Pydantic BaseModel 全部字段 | 0.5h | 类型定义完整，可实例化 |
| 7 | 实现 `github/service.py` — URL 格式校验 + 获取 repo 元数据（stars、forks、language、topics、license、description） | 1h | 打印元数据 JSON |
| 8 | 实现 `github/service.py` — 获取目录结构树 | 0.5h | 打印目录树文本 |
| 9 | 实现 `github/service.py` — 获取 README 内容 | 0.5h | 打印 README 文本 |
| 10 | 实现 `github/service.py` — 获取关键配置文件内容（package.json、requirements.txt、pyproject.toml、Dockerfile 等） | 0.5h | 打印关键文件内容 |
| 11 | 实现 `github/service.py` — 获取最近 commits 摘要和 issue/PR 统计 | 0.5h | 打印 commit 和 issue 数据 |
| 12 | 实现 `github/service.py` — 边界处理：私有仓库权限报错、大文件截断、README 缺失降级 | 0.5h | 异常场景有友好提示 |

#### 三、向量存储与 RAG

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 14 | 实现 `rag/vectorstore.py` — 初始化 ChromaDB 客户端，创建/获取 collection（以 repo 全名命名） | 0.5h | `database/chroma/` 数据目录生成 |
| 15 | 实现 `rag/vectorstore.py` — `embed_repo()` 将 README + 关键文件分块后 embedding 入库 | 1h | 日志显示 `INFO:httpx:HTTP Request: POST .../embeddings "HTTP/1.1 200 OK"` |
| 16 | 实现 `rag/vectorstore.py` — `query_context()` 根据查询检索相关上下文片段 | 0.5h | 输入查询返回相关文本 |
| 17 | 实现 `rag/service.py` — 编排分块、入库、查询完整流程，日志记录跳过/新增状态 | 1h | 日志显示 `⏭️ 跳过` 和 `📥 获取` |

#### 四、LLM 分析核心

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 18 | 定义 `analysis/schemas.py` — `AnalysisResult` 数据模型（含 confidence 字段）和 `GradeResult` 数据模型 | 0.5h | 类型定义完整，可实例化 |
| 19 | 设计 `agent/prompts.py` — 系统角色设定、等级定义说明、评分标准 | 1h | Prompt 文本完成 |
| 20 | 设计 `agent/prompts.py` — 输出 JSON schema 要求、字段说明、示例 | 1h | 手动测试 LLM 返回格式正确 |
| 21 | 实现 `agent/analyzer.py` — `ChatOpenAI` 初始化 + LangChain Chain 构建 | 1h | Chain 可调用，不报错 |
| 22 | 实现 `agent/analyzer.py` — LLM 返回 JSON 解析逻辑 | 0.5h | 调用 LLM 返回可解析的 AnalysisResult |
| 23 | 实现 `agent/analyzer.py` — JSON 解析失败重试一次，仍失败返回简化结果兜底 | 0.5h | 模拟解析失败时返回简化结果 |
| 24 | 实现 `analysis/grading.py` — 数值评分映射到 L1-L5 / D1-D5 等级的纯函数 | 0.5h | 输入评分返回正确等级和 reason |
| 25 | 实现 `analysis/service.py` — 串联 fetch → embed → analyze → grade 完整流程 | 1h | 输入 URL 返回完整 AnalysisResult + GradeResult |

#### 五、数据库持久化

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 26 | 实现 `database/sqlite.py` — Base 定义、AnalysisRecord ORM 模型、引擎创建、会话管理、启动时自动建表 | 1h | 启动时自动创建 `database/repopilot.db` |
| 27 | 实现 `database/chroma.py` — ChromaDB 客户端初始化、collection 创建/获取/删除 | 0.5h | `database/chroma/` 数据目录生成 |
| 28 | 实现 `analysis/repository.py` — `save_analysis()` 将分析结果写入数据库 | 0.5h | 分析结果成功写入 |
| 29 | 实现 `analysis/repository.py` — `get_history()` 查询所有历史记录 | 0.5h | 返回正确记录列表 |
| 30 | 实现 `analysis/repository.py` — `get_by_repo()` 按仓库名查询 | 0.5h | 返回对应记录 |
| 31 | 更新 `analysis/service.py` — 分析完成后自动调用 repository 持久化 | 0.5h | 端到端流程后数据库有记录 |

#### 六、终端报告渲染与 CLI 串联

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 32 | 实现 `cli/report.py` — 报告头部渲染（标题 Panel、一句话概述、项目定位） | 0.5h | Rich Panel 输出正确 |
| 33 | 实现 `cli/report.py` — 评级表格渲染（工程成熟度 + 复刻难度 + 综合评分） | 0.5h | Rich Table 输出正确 |
| 34 | 实现 `cli/report.py` — 技术架构区块渲染 | 0.5h | 技术栈信息展示正确 |
| 35 | 实现 `cli/report.py` — 亮点和不足区块渲染 | 0.5h | 列表展示正确 |
| 36 | 实现 `cli/report.py` — 优化建议区块渲染（按开发者水平分层） | 0.5h | 分层建议展示正确 |
| 37 | 实现 `cli/report.py` — 适合人群和求职参考价值区块渲染 | 0.5h | 内容展示正确 |
| 38 | 实现 `cli/app.py` — `analyze` 命令，调用 AnalysisService 后调用 render_report | 1h | `repopilot analyze <url>` 输出完整报告 |
| 39 | 实现 `cli/app.py` — `history` 命令，调用 repository 查询并用 Rich Table 展示列表 | 0.5h | `repopilot history` 显示历史记录 |
| 40 | 实现 `main.py` — 统一入口分发（CLI / Web） | 0.5h | 入口正常工作 |

#### 七、集成测试与打磨

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 41 | 端到端测试 — 小型 Python 项目（如 httpie） | 0.5h | 完整报告输出，等级合理 |
| 42 | 端到端测试 — 大型项目（如 fastapi） | 0.5h | 大文件截断正常，不超时 |
| 43 | 端到端测试 — 非 Python 项目（如 Go/JS 项目） | 0.5h | 技术栈识别正确 |
| 44 | Prompt 调优 — 根据测试结果优化分析质量和评分准确度 | 1h | 多个 repo 评级结果合理 |
| 45 | 日志完善 — 检查全流程日志输出格式一致性 | 0.5h | 日志格式统一，关键节点有记录 |
| 46 | 错误处理完善 — API 限流友好提示、网络超时重试、无效 URL 报错 | 0.5h | 异常场景有清晰提示 |
| 47 | README 编写 — 项目说明、安装步骤、使用示例、技术栈说明 | 0.5h | README 完整可读 |

### Phase 2: Web 版本（预计 15 小时）

#### 八、FastAPI 后端

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 48 | 实现 `web/app.py` — FastAPI 实例创建、CORS 中间件配置 | 0.5h | 服务启动无报错 |
| 49 | 实现 `web/app.py` — 挂载 static 目录、配置 Jinja2 模板引擎 | 0.5h | 静态文件可访问 |
| 50 | 实现 `web/api.py` — `POST /api/v1/analyze` 接口，调用 AnalysisService | 1.5h | curl 调用返回 JSON 分析结果 |
| 51 | 实现 `web/api.py` — `GET /api/v1/history` 接口 | 0.5h | curl 查询返回历史列表 |
| 52 | 实现 `web/api.py` — `GET /api/v1/reports/{id}` 接口 | 0.5h | curl 查询返回单条记录 |
| 53 | 异步改造 — aiosqlite 异步数据库操作 | 1h | 并发请求不阻塞 |
| 54 | 更新 `main.py` — 添加 `repopilot web` 启动入口 | 0.5h | 命令启动 uvicorn 服务 |

#### 九、Jinja2 前端页面

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 55 | 实现 `web/templates/base.html` — 基础 HTML 布局、导航栏 | 0.5h | 页面骨架渲染正确 |
| 56 | 实现 `web/static/` — 基础 CSS 样式文件 | 1h | 页面样式整洁可读 |
| 57 | 实现 `web/templates/index.html` — 首页输入表单、提交逻辑 | 1h | 输入 URL 可提交 |
| 58 | 实现 `web/templates/report.html` — 分析报告展示页面（评级、亮点、不足等区块） | 2h | 报告各区块展示完整 |
| 59 | 实现 `web/views.py` — 页面渲染路由（GET /、GET /report/{id}、GET /history） | 1h | 浏览器访问各页面正常 |

#### 十、异步优化与进度展示

| Step | 任务 | 预计 | 验证方式 |
|------|------|------|----------|
| 60 | 分析任务改为后台执行 — BackgroundTasks 或 asyncio.create_task | 1h | 提交后立即返回，不阻塞页面 |
| 61 | SSE 进度推送 — 分析各阶段（采集中→向量化中→分析中→完成）实时推送 | 1.5h | 页面实时显示进度状态 |
| 62 | 前端进度条 — JavaScript 监听 SSE 事件更新页面 | 1h | 进度条动态更新 |
| 63 | 端到端测试 — 浏览器完整流程测试（输入→等待→报告） | 0.5h | 全流程通畅 |

---

## 八、关键文件清单

实现时需要创建/修改的文件：

| 文件 | 说明 |
|------|------|
| `src/repopilot/__init__.py` | 包标识 |
| `src/repopilot/main.py` | 统一入口分发 |
| `src/repopilot/config.py` | 配置管理 |
| `src/repopilot/utils/__init__.py` | 工具函数包 |
| `src/repopilot/utils/logger.py` | 日志配置（输出到 logs/ 目录 + 终端） |
| `src/repopilot/github/__init__.py` | GitHub 采集包 |
| `src/repopilot/github/schemas.py` | RepoData 数据模型 |
| `src/repopilot/github/service.py` | GitHub 采集服务（URL 校验 + 数据采集 + 日志） |
| `src/repopilot/rag/__init__.py` | RAG 包 |
| `src/repopilot/rag/vectorstore.py` | ChromaDB embedding + 检索 |
| `src/repopilot/rag/service.py` | RAG 业务编排 |
| `src/repopilot/agent/__init__.py` | Agent 编排包 |
| `src/repopilot/agent/analyzer.py` | LangChain 分析链 |
| `src/repopilot/agent/prompts.py` | Prompt 模板定义 |
| `src/repopilot/agent/tools.py` | Agent 工具函数（可扩展） |
| `src/repopilot/analysis/__init__.py` | 分析包 |
| `src/repopilot/analysis/grading.py` | 等级映射 |
| `src/repopilot/analysis/schemas.py` | AnalysisResult, GradeResult |
| `src/repopilot/analysis/repository.py` | 分析记录 CRUD 操作 |
| `src/repopilot/analysis/service.py` | 分析业务编排 |
| `src/repopilot/database/__init__.py` | 数据库基础设施包 |
| `src/repopilot/database/sqlite.py` | SQLite ORM 模型、引擎、会话管理 |
| `src/repopilot/database/chroma.py` | ChromaDB 客户端初始化、collection 管理 |
| `src/repopilot/cli/__init__.py` | CLI 包 |
| `src/repopilot/cli/app.py` | Typer 命令定义 |
| `src/repopilot/cli/report.py` | Rich 终端渲染 |
| `.env.example` | 环境变量模板 |
| `pyproject.toml` | 更新入口点和包路径配置 |
