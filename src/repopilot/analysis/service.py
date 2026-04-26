import asyncio

from repopilot.agent.analysis_agent import analyze_repo
from repopilot.analysis.grading import grade
from repopilot.analysis.models import AnalysisRecord
from repopilot.analysis.repository import AnalysisRepository
from repopilot.analysis.schemas import AnalysisResult, GradeResult
from repopilot.github.schemas import RepoData
from repopilot.github.service import GithubService
from repopilot.rag.service import RagService
from repopilot.utils.logger import get_logger
from repopilot.utils.path_tool import get_module_name

logger = get_logger(name=get_module_name(__file__))

class AnalysisService:
    def __init__(self) -> None:
        self._github = GithubService()
        self._rag = RagService()
        self._repo = AnalysisRepository()

    def analyze(self, url: str) -> tuple[AnalysisResult, GradeResult, AnalysisRecord]:
        repo_data: RepoData = self._github.fetch(url)

        self._rag.embed(repo_data)
        result = analyze_repo(repo_data, self._rag)
        grade_result = grade(result)

        record = asyncio.run(
            self._repo.save(url, repo_data.repo_name, result, grade_result)
        )

        logger.info(f"分析完成: {repo_data.repo_name} | {grade_result.maturity_level} {grade_result.difficulty_level} | {result.overall_score}/10")
        return result, grade_result, record
