from typing import Any

from langchain_core.tools import tool

from repopilot.github.schemas import RepoData
from repopilot.rag.service import RagService
from repopilot.utils.logger import get_logger
from repopilot.utils.path_tool import get_module_name

logger = get_logger(name=get_module_name(__file__))


class AnalysisTools:
    def __init__(self, repo_data: RepoData, rag_service: RagService) -> None:
        self._repo_data = repo_data
        self._rag_service = rag_service

    def get_tools(self) -> list:
        repo_data = self._repo_data
        rag_service = self._rag_service

        @tool
        def get_repo_overview() -> dict[str, Any]:
            """获取仓库元数据概览，包括描述、语言、stars、forks、topics、license、open issues。"""
            logger.info(f"Tool 调用: get_repo_overview | {repo_data.repo_name}")
            return {
                "repo_name": repo_data.repo_name,
                "description": repo_data.description,
                "language": repo_data.language,
                "topics": repo_data.topics,
                "stars": repo_data.stars,
                "forks": repo_data.forks,
                "open_issues": repo_data.open_issues,
                "license": repo_data.license,
            }

        @tool
        def get_directory_structure() -> str:
            """获取仓库目录结构树。"""
            logger.info(f"Tool 调用: get_directory_structure | {repo_data.repo_name}")
            return repo_data.tree_text

        @tool
        def get_readme() -> str:
            """获取仓库 README 内容。"""
            logger.info(f"Tool 调用: get_readme | {repo_data.repo_name}")
            return repo_data.readme_text

        @tool
        def get_key_files() -> dict[str, str]:
            """获取关键配置文件内容，如 pyproject.toml、requirements.txt、Dockerfile 等。"""
            logger.info(f"Tool 调用: get_key_files | {repo_data.repo_name}")
            return repo_data.key_files

        @tool
        def get_recent_commits() -> list[str]:
            """获取最近提交摘要列表。"""
            logger.info(f"Tool 调用: get_recent_commits | {repo_data.repo_name}")
            return repo_data.recent_commits

        @tool
        def get_issue_pr_stats() -> dict[str, Any]:
            """获取 Issue 和 PR 统计信息。"""
            logger.info(f"Tool 调用: get_issue_pr_stats | {repo_data.repo_name}")
            return {
                "issues": repo_data.issue_stats,
                "prs": repo_data.pr_stats,
            }

        @tool
        def search_code(query: str) -> str:
            """根据查询语义检索相关代码/文档片段。适合查询架构、测试、CI/CD、错误处理、亮点等。"""
            logger.info(f"Tool 调用: search_code | {repo_data.repo_name} | query={query}")
            return rag_service.query(repo_data.repo_name, query, n_results=5)

        return [
            get_repo_overview,
            get_directory_structure,
            get_readme,
            get_key_files,
            get_recent_commits,
            get_issue_pr_stats,
            search_code,
        ]
