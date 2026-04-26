# RepoPilot

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![CLI](https://img.shields.io/badge/Interface-CLI-4EAA25)](#运行方式)
[![Agent](https://img.shields.io/badge/Agent-Tool--Calling-7B61FF)](#当前具备能力)
[![RAG](https://img.shields.io/badge/RAG-ChromaDB-FF6F00)](#当前具备能力)
[![Database](https://img.shields.io/badge/Database-SQLite%20%2B%20ChromaDB-0F6CBD)](#项目结构)
[![License](https://img.shields.io/badge/License-MIT-2EA44F)](#许可证)

一个面向 GitHub 仓库的智能分析助手，用来快速判断一个开源项目的价值、难度和成熟度。

它会抓取仓库元数据、README、关键配置文件、提交与 Issue/PR 统计，再结合 RAG 检索和 LLM Agent，输出结构化分析报告。

当前项目已实现 **Phase 1: CLI MVP**，可以在终端直接分析公开 GitHub 仓库，并将结果持久化到本地 SQLite。

## 快速开始

```bash
uv sync
uv run repopilot analyze https://github.com/owner/repo
uv run repopilot history
```

输入一个公开 GitHub 仓库地址后，当前版本会输出：

- 一句话概述
- 项目定位
- 工程成熟度（L1-L5）
- 复刻难度（D1-D5）
- 综合评分（0-10）
- 项目亮点 / 不足 / 建议

## 终端输出示例

```text
$ uv run repopilot analyze https://github.com/tiangolo/fastapi

正在分析: https://github.com/tiangolo/fastapi
...
╔═════════════════════════════════════════════════════════════════════════════╗
║ RepoPilot 分析报告                                                          ║
╚═════════════════════════════════════════════════════════════════════════════╝

一句话概述
  一个成熟的 Python Web 框架，围绕类型提示、自动文档和高性能 API 开发构建。

项目定位
  Web 框架 / API 开发基础设施

项目评级
  工程成熟度   L4 L4 Production/生产级
  复刻难度     D4 D4 Senior/资深级
  综合评分     8.4 / 10

技术架构
  语言: Python  |  架构: 模块化框架
  核心依赖: Starlette, Pydantic, Uvicorn

项目亮点
  • 类型提示驱动接口设计，减少重复定义，提高开发效率
  • 自动 OpenAPI 文档生成，降低接口维护成本
  • 框架边界清晰，扩展性和生态成熟度较高

项目不足
  • 依赖栈较深，初学者理解成本偏高
  • 过度依赖自动机制时，复杂场景调试门槛会上升
  • 在大型项目中仍需要额外约束工程规范，否则容易出现使用风格不统一的问题
```

## 目录

- [项目特点](#项目特点)
- [项目定位](#项目定位)
- [当前具备能力](#当前具备能力)
- [等级体系设计](#等级体系设计)
- [分析报告输出内容](#分析报告输出内容)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [核心数据流](#核心数据流)
- [环境要求](#环境要求)
- [安装](#安装)
- [配置](#配置)
- [运行方式](#运行方式)
- [日志说明](#日志说明)
- [许可证](#许可证)

---

## 项目特点

这个项目关注的不是单次问答，而是把 GitHub 仓库分析这件事拆成一条完整链路：数据采集、RAG 检索、Agent 分析、评分映射、结果持久化和 CLI 输出。

当前版本的特点主要有：

- **模块职责清晰**：GitHub 采集、RAG、Agent、评分、持久化、CLI 分开组织，方便后续继续扩展
- **分析过程可追踪**：Agent 使用 tool-calling 模式，工具调用过程会写入日志，便于观察它实际查了哪些证据
- **结果不是纯文本摘要**：会输出项目定位、亮点、不足、建议、成熟度、复刻难度和综合评分
- **本地可运行**：分析结果会写入 SQLite，向量数据会写入 ChromaDB，可以直接在终端里反复使用
- **更偏工程化实现**：相比只做 Prompt demo，这个版本更强调完整流程能否跑通

---

## 项目定位

这个项目更偏向一个 **开发者工具 / AI 分析助手**，适合用于：

- 快速了解一个 GitHub 仓库值不值得读
- 判断项目的工程成熟度是否足够高
- 评估复刻或学习该项目的难度

---

## 当前具备能力

### 1. GitHub 仓库采集

已实现：

- GitHub URL 解析
- 仓库基础元数据采集
  - owner/repo
  - description
  - language
  - topics
  - stars / forks / open issues
  - license
- 目录结构树获取
- README 内容获取
- 关键配置文件获取
- 最近提交摘要获取
- Issue / PR 统计获取

### 2. RAG 检索增强

已实现：

- README 与关键文件分块
- Embedding 写入本地 ChromaDB
- 基于语义查询检索相关上下文
- 为分析 Agent 提供代码与文档证据

### 3. Tool-calling Agent 分析

已实现：

- 使用 `langchain.agents.create_agent` 构建分析 Agent
- Agent 主动调用工具获取：
  - 仓库概览
  - 目录结构
  - README
  - 关键文件
  - 最近提交
  - Issue / PR 统计
  - RAG 检索结果
- 输出结构化 JSON 分析结果
- 每个工具调用都有日志，便于观察 Agent 的执行路径

### 4. 评分与持久化

已实现：

- 工程成熟度评级：L1-L5
- 复刻难度评级：D1-D5
- 综合评分：0-10
- 结果写入本地 SQLite
- 相同仓库重复分析时执行更新而不是重复插入

### 5. CLI 报告输出

已实现：

- `repopilot analyze <url>` 分析仓库
- `repopilot history` 查看历史记录
- Rich 美化终端报告输出
- Windows 终端 UTF-8 输出兼容处理

---

## 等级体系设计

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
| D1 | Beginner | 入门级 | 单一技术栈，几乎没有理解门槛 |
| D2 | Junior | 进阶级 | 需要熟悉框架和常见设计模式 |
| D3 | Intermediate | 实战级 | 需要扎实工程经验和系统设计能力 |
| D4 | Senior | 资深级 | 需要深入领域知识或复杂系统经验 |
| D5 | Expert | 专家级 | 需要稀缺专业技能 |

### 当前评分依据

当前评分由 Agent 结合 Prompt 规则进行综合判断，重点参考：

**成熟度评估依据：**
- 提交数量与项目阶段
- 代码组织结构
- 依赖管理与 lock 文件
- 文档完整度
- 测试覆盖
- CI/CD 配置
- 错误处理与日志
- 类型注解
- 核心模块是否是空壳实现

**复刻难度评估依据：**
- 技术栈复杂度
- 外部依赖与服务数量
- 代码规模
- 架构复杂度
- 领域知识门槛

说明：当前评分已经加入较严格的约束，但它仍然属于 **LLM + 规则约束** 的分析方式，不是纯静态分析器，因此更适合作为项目评估参考。

---

## 分析报告输出内容

当前 CLI 会输出以下结构化结果：

- 一句话概述
- 项目定位
- 工程成熟度等级
- 复刻难度等级
- 综合评分
- 技术架构
- 项目亮点（至少 3 条）
- 项目不足（至少 3 条）
- 分层优化建议
- 适合人群
- 求职参考价值

---

## 技术栈

- Python 3.12+
- Typer
- Rich
- PyGithub
- LangChain
- LangChain OpenAI
- ChromaDB
- SQLAlchemy 2.0
- aiosqlite
- Pydantic Settings
- FastAPI（依赖已接入）
- Jinja2（依赖已接入）
- uv

---

## 项目结构

```text
src/repopilot/
├── __init__.py
├── main.py
├── config.py
│
├── utils/
│   ├── __init__.py
│   └── logger.py
│
├── github/
│   ├── __init__.py
│   ├── schemas.py
│   └── service.py
│
├── rag/
│   ├── __init__.py
│   ├── vectorstore.py
│   └── service.py
│
├── agent/
│   ├── __init__.py
│   ├── analysis_agent.py
│   ├── prompts.py
│   └── tools.py
│
├── analysis/
│   ├── __init__.py
│   ├── grading.py
│   ├── models.py
│   ├── repository.py
│   ├── schemas.py
│   └── service.py
│
├── database/
│   ├── __init__.py
│   ├── sqlite.py
│   └── chroma.py
│
└── cli/
    ├── __init__.py
    ├── app.py
    └── report.py
```

运行时目录：

```text
database/
├── repopilot.db
└── chroma/

logs/
```

---

## 核心数据流

```text
用户输入 GitHub URL
       │
       ▼
GitHub Service
  ├─ 获取元数据
  ├─ 获取目录树
  ├─ 获取 README
  ├─ 获取关键文件
  ├─ 获取 commits
  └─ 获取 Issue/PR 统计
       │
       ▼
RAG VectorStore
  ├─ 文本分块
  ├─ Embedding
  └─ 写入 ChromaDB
       │
       ▼
Analysis Agent
  ├─ 主动调用 tools
  ├─ 调用 RAG 检索补证据
  └─ 输出结构化 JSON
       │
       ▼
Grading
  ├─ 映射 L1-L5
  └─ 映射 D1-D5
       │
       ▼
Repository
  └─ 持久化到 SQLite
       │
       ▼
CLI Report
  └─ Rich 终端渲染
```

---

## 环境要求

- Python >= 3.12
- GitHub Token
- OpenAI 兼容模型接口
- OpenAI 兼容 Embedding 接口
- uv

---

## 安装

```bash
uv sync
```

---

## 配置

在项目根目录创建 `.env` 文件。

示例：

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
REPOPILOT_DB_PATH=database/repopilot.db
REPOPILOT_CHROMA_PATH=database/chroma
```

### 配置说明

- `OPENAI_API_KEY`：LLM / Embedding API Key
- `OPENAI_BASE_URL`：OpenAI 兼容接口地址
- `OPENAI_MODEL`：聊天模型名
- `OPENAI_EMBEDDING_MODEL`：Embedding 模型名
- `GITHUB_TOKEN`：GitHub API Token，建议配置，否则容易触发限流
- `REPOPILOT_DB_PATH`：SQLite 数据库路径
- `REPOPILOT_CHROMA_PATH`：ChromaDB 持久化路径

---

## 运行方式

### 1. 查看帮助

```bash
uv run repopilot --help
```

### 2. 分析一个仓库

```bash
uv run repopilot analyze https://github.com/owner/repo
```

例如：

```bash
uv run repopilot analyze https://github.com/tiangolo/fastapi
```

### 3. 查看历史分析记录

```bash
uv run repopilot history
```

---

## 当前终端运行示例

```bash
uv sync
uv run repopilot analyze https://github.com/tiangolo/fastapi
uv run repopilot history
```

---

## 日志说明

项目运行时会输出以下日志：

- GitHub 采集日志
- RAG 向量化日志
- Agent 工具调用日志
- 分析完成日志

tool-calling 阶段日志示例：

```text
🔧 Tool 调用: get_repo_overview | owner/repo
🔧 Tool 调用: get_directory_structure | owner/repo
🔧 Tool 调用: search_code | owner/repo | query=tests pytest unittest
```

这些日志可以帮助观察 Agent 实际调用了哪些工具，以及分析证据来自哪里。

---

## 许可证

MIT License
