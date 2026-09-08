import os
import sys
from modules.ingestion.doc_loader import load_and_chunk_pdf
from modules.ingestion.image_loader import load_and_chunk_image
from modules.ingestion.audio_loader import load_and_chunk_audio
from modules.retrieval.vector_store import add_chunks_to_db

def ingest_file(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
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
        print(f"Successfully processed and stored {len(chunks)} chunks from {file_path}!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_manager.py <path_to_file>")
    else:
        ingest_file(sys.argv[1])