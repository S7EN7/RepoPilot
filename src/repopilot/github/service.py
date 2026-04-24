import re

from github import Github, GithubException

from repopilot.config import settings
from repopilot.github.schemas import RepoData
from repopilot.utils.logger import get_logger
from repopilot.utils.path_tool import get_module_name

logger = get_logger(name=get_module_name(__file__))

GITHUB_URL_PATTERN = re.compile(
    r"(?:https?://)?github\.com/([^/]+)/([^/.]+?)(?:\.git)?/?$"
)

KEY_FILE_NAMES = [
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Makefile",
    ".github/workflows",
    "tsconfig.json",
    "setup.py",
    "setup.cfg",
    "pom.xml",
    "build.gradle",
]

MAX_FILE_SIZE = 1024 * 1024  # 1MB


class GithubService:
    """GitHub 仓库数据采集服务"""



    def __init__(self) -> None:
        if not settings.github_token:
            logger.warning("GITHUB_TOKEN 未配置，API 请求频率将受限")
        self._client = Github(settings.github_token or None)

    def fetch(self, url: str) -> RepoData:
        """采集 GitHub 仓库完整数据"""
        repo_name = self._parse_repo_name(url)
        logger.info(f"开始采集仓库: {repo_name}")

        try:
            repo = self._client.get_repo(repo_name)
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"仓库不存在或无权访问: {repo_name}")
            raise

        # 元数据
        data = RepoData(
            repo_url=url,
            repo_name=repo.full_name,
            owner=repo.owner.login,
            name=repo.name,
            description=repo.description or "",
            language=repo.language or "",
            topics=repo.get_topics(),
            stars=repo.stargazers_count,
            forks=repo.forks_count,
            open_issues=repo.open_issues_count,
            license=repo.license.name if repo.license else "",
            default_branch=repo.default_branch,
        )

        logger.info(f"元数据采集完成: {repo_name}")

        # 目录结构树
        logger.info(f"获取目录结构: {repo_name}")
        data.tree_text = self._fetch_tree(repo)

        # README
        logger.info(f"获取 README: {repo_name}")
        data.readme_text = self._fetch_readme(repo)

        # 关键配置文件
        logger.info(f"获取关键文件: {repo_name}")
        data.key_files = self._fetch_key_files(repo)

        # 最近 commits
        logger.info(f"获取最近 commits: {repo_name}")
        data.recent_commits = self._fetch_recent_commits(repo)

        # Issue/PR 统计
        logger.info(f"获取 Issue/PR 统计: {repo_name}")
        data.issue_stats = self._fetch_issue_stats(repo)
        data.pr_stats = self._fetch_pr_stats(repo)

        logger.info(f"仓库采集完成: {repo_name}")
        return data

    def _parse_repo_name(self, url: str) -> str:
        """
        从 GitHub URL 中提取 owner/repo
        支持格式：
            - https://github.com/owner/repo
            - https://github.com/owner/repo.git
            - http://github.com/owner/repo
            - github.com/owner/repo
        """
        match = GITHUB_URL_PATTERN.match(url.strip())
        if not match:
            raise ValueError(f"无法解析 GitHub 仓库地址: {url}")
        return f"{match.group(1)}/{match.group(2)}"

    def _fetch_tree(self, repo) -> str:
        """获取仓库目录结构树文本，格式类似 tree 命令输出"""
        try:
            tree = repo.get_git_tree(repo.default_branch, recursive=True).tree
        except GithubException:
            logger.warning(f"无法获取目录结构: {repo.full_name}")
            return ""

        dirs: dict[str, list[str]] = {}
        for item in tree:
            parent = "/".join(item.path.split("/")[:-1]) or "."
            dirs.setdefault(parent, [])
            dirs.setdefault(item.path, [])
            if item.type == "tree":
                dirs[parent].append(item.path)

        def build(path: str, prefix: str = "") -> list[str]:
            children = []
            for item in tree:
                parts = item.path.split("/")
                parent = "/".join(parts[:-1]) or "."
                if parent == path:
                    children.append(item)

            lines = []
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                connector = "└── " if is_last else "├── "
                name = child.path.split("/")[-1]
                if child.type == "tree":
                    name += "/"
                lines.append(f"{prefix}{connector}{name}")
                if child.type == "tree":
                    extension = "    " if is_last else "│   "
                    lines.extend(build(child.path, prefix + extension))
            return lines

        result = [f"{repo.name}/"]
        result.extend(build("."))
        return "\n".join(result)

    def _fetch_readme(self, repo) -> str:
        """获取 README 内容，缺失时降级为仓库描述"""
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode("utf-8")
        except GithubException:
            logger.warning(f"README 不存在，降级为仓库描述: {repo.full_name}")
            return repo.description or ""



    def _fetch_key_files(self, repo) -> dict[str, str]:
        """获取关键配置文件内容，大文件截断保留头尾摘要"""
        result = {}
        for filename in KEY_FILE_NAMES:
            try:
                content_file = repo.get_contents(filename)
                if isinstance(content_file, list):
                    names = [f.name for f in content_file]
                    result[filename] = f"[目录] 包含: {', '.join(names)}"
                    continue
                raw = content_file.decoded_content.decode("utf-8")
                if len(raw) > MAX_FILE_SIZE:
                    head = raw[:512 * 1024]
                    tail = raw[-512 * 1024:]
                    result[filename] = f"{head}\n\n... [截断，原文件 {len(raw)} 字节] ...\n\n{tail}"
                else:
                    result[filename] = raw
            except GithubException:
                continue
        logger.info(f"获取到 {len(result)} 个关键文件")
        return result

    def _fetch_recent_commits(self, repo, count: int = 20) -> list[str]:
        """获取最近 N 条 commit 摘要"""
        try:
            commits = repo.get_commits()[:count]
            return [
                f"{c.sha[:7]} {c.commit.message.split(chr(10))[0]}"
                for c in commits
            ]
        except GithubException:
            logger.warning(f"无法获取 commits: {repo.full_name}")
            return []

    def _fetch_issue_stats(self, repo) -> dict[str, int]:
        """获取 Issue 统计"""
        try:
            open_issues = repo.get_issues(state="open")
            closed_issues = repo.get_issues(state="closed")
            return {
                "open": open_issues.totalCount,
                "closed": closed_issues.totalCount,
            }
        except GithubException:
            logger.warning(f"无法获取 Issue 统计: {repo.full_name}")
            return {}

    def _fetch_pr_stats(self, repo) -> dict[str, int]:
        """获取 PR 统计"""
        try:
            open_prs = repo.get_pulls(state="open")
            closed_prs = repo.get_pulls(state="closed")
            return {
                "open": open_prs.totalCount,
                "merged": sum(1 for pr in closed_prs if pr.merged),
                "closed": closed_prs.totalCount,
            }
        except GithubException:
            logger.warning(f"无法获取 PR 统计: {repo.full_name}")
            return {}

if __name__ == "__main__":
    service = GithubService()
    repo_url = "https://github.com/S7EN7/RepoPilot"
    try:
        repo_data = service.fetch(repo_url)
        print(repo_data.model_dump_json(indent=2))
        print("\n目录结构:")
        print(repo_data.tree_text)
        print("\nREADME:")
        print(repo_data.readme_text)
    except Exception as e:
        logger.error(f"采集失败: {e}")
