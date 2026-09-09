from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL, VECTORDB_PATH

# Lazy-loaded cache — embedding model is heavy (~90 MB) and must NOT load at import time.
# It is initialised on the first actual call and reused for the rest of the session.
_embedding_model: HuggingFaceEmbeddings | None = None


def _get_embedding_model() -> HuggingFaceEmbeddings:
    """Returns the cached embedding model, loading it on first access."""
    global _embedding_model
    if _embedding_model is None:
        print(f"Loading embedding model '{EMBEDDING_MODEL}' (first time only)...")
        _embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embedding_model


def get_vector_store(persist_directory: str = VECTORDB_PATH) -> Chroma:
    """Initialises or opens the local ChromaDB vector store."""
    return Chroma(
        embedding_function=_get_embedding_model(),
        persist_directory=persist_directory,
    )


def add_chunks_to_db(chunks: list, persist_directory: str = VECTORDB_PATH) -> Chroma | None:
    """Embeds and saves document chunks to the ChromaDB database."""
    if not chunks:
        print("WARNING: add_chunks_to_db called with an empty chunk list — nothing saved.")
        return None

    vector_store = get_vector_store(persist_directory)
    vector_store.add_documents(documents=chunks)
    print(f"Saved {len(chunks)} chunk(s) to the vector database at '{persist_directory}'.")
    return vector_store


def get_document_count(persist_directory: str = VECTORDB_PATH) -> int:
    """Returns the total number of chunks stored in ChromaDB."""
    try:
        store = get_vector_store(persist_directory)
        return store._collection.count()
    except Exception:
        return 0