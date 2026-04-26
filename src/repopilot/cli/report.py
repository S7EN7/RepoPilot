import re

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from repopilot.analysis.schemas import AnalysisResult, GradeResult

console = Console(width=110)

TEXT_WIDTH = 100


def _cell_width(char: str) -> int:
    if "\u4e00" <= char <= "\u9fff":
        return 2
    if "\u3040" <= char <= "\u30ff":
        return 2
    if "\uff00" <= char <= "\uffef":
        return 2
    return 1


def _wrap_line(text: str, width: int = TEXT_WIDTH, indent: str = "") -> str:
    lines = []
    current = ""
    current_width = 0
    indent_width = sum(_cell_width(c) for c in indent)

    for char in text:
        char_width = _cell_width(char)
        limit = width if not lines else width - indent_width

        if current and current_width + char_width > limit:
            lines.append(current.rstrip())
            current = indent + char
            current_width = indent_width + char_width
        else:
            current += char
            current_width += char_width

    if current:
        lines.append(current.rstrip())

    return "\n".join(lines)


def _wrap_text(text: str, width: int = TEXT_WIDTH, indent: str = "") -> str:
    return "\n".join(
        _wrap_line(line, width, indent) if line.strip() else ""
        for line in str(text).splitlines()
    )


def _clean_prefix(text: str) -> str:
    text = re.sub(r"^(亮点|不足)\s*\d+\s*[:：]\s*", "", text)
    text = re.sub(r"^[•\-\*]\s*", "", text)
    return text.strip()


def _panel(content, title: str, border_style: str = "cyan") -> Panel:
    return Panel(
        content,
        title=f"[bold]{title}[/bold]",
        title_align="left",
        border_style=border_style,
        padding=(1, 2),
    )


def _bullets(items: list[str], bullet_color: str = "cyan") -> Group:
    lines = []
    for item in items:
        clean = _clean_prefix(item)
        t = Text(overflow="fold")
        t.append(f"  ▸ ", style=bullet_color)
        t.append(_wrap_text(clean, TEXT_WIDTH - 4, "    "))
        lines.append(t)
    return Group(*lines)


def render_report(result: AnalysisResult, grade: GradeResult, repo_name: str) -> None:
    console.print()
    console.print(_panel(
        Text(f" {repo_name}", style="bold white"),
        "RepoPilot 分析报告",
        "cyan",
    ))

    summary_text = Text(overflow="fold")
    summary_text.append(f"  {_wrap_text(result.summary, TEXT_WIDTH, '  ')}\n")
    summary_text.append(
        f"  {_wrap_text('定位: ' + result.positioning, TEXT_WIDTH, '  ')}",
        style="dim",
    )
    console.print(_panel(summary_text, "概述", "cyan"))

    grade_table = Table(show_header=False, box=None, pad_edge=False, padding=(0, 2))
    grade_table.add_column(style="bold", no_wrap=True, width=12)
    grade_table.add_column()
    grade_table.add_row("工程成熟度", f"[green]{grade.maturity_level}  {grade.maturity_name}[/green]")
    grade_table.add_row("复刻难度", f"[yellow]{grade.difficulty_level}  {grade.difficulty_name}[/yellow]")
    grade_table.add_row("综合评分", f"[bold]{result.overall_score:.1f} / 10[/bold]")
    console.print(_panel(grade_table, "评级", "magenta"))

    ts = result.tech_stack
    tech = Text(overflow="fold")
    tech.append(f"  {_wrap_text('语言: ' + (ts.language or '未知'), TEXT_WIDTH, '  ')}\n")
    tech.append(f"  {_wrap_text('架构: ' + (ts.architecture or '未知'), TEXT_WIDTH, '  ')}\n")
    if ts.core_deps:
        tech.append(
            f"  {_wrap_text('核心依赖: ' + ', '.join(ts.core_deps), TEXT_WIDTH, '  ')}",
            style="dim",
        )
    console.print(_panel(tech, "技术架构", "green"))

    if result.highlights:
        console.print(_panel(_bullets(result.highlights, "green"), "项目亮点", "green"))

    if result.weaknesses:
        console.print(_panel(_bullets(result.weaknesses, "yellow"), "项目不足", "yellow"))

    suggestions = Text(overflow="fold")
    if result.suggestions.beginner:
        suggestions.append(f"  [入门] ", style="dim")
        suggestions.append(f"{_wrap_text(result.suggestions.beginner, TEXT_WIDTH - 9, '         ')}\n")
    if result.suggestions.intermediate:
        suggestions.append(f"  [中级] ", style="dim")
        suggestions.append(f"{_wrap_text(result.suggestions.intermediate, TEXT_WIDTH - 9, '         ')}\n")
    if result.suggestions.senior:
        suggestions.append(f"  [高级] ", style="dim")
        suggestions.append(f"{_wrap_text(result.suggestions.senior, TEXT_WIDTH - 9, '         ')}")
    console.print(_panel(suggestions, "优化建议", "blue"))

    if result.target_audience:
        console.print(_panel(_bullets(result.target_audience, "blue"), "适合人群", "blue"))

    if result.career_value:
        career = Text(f"  {_wrap_text(result.career_value, TEXT_WIDTH, '  ')}", overflow="fold")
        console.print(_panel(career, "求职参考价值", "magenta"))

    if result.confidence < 0.6:
        console.print(f"[dim]置信度: {result.confidence:.0%}（数据不足，结果仅供参考）[/dim]")
    console.print()


