import json
import re

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from repopilot.agent.prompts import SYSTEM_PROMPT
from repopilot.agent.tools import AnalysisTools
from repopilot.analysis.schemas import AnalysisResult
from repopilot.config import settings
from repopilot.github.schemas import RepoData
from repopilot.rag.service import RagService
from repopilot.utils.logger import get_logger
from repopilot.utils.path_tool import get_module_name

logger = get_logger(name=get_module_name(__file__))

_TOOL_CALLING_PROMPT = """你的任务是分析这个 GitHub 仓库。

要求：
1. 先主动调用工具收集证据，不要直接猜测。
2. 至少检查：仓库概览、目录结构、README、最近提交、Issue/PR 统计。
3. 如果需要判断代码质量、测试、CI/CD、错误处理、模块实现情况，调用 search_code。
4. 收集完信息后，严格输出 JSON，不要输出任何额外解释文字。"""


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
        temperature=0.3,
    )


def _parse_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    raw = match.group(1) if match else text
    return json.loads(raw.strip())


def _fallback_result(repo_data: RepoData) -> AnalysisResult:
    return AnalysisResult(
        summary=repo_data.description or repo_data.repo_name,
        confidence=0.1,
    )


def analyze_repo(repo_data: RepoData, rag_service: RagService) -> AnalysisResult:
    tools = AnalysisTools(repo_data, rag_service).get_tools()
    llm = _build_llm()
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

    messages = [
        HumanMessage(
            content=(
                f"{_TOOL_CALLING_PROMPT}\n\n"
                f"仓库名称: {repo_data.repo_name}\n"
                f"仓库描述: {repo_data.description or '无'}"
            )
        ),
    ]

    for attempt in range(2):
        try:
            response = agent.invoke({"messages": messages})
            final_message = response["messages"][-1]
            data = _parse_json(final_message.content)
            result = AnalysisResult(**data)
            logger.info(
                f"LangGraph Agent 分析完成: {repo_data.repo_name} (attempt {attempt + 1})"
            )
            return result
        except Exception as e:
            logger.warning(f"LangGraph Agent 解析失败 (attempt {attempt + 1}): {e}")

    logger.error(f"LangGraph Agent 分析失败，返回兜底结果: {repo_data.repo_name}")
    return _fallback_result(repo_data)
