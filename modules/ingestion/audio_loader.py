import os
import traceback
from faster_whisper import WhisperModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import WHISPER_MODEL_SIZE, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE, CHUNK_SIZE, CHUNK_OVERLAP

# Fix for OpenMP crashes on Windows with faster-whisper
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Module-level cache: model is loaded once and reused across all calls in the session
_whisper_model: WhisperModel | None = None


def _get_whisper_model() -> WhisperModel:
    """Loads the Whisper model into memory on first call and caches it."""
    global _whisper_model
    if _whisper_model is None:
        print(
            f"Loading Whisper '{WHISPER_MODEL_SIZE}' model "
            f"(device={WHISPER_DEVICE}, compute={WHISPER_COMPUTE_TYPE}) — first time only..."
        )
        _whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
    return _whisper_model


def load_and_chunk_audio(file_path: str,
                          chunk_size: int = CHUNK_SIZE,
                          chunk_overlap: int = CHUNK_OVERLAP) -> list:
    """
    Transcribes an audio file using the local faster-whisper model,
    then splits the transcript into vector-store-ready chunks.

    Returns a list of LangChain Document objects with metadata:
        {"source": file_path, "type": "audio", "language": <detected_lang>}

    Returns an empty list if transcription fails.
    """
    print(f"Transcribing audio: {file_path}...")

    try:
        model = _get_whisper_model()
        # segments is a lazy generator — materialise it immediately so the
        # audio file handle is released before any further processing (critical on Windows)
        segments, info = model.transcribe(file_path)
        segments = list(segments)
    except Exception as e:
        print(f"ERROR: Audio transcription failed for '{file_path}': {e}")
        traceback.print_exc()
        return []

    if not segments:
        print(f"WARNING: No speech detected in '{file_path}'.")
        return []

    full_text = " ".join(seg.text.strip() for seg in segments if seg.text.strip())
    detected_lang = getattr(info, "language", "unknown")
    print(f"Transcription complete. Detected language: '{detected_lang}'. "
          f"Total words ≈ {len(full_text.split())}.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.create_documents(
        texts=[full_text],
        metadatas=[{
            "source": file_path,
            "type": "audio",
            "language": detected_lang,
        }],
    )

    return chunks