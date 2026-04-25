from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from repopilot.config import settings
from repopilot.database.chroma import get_collection_name, reset_collection, get_chroma_client
from repopilot.github.schemas import RepoData
from repopilot.utils.logger import get_logger
from repopilot.utils.path_tool import get_module_name

logger = get_logger(name=get_module_name(__file__))


def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_embedding_model,
    )


def embed_repo(repo_data: RepoData) -> str:
    """将仓库 README + 关键文件分块 embedding 入库，返回 collection 名称"""
    documents = []
    metadatas = []

    if repo_data.readme_text:
        documents.append(repo_data.readme_text)
        metadatas.append({"source": "README.md"})

    for filename, content in repo_data.key_files.items():
        documents.append(content)
        metadatas.append({"source": filename})

    if not documents:
        logger.warning(f"没有可 embedding 的文档: {repo_data.repo_name}")
        return get_collection_name(repo_data.repo_name)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    all_chunks, all_metadatas, all_ids = [], [], []
    for doc, meta in zip(documents, metadatas):
        for i, chunk in enumerate(splitter.split_text(doc)):
            all_chunks.append(chunk)
            all_metadatas.append(meta)
            all_ids.append(f"{meta['source']}_{i}")

    logger.info(f"分块完成: {len(all_chunks)} 个片段")

    collection = reset_collection(repo_data.repo_name)
    embeddings = _get_embeddings()

    batch_size = 50
    for start in range(0, len(all_chunks), batch_size):
        end = min(start + batch_size, len(all_chunks))
        collection.add(
            ids=all_ids[start:end],
            documents=all_chunks[start:end],
            embeddings=embeddings.embed_documents(all_chunks[start:end]),
            metadatas=all_metadatas[start:end],
        )
        logger.info(f"入库: {start + 1}-{end}/{len(all_chunks)}")

    col_name = get_collection_name(repo_data.repo_name)
    logger.info(f"embedding 完成: {col_name}")
    return col_name


def query_context(repo_name: str, query: str, n_results: int = 5) -> str:
    """检索相关上下文片段，返回拼接后的文本"""
    col_name = get_collection_name(repo_name)
    client = get_chroma_client()

    try:
        collection = client.get_collection(name=col_name)
    except Exception:
        logger.warning(f"collection 不存在: {col_name}")
        return ""

    results = collection.query(
        query_embeddings=[_get_embeddings().embed_query(query)],
        n_results=n_results,
    )

    if not results["documents"] or not results["documents"][0]:
        return ""

    parts = [
        f"[来源: {m.get('source', '')}]\n{chunk}"
        for chunk, m in zip(results["documents"][0], results["metadatas"][0])
    ]
    return "\n\n---\n\n".join(parts)
