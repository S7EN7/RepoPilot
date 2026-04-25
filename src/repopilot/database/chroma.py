import chromadb

from repopilot.config import settings
from repopilot.utils.logger import get_logger
from repopilot.utils.path_tool import get_module_name

logger = get_logger(name=get_module_name(__file__))


def get_chroma_client() -> chromadb.PersistentClient:
    """获取 ChromaDB 持久化客户端"""
    return chromadb.PersistentClient(path=settings.repopilot_chroma_path)


def get_collection_name(repo_name: str) -> str:
    """将 owner/repo 转为合法的 collection 名称"""
    return repo_name.replace("/", "_").replace(".", "_")[:63]


def get_or_create_collection(repo_name: str):
    """获取或创建 collection"""
    client = get_chroma_client()
    collection_name = get_collection_name(repo_name)
    return client.get_or_create_collection(name=collection_name)


def reset_collection(repo_name: str):
    """删除并重新创建 collection"""
    client = get_chroma_client()
    collection_name = get_collection_name(repo_name)

    try:
        client.delete_collection(collection_name)
    except Exception:
        logger.debug(f"collection 不存在，跳过删除: {collection_name}")

    return client.create_collection(name=collection_name)
