import os
import sys
import hashlib

from modules.ingestion.doc_loader import load_and_chunk_pdf
from modules.ingestion.image_loader import load_and_chunk_image
from modules.ingestion.audio_loader import load_and_chunk_audio
from modules.retrieval.vector_store import add_chunks_to_db
from config import ALLOWED_EXTENSIONS
import database


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _get_file_hash(path: str) -> str:
    """Returns the MD5 hash of a file's content (for deduplication)."""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# Main Routing Manager
# ---------------------------------------------------------------------------

def ingest_file(file_path: str, user_id: str, original_filename: str = "") -> dict:
    """
    Routes a file through the correct ingestion pipeline based on its extension.
    All ingested chunks are tagged with the user_id so they are isolated
    from other users' data in both SQLite and ChromaDB.

    Args:
        file_path:         Path to the (possibly temporary) file on disk.
        user_id:           The user this file belongs to.
        original_filename: The original name of the uploaded file (for display).

    Returns a dict:
        {
            "status":  "success" | "skipped" | "error",
            "chunks":  <int>,
            "message": <str>
        }
    """
    # --- Validate the user exists ---
    if not database.user_exists(user_id):
        msg = f"User '{user_id}' not found. Please register first."
        return {"status": "error", "chunks": 0, "message": msg}

    # --- Validate the file exists ---
    if not os.path.exists(file_path):
        msg = f"File not found: '{file_path}'"
        print(f"ERROR: {msg}")
        return {"status": "error", "chunks": 0, "message": msg}

    size_bytes = os.path.getsize(file_path)
    display_name = original_filename or os.path.basename(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        msg = f"Unsupported file format: '{ext}'"
        return {"status": "error", "chunks": 0, "message": msg}

    # --- Deduplication check: per-user (same file can belong to different users) ---
    file_hash = _get_file_hash(file_path)
    if database.file_already_ingested(file_hash, user_id):
        msg = f"'{display_name}' is already in your library."
        print(msg)
        return {"status": "skipped", "chunks": 0, "message": msg}

    # --- Route to the correct pipeline ---
    print(f"[{user_id}] Routing '{ext}' file: {display_name}")
    chunks = []
    try:
        if ext == ".pdf":
            chunks = load_and_chunk_pdf(file_path)
        elif ext in {".png", ".jpg", ".jpeg"}:
            chunks = load_and_chunk_image(file_path)
        elif ext in {".mp3", ".wav", ".m4a", ".flac"}:
            chunks = load_and_chunk_audio(file_path)
    except Exception as e:
        msg = f"Pipeline error while processing '{display_name}': {e}"
        print(f"ERROR: {msg}")
        return {"status": "error", "chunks": 0, "message": msg}

    if not chunks:
        msg = f"No text could be extracted from '{display_name}'."
        return {"status": "error", "chunks": 0, "message": msg}

    # --- Stamp every chunk with the user_id before storing ---
    for chunk in chunks:
        chunk.metadata["user_id"] = user_id
        chunk.metadata["original_filename"] = display_name

    # --- Save to ChromaDB ---
    add_chunks_to_db(chunks)

    # --- Record in SQLite ---
    database.log_ingestion(
        file_hash=file_hash,
        user_id=user_id,
        original_filename=display_name,
        file_type=ext.lstrip("."),
        size_bytes=size_bytes,
        chunk_count=len(chunks),
    )

    msg = f"Successfully indexed {len(chunks)} chunks from '{display_name}'."
    print(f"[{user_id}] {msg}")
    return {"status": "success", "chunks": len(chunks), "message": msg}


# ---------------------------------------------------------------------------
# CLI Entry Point (for quick testing without the API)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ingest_manager.py <user_id> <path_to_file>")
        sys.exit(1)
    database.init_db()
    result = ingest_file(file_path=sys.argv[2], user_id=sys.argv[1])
    print(result)