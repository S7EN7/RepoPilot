import json
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from repopilot.agent.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT
from repopilot.analysis.schemas import AnalysisResult
from repopilot.config import settings
from repopilot.github.schemas import RepoData
from repopilot.utils.logger import get_logger
from repopilot.utils.path_tool import get_module_name

logger = get_logger(name=get_module_name(__file__))


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
        temperature=0.2,
    )


def _parse_json(text: str) -> dict:
    # 提取 ```json ... ``` 代码块，或直接解析
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    raw = match.group(1) if match else text
    return json.loads(raw.strip())


def _fallback_result(repo_data: RepoData) -> AnalysisResult:
    return AnalysisResult(
        summary=repo_data.description or repo_data.repo_name,
        confidence=0.1,
    )


def analyze_repo(repo_data: RepoData, rag_context: str) -> AnalysisResult:
    llm = _build_llm()

    issue_pr_stats = (
        f"Issues: {repo_data.issue_stats} | PRs: {repo_data.pr_stats}"
    )
    user_content = ANALYSIS_PROMPT.format(
        repo_name=repo_data.repo_name,
        description=repo_data.description,
        language=repo_data.language,
        stars=repo_data.stars,
        forks=repo_data.forks,
        open_issues=repo_data.open_issues,
        license=repo_data.license,
        topics=", ".join(repo_data.topics),
        tree_text=repo_data.tree_text[:3000] if repo_data.tree_text else "",
        recent_commits="\n".join(repo_data.recent_commits[:10]),
        issue_pr_stats=issue_pr_stats,
        rag_context=rag_context[:4000] if rag_context else "无",
    )

    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_content)]

    for attempt in range(2):
        try:
            response = llm.invoke(messages)
            data = _parse_json(response.content)
            result = AnalysisResult(**data)
            logger.info(f"LLM 分析完成: {repo_data.repo_name} (attempt {attempt + 1})")
            return result
        except Exception as e:
            logger.warning(f"解析失败 (attempt {attempt + 1}): {e}")

    logger.error(f"LLM 分析失败，返回兜底结果: {repo_data.repo_name}")
    return _fallback_result(repo_data)
