from pathlib import Path


def get_project_root() -> Path:
    """
    获取工程所在的根目录
    :return: 工程根目录 Path 对象
    """
    # 当前文件路径: src/repopilot/utils/path_tool.py
    current_file = Path(__file__).resolve()

    # 当前文件所在目录: src/repopilot/utils/
    current_dir = current_file.parent

    # 包目录: src/repopilot/
    package_dir = current_dir.parent

    # src 目录: src/
    src_dir = package_dir.parent

    # 工程根目录: RepoPilot/
    project_root = src_dir.parent

    return project_root


def get_abs_path(relative_path: str | Path) -> Path:
    """
    传递相对路径，得到绝对路径
    :param relative_path: 相对路径
    :return: 绝对路径 Path 对象
    """
    
    return get_project_root() / relative_path


def get_module_name(file_path: str | Path) -> str:
    """
    根据文件路径生成模块名

    示例：
    src/repopilot/utils/logger.py -> repopilot.utils.logger
    """
    path = Path(file_path).resolve()
    src_root = get_project_root() / "src"

    try:
        relative_path = path.relative_to(src_root)
    except ValueError:
        relative_path = path.stem
        return str(relative_path)

    return ".".join(relative_path.with_suffix("").parts)

if __name__ == "__main__":
    print(get_abs_path("config.py"))
    print(get_module_name("src/repopilot/utils/logger.py"))