# api.py — FastAPI HTTP server for the SIH25231 offline multimodal RAG backend.
# Start with:  python api.py   OR   uvicorn api:app --reload --port 8000
# Docs at:     http://localhost:8000/docs

import os
import tempfile
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import database
from config import (
    API_HOST,
    API_PORT,
    CORS_ORIGINS,
    MAX_FILE_SIZE_MB,
    ALLOWED_EXTENSIONS,
)
from ingest_manager import ingest_file
from modules.llm.query_engine import ask_question, is_ollama_running
from modules.retrieval.vector_store import get_document_count

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Lifespan: initialise DB schema once when the server starts
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    print("[API] Database schema initialised.")
    yield


app = FastAPI(
    title="SIH25231 Offline RAG API",
    lifespan=lifespan,
    description=(
        "Offline multimodal RAG backend for bilingual (Hindi/English) "
        "rural document retrieval. Each user's documents are completely isolated."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    user_id:      str = Field(..., min_length=3, max_length=50,
                               description="Unique identifier (e.g. phone number or name)")
    display_name: str = Field(..., min_length=1, max_length=100)
    pin:          str = Field(..., min_length=4, max_length=20,
                               description="4-20 character PIN")

class LoginRequest(BaseModel):
    user_id: str
    pin:     str

class TokenResponse(BaseModel):
    user_id:      str
    display_name: str
    message:      str

class QueryRequest(BaseModel):
    question: str

class SourceDocument(BaseModel):
    source:   str
    filename: str
    type:     str
    page:     int | None = None
    language: str | None = None
    preview:  str

class QueryResponse(BaseModel):
    answer:  str
    sources: list[SourceDocument]

class IngestResponse(BaseModel):
    status:   str      # "success" | "skipped" | "error"
    filename: str
    chunks:   int
    message:  str

class FileRecord(BaseModel):
    id:                str
    original_filename: str
    file_type:         str
    size_bytes:        int
    chunk_count:       int
    ingested_at:       str

class StatsResponse(BaseModel):
    total_files:    int
    total_chunks:   int
    ollama_running: bool
    user_id:        str


# ---------------------------------------------------------------------------
# Auth Dependency — reads X-User-ID and X-User-PIN headers
# ---------------------------------------------------------------------------

def get_current_user(
    x_user_id:  str = Header(..., description="Your user ID"),
    x_user_pin: str = Header(..., description="Your PIN"),
) -> str:
    """
    FastAPI dependency that validates the user's credentials on every request.

    Usage: Add `user_id: str = Depends(get_current_user)` to any endpoint.

    The Next.js frontend sends these two headers with every API call:
        X-User-ID:  <user_id>
        X-User-PIN: <pin>
    """
    if not database.verify_user(x_user_id, x_user_pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID or PIN. Please check your credentials.",
        )
    return x_user_id


# ---------------------------------------------------------------------------
# System Endpoints (no auth required)
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"])
def health_check():
    """Liveness probe — returns ok when the server is running."""
    return {"status": "ok", "message": "SIH25231 RAG backend is running."}


# ---------------------------------------------------------------------------
# User Management (no auth required for register/login)
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=TokenResponse, tags=["Auth"])
def register(req: RegisterRequest):
    """
    Create a new user account.
    - user_id must be unique (e.g. phone number, aadhaar last 4 digits, or any name)
    - PIN is hashed with SHA-256 before storage — never stored in plain text
    """
    created = database.create_user(
        user_id=req.user_id.strip(),
        display_name=req.display_name.strip(),
        pin=req.pin,
    )
    if not created:
        raise HTTPException(
            status_code=409,
            detail=f"User ID '{req.user_id}' is already taken. Please choose another.",
        )
    return TokenResponse(
        user_id=req.user_id,
        display_name=req.display_name,
        message="Account created successfully.",
    )


@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(req: LoginRequest):
    """
    Verify credentials and return user info.
    The frontend should store user_id + PIN locally (offline-safe) and
    send them as X-User-ID / X-User-PIN headers on every subsequent request.
    """
    if not database.verify_user(req.user_id, req.pin):
        raise HTTPException(
            status_code=401,
            detail="Incorrect user ID or PIN.",
        )
    user = database.get_user(req.user_id)
    if user is None:
        raise HTTPException(status_code=500, detail="User record missing after verification.")
    return TokenResponse(
        user_id=req.user_id,
        display_name=user["display_name"],
        message="Login successful.",
    )


# ---------------------------------------------------------------------------
# Ingestion (requires auth)
# ---------------------------------------------------------------------------

@app.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_endpoint(
    file:    UploadFile = File(...),
    user_id: str        = Depends(get_current_user),
):
    """
    Upload a file (PDF, image, or audio) to YOUR personal document library.
    Other users cannot see or search your documents.
    """
    original_name = file.filename or "unknown"
    suffix = Path(original_name).suffix.lower()

    # Validate extension
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # Read and check size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max: {MAX_FILE_SIZE_MB} MB.",
        )

    # Save to temp file → run pipeline → clean up
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        result = ingest_file(
            file_path=tmp_path,
            user_id=user_id,
            original_filename=original_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return IngestResponse(
        status=result["status"],
        filename=original_name,
        chunks=result["chunks"],
        message=result["message"],
    )


# ---------------------------------------------------------------------------
# Query (requires auth)
# ---------------------------------------------------------------------------

@app.post("/query", response_model=QueryResponse, tags=["Query"])
def query_endpoint(
    request: QueryRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Ask a question — answers are drawn ONLY from your own documents.
    Supports both Hindi and English questions.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # user_id is passed so ChromaDB only searches THIS user's chunks
    answer, source_docs = ask_question(request.question, user_id=user_id)

    sources = [
        SourceDocument(
            source=doc.metadata.get("source", "Unknown"),
            filename=doc.metadata.get("original_filename", Path(doc.metadata.get("source", "")).name),
            type=doc.metadata.get("type", "unknown"),
            page=doc.metadata.get("page"),
            language=doc.metadata.get("language"),
            preview=doc.page_content[:120].replace("\n", " "),
        )
        for doc in source_docs
    ]

    return QueryResponse(answer=answer, sources=sources)


# ---------------------------------------------------------------------------
# File Management (requires auth — users only see their own files)
# ---------------------------------------------------------------------------

@app.get("/files", response_model=list[FileRecord], tags=["Files"])
def list_files(user_id: str = Depends(get_current_user)):
    """
    Returns YOUR files only. Other users' documents are never exposed.
    """
    try:
        rows = database.get_user_files(user_id)
        return [
            FileRecord(
                id=r["hash"],
                original_filename=r["original_filename"],
                file_type=r["file_type"],
                size_bytes=r["size_bytes"],
                chunk_count=r["chunk_count"],
                ingested_at=r["ingested_at"],
            )
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/files/{file_id}", tags=["Files"])
def delete_file(file_id: str, user_id: str = Depends(get_current_user)):
    """
    Remove a file from YOUR library. You cannot delete another user's file.
    """
    deleted = database.delete_user_file(file_hash=file_id, user_id=user_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="File not found in your library.",
        )
    return {"status": "deleted", "id": file_id}


# ---------------------------------------------------------------------------
# Stats (requires auth — returns stats for the current user only)
# ---------------------------------------------------------------------------

@app.get("/stats", response_model=StatsResponse, tags=["System"])
def get_stats(user_id: str = Depends(get_current_user)):
    """
    Returns dashboard statistics scoped to the current user:
    - total_files: how many files YOU have ingested
    - total_chunks: total vector chunks across the entire shared ChromaDB
    - ollama_running: whether the local LLM server is reachable
    """
    return StatsResponse(
        total_files=database.get_user_file_count(user_id),
        total_chunks=get_document_count(),
        ollama_running=is_ollama_running(),
        user_id=user_id,
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    print(f"\n  SIH25231 RAG API  →  http://localhost:{API_PORT}")
    print(f"  Interactive docs  →  http://localhost:{API_PORT}/docs\n")
    uvicorn.run("api:app", host=API_HOST, port=API_PORT, reload=True)