def main() -> None:
    from types import SimpleNamespace

    result = SimpleNamespace(
        summary="这是一个已经跑通 GitHub 仓库采集、RAG 检索、Agent 分析和本地持久化链路的 CLI MVP，但工程化保障仍停留在早期可用阶段。",
        positioning="开发者工具 / AI 仓库分析助手",
        overall_score=6.3,
        tech_stack=SimpleNamespace(
            language="Python 3.12+",
            architecture="模块化单体架构，围绕 GitHub 采集、RAG、Agent、评分、存储和 CLI 展示分层组织",
            core_deps=[
                "Typer",
                "Rich",
                "PyGithub",
                "LangChain",
                "langchain-openai",
                "ChromaDB",
                "SQLAlchemy",
                "aiosqlite",
                "pydantic-settings",
            ],
        ),
        highlights=[
            "项目把仓库分析拆成 GitHub 数据采集、RAG 检索、Agent 推理、评分映射和 SQLite 持久化等模块，这种职责分离让后续替换模型、扩展数据源或新增输出端更容易落地。",
            "README 不只是概念介绍，还给出了安装方式、环境变量、运行命令、终端输出示例和核心数据流说明，这能显著降低新用户上手成本并帮助评审快速理解设计意图。",
            "最近已有 19 次提交且提交信息覆盖 github、rag、analysis、database、agent、cli 等关键模块，说明项目并非一次性骨架，而是在按功能逐步迭代形成可运行 MVP。",
            "项目引入 uv.lock 作为锁文件并在 pyproject.toml 中集中声明依赖与脚本入口，这有助于环境复现、依赖一致性和命令入口标准化。",
            "README 明确说明 tool-calling 日志和历史分析记录能力，说明作者关注分析过程可追踪性而不只是最终文本结果，这对调试 Agent 行为和做演示都很有帮助。",
        ],
        weaknesses=[
            "仓库目录中没有 tests 目录或明显测试文件证据，缺少自动化验证会让评分规则、Agent 输出结构和持久化逻辑在后续迭代时更容易回归失效。",
            "未发现 .github/workflows 等 CI 配置，也没有 Issue 或 PR 历史，说明项目当前更像个人 MVP 而非经过协作流程验证的工程，这会削弱可靠性和长期维护信心。",
            "仓库概览未返回 License 文件而 README 仅写了 MIT License，如果实际仓库中没有正式许可证文件，会给复用、分发和求职展示带来合规不确定性。",
            "技术栈中已经声明 FastAPI 和 Jinja2 已接入，但目录结构里 web 模块几乎为空，说明设计愿景大于当前交付范围，若对外表述不清容易造成功能完成度被高估。",
            "项目依赖 GitHub API、LLM 接口和 Embedding 服务三类外部能力，但目前公开证据更多来自 README 而非完整代码片段，若缺少超时、降级和失败恢复机制，真实运行稳定性会受外部服务波动影响。",
        ],
        suggestions=SimpleNamespace(
            beginner="先补齐基础工程护栏，优先新增 tests 目录并为 URL 解析、评分映射、SQLite 读写和 CLI 命令写最小可运行测试，同时补上正式 LICENSE 文件，这样能最快提升可信度和复现性。",
            intermediate="接着增加 GitHub Actions，把 lint、类型检查和 pytest 接入提交流程，并为外部 API 调用补充超时、重试和结构化异常处理，这能显著降低回归风险并证明项目具备持续演进能力。",
            senior="下一步可以把当前 CLI MVP 演进为可观测的服务化架构，例如补充统一 tracing 日志、缓存与限流策略、结果版本化和 Web API 层，再通过真实样例仓库基准集验证评分稳定性与一致性。",
        ),
        target_audience=[
            "想用 AI 快速筛选和阅读 GitHub 仓库的开发者",
            "希望展示 Agent 工具调用与 RAG 集成能力的 Python 开发者",
        ],
        career_value="这个项目对求职展示的价值在于它体现了你能把 LLM、RAG、外部 API、CLI 交互和本地存储串成一条完整产品链路，适合展示 AI 应用工程化思维与模块化设计能力，但目前仍缺少测试覆盖、CI 证据、协作记录和正式许可证等强证明材料，离高可信度作品集项目还有一段距离。",
        confidence=0.85,
    )

    grade = SimpleNamespace(
        maturity_level="L3",
        maturity_name=" L3 Standard/标准级",
        difficulty_level="D3",
        difficulty_name="D3 Intermediate/实战级",
    )

    render_report(result, grade, "S7EN7/RepoPilot")


if __name__ == "__main__":
    main()