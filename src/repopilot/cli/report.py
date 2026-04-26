import re
from textwrap import fill

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from repopilot.analysis.schemas import AnalysisResult, GradeResult

console = Console(width=100)


def _clean_prefix(text: str) -> str:
    return re.sub(r"^(亮点|不足)\s*\d+\s*[:：]\s*", "", text).strip()


def _wrap(text: str, indent: str = "  ") -> str:
    return fill(text, width=92, initial_indent=indent, subsequent_indent=indent)


def _render_bullets(items: list[str]) -> Group:
    lines = []
    for item in items:
        clean = _clean_prefix(item)
        wrapped = fill(clean, width=88, initial_indent="  • ", subsequent_indent="    ")
        lines.append(Text.from_markup(wrapped))
    return Group(*lines)


def render_report(result: AnalysisResult, grade: GradeResult) -> None:
    title = Panel(
        Text("RepoPilot 分析报告", style="bold cyan", justify="center"),
        box=box.DOUBLE,
        expand=False,
        padding=(0, 2),
    )
    console.print()
    console.print(title)

    console.print(Panel(_wrap(result.summary), title="一句话概述", border_style="cyan", expand=False))
    console.print(Panel(_wrap(result.positioning), title="项目定位", border_style="blue", expand=False))

    grade_table = Table(box=box.SIMPLE_HEAVY, show_header=False, expand=False, pad_edge=False)
    grade_table.add_column(style="bold cyan", no_wrap=True)
    grade_table.add_column(style="white")
    grade_table.add_row("工程成熟度", f"[green]{grade.maturity_level} {grade.maturity_name}[/green]")
    grade_table.add_row("复刻难度", f"[yellow]{grade.difficulty_level} {grade.difficulty_name}[/yellow]")
    grade_table.add_row("综合评分", f"[bold]{result.overall_score:.1f} / 10[/bold]")
    console.print(Panel(grade_table, title="项目评级", border_style="magenta", expand=False))

    ts = result.tech_stack
    tech_lines = [
        _wrap(f"语言: {ts.language or '未知'}"),
        _wrap(f"架构: {ts.architecture or '未知'}"),
    ]
    if ts.core_deps:
        tech_lines.append(_wrap(f"核心依赖: {', '.join(ts.core_deps)}"))
    console.print(Panel(Group(*[Text(line) for line in tech_lines]), title="技术架构", border_style="green", expand=False))

    if result.highlights:
        console.print(Panel(_render_bullets(result.highlights), title="项目亮点", border_style="green", expand=False))

    if result.weaknesses:
        console.print(Panel(_render_bullets(result.weaknesses), title="项目不足", border_style="yellow", expand=False))

    suggestion_lines = []
    s = result.suggestions
    if s.beginner:
        suggestion_lines.append(Text(_wrap(f"[入门] {s.beginner}")))
    if s.intermediate:
        suggestion_lines.append(Text(_wrap(f"[中级] {s.intermediate}")))
    if s.senior:
        suggestion_lines.append(Text(_wrap(f"[高级] {s.senior}")))
    if suggestion_lines:
        console.print(Panel(Group(*suggestion_lines), title="优化建议", border_style="cyan", expand=False))

    if result.target_audience:
        console.print(Panel(_render_bullets(result.target_audience), title="适合人群", border_style="blue", expand=False))

    if result.career_value:
        console.print(Panel(_wrap(result.career_value), title="求职参考价值", border_style="magenta", expand=False))

    if result.confidence < 0.6:
        console.print(Text(f"置信度: {result.confidence:.0%}（数据不足，结果仅供参考）", style="dim"))
    console.print()
