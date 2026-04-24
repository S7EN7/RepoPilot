from pydantic import BaseModel, Field


class RepoData(BaseModel):
    """GitHub 仓库采集数据模型"""

    # 基本标识
    repo_url: str = Field(description="GitHub 仓库完整 URL")
    repo_name: str = Field(description="仓库全名，格式: owner/repo")
    owner: str = Field(description="仓库所有者")
    name: str = Field(description="仓库名称")

    # 元数据
    description: str = Field(default="", description="仓库描述")
    language: str = Field(default="", description="主要编程语言")
    topics: list[str] = Field(default_factory=list, description="仓库标签列表")

    # 统计数据
    stars: int = Field(default=0, description="Star 数量")
    forks: int = Field(default=0, description="Fork 数量")
    open_issues: int = Field(default=0, description="Open Issue 数量")
    license: str = Field(default="", description="开源协议名称")

    # 仓库结构
    default_branch: str = Field(default="main", description="默认分支名")
    tree_text: str = Field(default="", description="目录结构树文本")

    # 文件内容
    readme_text: str = Field(default="", description="README 内容，缺失时降级为仓库描述")
    key_files: dict[str, str] = Field(
        default_factory=dict,
        description="关键配置文件内容，key 为文件名，value 为文件内容",
    )

    # 活跃度
    recent_commits: list[str] = Field(
        default_factory=list, description="最近 commit 摘要列表"
    )
    issue_stats: dict[str, int] = Field(
        default_factory=dict, description="Issue 统计，如 {open: 10, closed: 50}"
    )
    pr_stats: dict[str, int] = Field(
        default_factory=dict, description="PR 统计，如 {open: 3, merged: 120}"
    )
