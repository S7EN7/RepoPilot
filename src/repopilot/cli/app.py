import asyncio
import sys

import typer
from rich.console import Console
from rich.table import Table

from repopilot.analysis.repository import AnalysisRepository
from repopilot.analysis.schemas import AnalysisResult
from repopilot.analysis.service import AnalysisService
from repopilot.cli.report import render_report
from repopilot.database.sqlite import init_db

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

app = typer.Typer(help="RepoPilot — GitHub 仓库智能分析助手")
console = Console()


@app.callback(invoke_without_command=True)
def _init(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
    asyncio.run(init_db())


@app.command()
def analyze(url: str = typer.Argument(..., help="GitHub 仓库 URL")) -> None:
    """分析 GitHub 仓库"""
    console.print(f"[cyan]正在分析: {url}[/cyan]")
    try:
        result, grade, _ = AnalysisService().analyze(url)
        render_report(result, grade)
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def history() -> None:
    """查看历史分析记录"""
    records = asyncio.run(AnalysisRepository().get_history())
    if not records:
        console.print("[dim]暂无历史记录[/dim]")
        return

    table = Table(title="历史分析记录")
    table.add_column("ID", style="dim")
    table.add_column("仓库")
    table.add_column("成熟度")
    table.add_column("难度")
    table.add_column("评分")
    table.add_column("时间")

    for r in records:
        table.add_row(
            str(r.id),
            r.repo_name,
            r.maturity_level,
            r.difficulty_level,
            f"{r.overall_score:.1f}",
            r.analyzed_at.strftime("%Y-%m-%d %H:%M"),
        )
    console.print(table)
