# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RepoPilot is a GitHub repository intelligent analysis assistant. It evaluates repos across two dimensions — engineering maturity (L1-L5) and replication difficulty (D1-D5) — and outputs structured reports with scoring, highlights, weaknesses, and optimization suggestions for different skill levels.

Tech stack: LangChain + ChromaDB (RAG) + PyGithub + SQLAlchemy/SQLite + Typer/Rich (CLI) + FastAPI/Jinja2 (Web, Phase 2). LLM via OpenAI-compatible proxy at `api.timebackward.com`.

## Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run repopilot analyze <github_url>
uv run repopilot history

# Run web server (Phase 2)
uv run repopilot web
```

## Architecture

Uses `src/repopilot/` layout with domain-based packaging:

- `github/` — PyGithub data fetching (fetcher.py, schemas.py, service.py)
- `rag/` — ChromaDB embedding + retrieval (vectorstore.py, service.py)
- `analysis/` — LangChain analysis chain, grading, CRUD (analyzer.py, grading.py, schemas.py, repository.py, service.py)
- `database/` — Infrastructure only: ORM models + session management (models.py, session.py). CRUD lives in domain packages.
- `cli/` — Typer commands + Rich terminal rendering (app.py, report.py)
- `web/` — Phase 2: FastAPI + Jinja2 in one package (app.py, views.py, api.py, templates/, static/)

Key data flow: `cli/app.py` → `analysis/service.py` (orchestrator) → `github/service.py` → `rag/service.py` → `analysis/analyzer.py` → `analysis/grading.py` → `analysis/repository.py` → `cli/report.py`

`analysis/service.py` is the core orchestrator — both CLI and Web call it. Entry layers (`cli/`, `web/`) never contain business logic.

## Configuration

All config via environment variables loaded by pydantic-settings in `config.py`:
- `OPENAI_API_KEY`, `OPENAI_BASE_URL` (default: `https://api.timebackward.com/v1`)
- `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`
- `GITHUB_TOKEN`
- `REPOPILOT_DB_PATH` (default: `database/repopilot.db`), `REPOPILOT_CHROMA_PATH` (default: `database/chroma`)

## Logging Convention

Business logs use emoji prefixes: `⏭️ 跳过`, `✅ 完成`, `📥 获取`. Format: `INFO:module_name:message`. httpx logs are auto-captured for LLM/embedding HTTP requests.

## Design Doc

Full spec at `docs/design.md` — grading system, DB schema, report format, 63-step development plan.
