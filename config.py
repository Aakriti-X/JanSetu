# config.py — Single source of truth for all model names, paths, and settings.
# Change a model here and it automatically updates everywhere in the project.

# --- Whisper (Audio Transcription) ---
WHISPER_MODEL_SIZE = "base"     # Options: "tiny", "base", "small", "medium", "large"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# --- Ollama Models (must be pulled via: ollama pull <model>) ---
VISION_MODEL = "llava"          # Used for image understanding/OCR
LLM_MODEL = "llama3"            # Used for answering questions

# --- Embeddings (HuggingFace, runs fully offline) ---
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# --- Storage Paths ---
VECTORDB_PATH = "./my_vectordb"
INGESTION_LOG_DB = "ingestion_log.db"

# --- FastAPI Server ---
API_HOST = "0.0.0.0"
API_PORT = 8000
# Add your Next.js dev/prod URLs here
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
]

# --- File Upload Limits ---
MAX_FILE_SIZE_MB = 100
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".mp3", ".wav", ".m4a", ".flac"}

# --- Text Chunking ---
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- Retrieval ---
TOP_K_RESULTS = 3
