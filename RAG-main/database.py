# database.py — Single source of truth for ALL SQLite schema and operations.
#
# SQLite is BUILT INTO Python — no download or installation required.
# The database file (rag_data.db) is created automatically on first run.
#
# Schema overview:
#   users          — registered users (user_id, display_name, pin_hash)
#   ingestion_log  — files ingested PER USER (user_id + hash = unique pair)
#
# Multi-user isolation:
#   Every file is associated with a user_id. Queries to list/delete files
#   always filter by user_id, so users never see each other's documents.
#   ChromaDB chunks also carry a "user_id" metadata field so vector search
#   can be filtered per user.

import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path

from config import INGESTION_LOG_DB


# ---------------------------------------------------------------------------
# Schema SQL — defined once, in one place
# ---------------------------------------------------------------------------

_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id      TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    pin_hash     TEXT NOT NULL,
    created_at   TEXT NOT NULL
);
"""

_CREATE_INGESTION_LOG = """
CREATE TABLE IF NOT EXISTS ingestion_log (
    hash              TEXT    NOT NULL,
    user_id           TEXT    NOT NULL,
    original_filename TEXT    NOT NULL,
    file_type         TEXT    NOT NULL,
    size_bytes        INTEGER NOT NULL DEFAULT 0,
    chunk_count       INTEGER NOT NULL DEFAULT 0,
    ingested_at       TEXT    NOT NULL,
    PRIMARY KEY (hash, user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------


def get_connection() -> sqlite3.Connection:
    """Opens a connection to the SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(INGESTION_LOG_DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row   # rows behave like dicts: row["column_name"]
    return conn


# ---------------------------------------------------------------------------
# Schema initialisation — call this ONCE at server startup
# ---------------------------------------------------------------------------


def init_db() -> None:
    """
    Creates all tables if they don't already exist.
    Safe to call multiple times — it will never drop or overwrite data.
    """
    with get_connection() as conn:
        conn.execute(_CREATE_USERS)
        conn.execute(_CREATE_INGESTION_LOG)
        conn.commit()
    print(f"[DB] Schema ready at '{INGESTION_LOG_DB}'.")


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------


def _hash_pin(pin: str) -> str:
    """Returns a SHA-256 hash of the PIN (never store PINs in plain text)."""
    return hashlib.sha256(pin.encode()).hexdigest()


def create_user(user_id: str, display_name: str, pin: str) -> bool:
    """
    Registers a new user.
    Returns True if created, False if user_id already exists.
    """
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (user_id, display_name, pin_hash, created_at) "
                "VALUES (?, ?, ?, ?)",
                (user_id, display_name, _hash_pin(pin), datetime.now().isoformat()),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # user_id already taken


def verify_user(user_id: str, pin: str) -> bool:
    """
    Returns True if the user_id + PIN combination is correct.
    Used to authenticate API requests.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT pin_hash FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
    if row is None:
        return False
    return row["pin_hash"] == _hash_pin(pin)


def user_exists(user_id: str) -> bool:
    """Returns True if the given user_id exists in the database."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
    return row is not None


def get_user(user_id: str) -> dict | None:
    """Returns user info dict or None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT user_id, display_name, created_at FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Ingestion log — per-user file tracking
# ---------------------------------------------------------------------------


def file_already_ingested(file_hash: str, user_id: str) -> bool:
    """
    Returns True if this exact file (by content hash) has already been
    ingested by this specific user. Different users can ingest the same file.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM ingestion_log WHERE hash = ? AND user_id = ?",
            (file_hash, user_id),
        ).fetchone()
    return row is not None


def log_ingestion(
    file_hash: str,
    user_id: str,
    original_filename: str,
    file_type: str,
    size_bytes: int,
    chunk_count: int,
) -> None:
    """Records a successful ingestion event linked to a specific user."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO ingestion_log "
            "(hash, user_id, original_filename, file_type, size_bytes, chunk_count, ingested_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                file_hash,
                user_id,
                original_filename,
                file_type,
                size_bytes,
                chunk_count,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()


def get_user_files(user_id: str) -> list[dict]:
    """
    Returns all files ingested by a specific user, newest first.
    Other users' files are NOT returned.
    """
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT hash, original_filename, file_type, size_bytes, chunk_count, ingested_at "
            "FROM ingestion_log WHERE user_id = ? ORDER BY ingested_at DESC",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_user_file_count(user_id: str) -> int:
    """Returns the number of files ingested by a specific user."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM ingestion_log WHERE user_id = ?", (user_id,)
        ).fetchone()
    return row["cnt"] if row else 0


def delete_user_file(file_hash: str, user_id: str) -> bool:
    """
    Removes a file record from the ingestion log for this user only.
    Returns True if a record was deleted, False if it wasn't found.
    """
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM ingestion_log WHERE hash = ? AND user_id = ?",
            (file_hash, user_id),
        )
        conn.commit()
    return cur.rowcount > 0
