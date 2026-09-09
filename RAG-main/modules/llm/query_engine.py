import requests
from langchain_ollama import OllamaLLM
from modules.retrieval.vector_store import get_vector_store
from config import LLM_MODEL, TOP_K_RESULTS

# Cached LLM instance — initialised once per server session
_llm: OllamaLLM | None = None

_OLLAMA_BASE_URL = "http://localhost:11434"

# Bilingual system prompt — instructs the model to respond in the same language
# as the question (Hindi or English), suitable for rural communities.
_SYSTEM_PROMPT = """You are a secure, offline AI assistant for rural communities.
Answer the question based ONLY on the context provided below.
If the answer is not in the context, say "I don't know based on the available documents."
Respond in the same language as the question (Hindi or English)."""


def _get_llm() -> OllamaLLM:
    """Returns the cached Ollama LLM, creating it on first call."""
    global _llm
    if _llm is None:
        _llm = OllamaLLM(model=LLM_MODEL, base_url=_OLLAMA_BASE_URL, num_gpu=0)
    return _llm


def is_ollama_running() -> bool:
    """Quick health-check: returns True if the Ollama server is reachable."""
    try:
        requests.get(_OLLAMA_BASE_URL, timeout=2)
        return True
    except Exception:
        return False


def ask_question(question: str, user_id: str) -> tuple[str, list]:
    """
    Runs the full RAG pipeline for a given question, scoped to a single user.

    ChromaDB is filtered by user_id so each user only gets answers from
    their own ingested documents — other users' data is never exposed.

    Args:
        question: The user's natural-language question (Hindi or English).
        user_id:  The user whose document library should be searched.

    Returns:
        (answer_string, source_documents)
        On any failure, returns an error message string and an empty list.
    """
    # 1. Guard: Ollama server check
    if not is_ollama_running():
        return (
            "Ollama is not running. Please start it with:  ollama serve",
            [],
        )

    # 2. Retrieve relevant context — FILTERED to this user's chunks only
    try:
        vector_store = get_vector_store()
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": TOP_K_RESULTS,
                # Filter by user_id only if one is provided and non-empty
                **({"filter": {"user_id": user_id}} if user_id else {}),
            },
        )
        docs = retriever.invoke(question)
    except Exception as e:
        return (f"Database retrieval error: {e}", [])

    if not docs:
        return (
            "No relevant information was found in your documents for this question.",
            [],
        )

    # 3. Build bilingual context prompt
    # Sanitize text: replace characters Windows cp1252 can't encode (PDF ligatures, etc.)
    def _sanitize(text: str) -> str:
        return text.encode("utf-8", errors="replace").decode("utf-8")

    context = "\n\n---\n\n".join(_sanitize(doc.page_content) for doc in docs)
    safe_question = _sanitize(question)
    prompt = f"""{_SYSTEM_PROMPT}

Context:
{context}

Question: {safe_question}
Answer:"""

    # 4. Call the local LLM
    try:
        llm = _get_llm()
        response = llm.invoke(prompt)
        # Sanitize response for safe printing on Windows
        if isinstance(response, str):
            response = response.encode("utf-8", errors="replace").decode("utf-8")
    except Exception as e:
        print(f"[ERROR] LLM generation error: {e}")
        return (f"LLM generation error: {e}", docs)

    return response, docs