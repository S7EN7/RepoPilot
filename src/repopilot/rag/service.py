from repopilot.github.schemas import RepoData
from repopilot.rag.vectorstore import embed_repo, query_context
from repopilot.utils.logger import get_logger
from repopilot.utils.path_tool import get_module_name

logger = get_logger(name=get_module_name(__file__))


class RagService:
    def embed(self, repo_data: RepoData) -> str:
        logger.info(f"开始 embedding: {repo_data.repo_name}")
        col_name = embed_repo(repo_data)
        logger.info(f"embedding 完成: {col_name}")
        return col_name

    def query(self, repo_name: str, query: str, n_results: int = 5) -> str:
        return query_context(repo_name, query, n_results)
