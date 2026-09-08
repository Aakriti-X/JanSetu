from faster_whisper import WhisperModel
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_chunk_audio(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    # Load the optimized local Whisper model
    model = WhisperModel("base", device="cpu", compute_type="int8")
    
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