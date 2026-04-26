from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from repopilot.analysis.schemas import AnalysisResult, GradeResult

console = Console()


def render_report(result: AnalysisResult, grade: GradeResult) -> None:
    console.print(Panel("[bold cyan]RepoPilot 分析报告[/bold cyan]", box=box.DOUBLE))

    console.print(f"\n[bold]一句话概述[/bold]\n  {result.summary}")
    console.print(f"\n[bold]项目定位[/bold]\n  {result.positioning}")

    grade_table = Table(box=box.SIMPLE, show_header=False)
    grade_table.add_column(style="bold")
    grade_table.add_column()
    grade_table.add_row("工程成熟度", f"[green]{grade.maturity_level} {grade.maturity_name}[/green]")
    grade_table.add_row("复刻难度", f"[yellow]{grade.difficulty_level} {grade.difficulty_name}[/yellow]")
    grade_table.add_row("综合评分", f"[bold]{result.overall_score:.1f} / 10[/bold]")
    console.print("\n[bold]项目评级[/bold]")
    console.print(grade_table)

    ts = result.tech_stack
    console.print(f"\n[bold]技术架构[/bold]")
    console.print(f"  语言: {ts.language}  |  架构: {ts.architecture}")
    if ts.core_deps:
        console.print(f"  核心依赖: {', '.join(ts.core_deps)}")

    if result.highlights:
        console.print("\n[bold green]项目亮点[/bold green]")
        for h in result.highlights:
            console.print(f"  • {h}")

    if result.weaknesses:
        console.print("\n[bold yellow]项目不足[/bold yellow]")
        for w in result.weaknesses:
            console.print(f"  • {w}")

    s = result.suggestions
    console.print("\n[bold]优化建议[/bold]")
    if s.beginner:
        console.print(f"  [dim][入门][/dim] {s.beginner}")
    if s.intermediate:
        console.print(f"  [dim][中级][/dim] {s.intermediate}")
    if s.senior:
        console.print(f"  [dim][高级][/dim] {s.senior}")

    if result.target_audience:
        console.print("\n[bold]适合人群[/bold]")
        for t in result.target_audience:
            console.print(f"  • {t}")

    if result.career_value:
        console.print(f"\n[bold]求职参考价值[/bold]\n  {result.career_value}")

    if result.confidence < 0.6:
        console.print(f"\n[dim]置信度: {result.confidence:.0%}（数据不足，结果仅供参考）[/dim]")
