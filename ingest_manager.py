import os
import sys
import sqlite3
import hashlib
from datetime import datetime

from modules.ingestion.doc_loader import load_and_chunk_pdf
from modules.ingestion.image_loader import load_and_chunk_image
from modules.ingestion.audio_loader import load_and_chunk_audio
from modules.retrieval.vector_store import add_chunks_to_db

# --- Step 9: Deduplication Helpers ---
def get_file_hash(path):
    """Generates a unique MD5 hash for the file."""
    return hashlib.md5(open(path, 'rb').read()).hexdigest()

def is_already_ingested(path):
    """Checks the SQLite database to see if the file hash already exists."""
    conn = sqlite3.connect("ingestion_log.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS logs (hash TEXT PRIMARY KEY, path TEXT, ingested_at TEXT)")
    
    file_hash = get_file_hash(path)
    cur.execute("SELECT 1 FROM logs WHERE hash=?", (file_hash,))
    result = cur.fetchone()
    conn.close()
    
    return result is not None

def log_ingestion(path):
    """Records the file in the database after successful ingestion."""
    conn = sqlite3.connect("ingestion_log.db")
    cur = conn.cursor()
    file_hash = get_file_hash(path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cur.execute("INSERT INTO logs (hash, path, ingested_at) VALUES (?, ?, ?)", (file_hash, path, timestamp))
    conn.commit()
    conn.close()

# --- Main Routing Manager ---
def ingest_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    # Check for duplicates before doing any heavy processing
    if is_already_ingested(file_path):
        print(f"Skipping '{file_path}': This file has already been ingested.")
        return

    ext = os.path.splitext(file_path)[1].lower()
    chunks = []

    print(f"Routing file type '{ext}' to the appropriate pipeline...")
    
    if ext == ".pdf":
        chunks = load_and_chunk_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        chunks = load_and_chunk_image(file_path)
    elif ext in [".mp3", ".wav", ".m4a", ".flac"]:
        chunks = load_and_chunk_audio(file_path)
    else:
        print(f"Unsupported file format: {ext}")
        return

    if chunks:
        add_chunks_to_db(chunks)
        log_ingestion(file_path)
        print(f"Successfully processed and stored {len(chunks)} chunks from {file_path}!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_manager.py <path_to_file>")
    else:
        ingest_file(sys.argv[1])