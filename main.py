import os
import sys

# Force UTF-8 output on Windows to handle special chars in PDF/LLM text
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # type: ignore
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')  # type: ignore

import database
from modules.llm.query_engine import ask_question, is_ollama_running
from modules.retrieval.vector_store import get_document_count
from ingest_manager import ingest_file

_DEFAULT_CLI_USER = "cli_user"


def _ensure_cli_user():
    """Creates a default user for CLI sessions if it doesn't exist."""
    if not database.user_exists(_DEFAULT_CLI_USER):
        database.create_user(
            user_id=_DEFAULT_CLI_USER,
            display_name="CLI User",
            pin="0000",
        )
        print(f"[CLI] Created default user '{_DEFAULT_CLI_USER}' (pin: 0000).")


def _do_upload(user_id: str) -> None:
    """Interactively prompt for a file path and ingest it."""
    try:
        file_path = input("  Enter file path to ingest (PDF / image / audio): ").strip().strip('"').strip("'")
    except (KeyboardInterrupt, EOFError):
        print("\n  Upload cancelled.")
        return

    if not file_path:
        print("  No path entered — upload cancelled.")
        return

    if not os.path.exists(file_path):
        print(f"  ERROR: File not found: '{file_path}'")
        return

    original_name = os.path.basename(file_path)
    print(f"\n  Ingesting '{original_name}' ...")
    result = ingest_file(
        file_path=file_path,
        user_id=user_id,
        original_filename=original_name,
    )
    status = result["status"]
    icon = "✓" if status == "success" else ("⚠" if status == "skipped" else "✗")
    print(f"  {icon} {result['message']}\n")


def main():
    print("=" * 55)
    print("  Offline Multimodal RAG System — SIH25231  (CLI)")
    print("=" * 55)

    database.init_db()
    _ensure_cli_user()
    user_id = _DEFAULT_CLI_USER

    # Optionally ingest a file passed as a CLI argument
    if len(sys.argv) > 1:
        file_to_ingest = sys.argv[1]
        print(f"\n--- Ingesting: {file_to_ingest} ---")
        result = ingest_file(
            file_path=file_to_ingest,
            user_id=user_id,
            original_filename=os.path.basename(file_to_ingest),
        )
        print(f"Result: {result['message']}\n")

    count = get_document_count()

    if not is_ollama_running():
        print("\nWARNING: Ollama is not running. Start it with:  ollama serve")

    if count == 0:
        print(
            "\nThe vector database is empty — no documents have been ingested yet.\n"
            "  • Run:  python main.py <file.pdf>  to ingest from the command line.\n"
            "  • Or type  upload  at the prompt below.\n"
        )
    else:
        print(f"\nDatabase ready — {count} total chunks indexed.")

    print("\nCommands:  upload (u) — ingest a file | quit (q) — exit\n")

    while True:
        try:
            user_input = input("Question / Command: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        # Upload command
        if user_input.lower() in {"upload", "u", "ingest"}:
            _do_upload(user_id)
            count = get_document_count()
            print(f"  [DB] {count} total chunks in vector store.\n")
            continue

        # Guard: need at least some documents before querying
        count = get_document_count()
        if count == 0:
            print("  No documents ingested yet. Type  upload  to add a file first.\n")
            continue

        print("Searching and generating answer...\n")
        answer, sources = ask_question(user_input, user_id=user_id)

        print("=== ANSWER ===")
        print(answer)

        if sources:
            print("\n=== SOURCES ===")
            for doc in sources:
                src  = doc.metadata.get("original_filename", doc.metadata.get("source", "Unknown"))
                page = doc.metadata.get("page")
                loc  = f" (page {page})" if page else ""
                preview = doc.page_content[:80].replace("\n", " ")
                print(f"  • {src}{loc} — \"{preview}...\"")
        print()


if __name__ == "__main__":
    main()