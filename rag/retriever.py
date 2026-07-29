import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CHROMA_DIR = os.path.join(PROJECT_ROOT, "data", "chroma_db")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_K = 3

# Module-level cache so we don't reload the embedding model / vectorstore
# on every single function call
_vectorstore = None


def _get_vectorstore():
    """Lazily loads and caches the Chroma vector store (loads once, reuses after)."""
    global _vectorstore

    if _vectorstore is None:
        if not os.path.exists(CHROMA_DIR):
            raise FileNotFoundError(
                f"Chroma database not found at {CHROMA_DIR}. "
                "Run 'python rag/ingest.py' first to build it."
            )

        embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embedding_model
        )

    return _vectorstore


def get_retriever(k: int = DEFAULT_K):
    """
    Returns a LangChain retriever backed by the persisted Chroma vector store.

    Args:
        k: number of top matching chunks to return per query (default 3)
    """
    vectorstore = _get_vectorstore()
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )


def retrieve_context(query: str, k: int = DEFAULT_K) -> str:
    """
    Convenience function: runs a retrieval query and returns a single
    formatted context string (source-tagged), ready to feed into an LLM prompt.
    """
    retriever = get_retriever(k=k)
    docs = retriever.invoke(query)

    chunks = [f"[Source: {doc.metadata['source']}]\n{doc.page_content}" for doc in docs]
    return "\n\n".join(chunks)


if __name__ == "__main__":
    # Quick manual test when running this file directly
    test_query = "Where can I see elephants?"
    print(f"Test query: {test_query}\n")
    print(retrieve_context(test_query))