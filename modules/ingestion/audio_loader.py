from faster_whisper import WhisperModel
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Step 7: Cache the model outside the function so it only loads once per session
_whisper_model = None

def _get_whisper_model():
    """Loads the local Whisper model into memory if it hasn't been loaded yet."""
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model into memory (this only happens once)...")
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model

def load_and_chunk_audio(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    # Retrieve the cached model instead of loading it from scratch
    model = _get_whisper_model()
    
    print(f"Transcribing audio file: {file_path}...")
    segments, info = model.transcribe(file_path)
    
    full_text = " ".join([segment.text for segment in segments])
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.create_documents(
        texts=[full_text],
        metadatas=[{"source": file_path, "type": "audio"}]
    )
    return chunks