import ollama
import easyocr
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import VISION_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

_IMAGE_PROMPT = (
    "Provide a detailed description of any charts, diagrams, tables, "
    "or visual data present in this image. Be thorough."
)

_reader = None

def _get_ocr_reader():
    global _reader
    if _reader is None:
        print("Loading EasyOCR model...")
        _reader = easyocr.Reader(['en'])
    return _reader

def load_and_chunk_image(file_path: str,
                          chunk_size: int = CHUNK_SIZE,
                          chunk_overlap: int = CHUNK_OVERLAP) -> list:
    """
    Uses EasyOCR to extract exact text from an image file, and a local vision model 
    (LLaVA via Ollama) to extract descriptions, then splits the output into 
    vector-store-ready chunks.
    """
    print(f"Extracting text via EasyOCR for: {file_path}...")
    try:
        reader = _get_ocr_reader()
        ocr_result = reader.readtext(file_path, detail=0)
        ocr_text = "\n".join(ocr_result)
    except Exception as e:
        print(f"WARNING: OCR failed for '{file_path}': {e}")
        ocr_text = ""

    print(f"Analyzing image with local '{VISION_MODEL}' model: {file_path}...")
    try:
        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": _IMAGE_PROMPT,
                    "images": [file_path],
                }
            ],
        )
        vision_text = response.message.content
    except ollama.ResponseError as e:
        print(
            f"ERROR: Ollama model '{VISION_MODEL}' returned an error: {e}\n"
            f"  Fix: Run  ollama pull {VISION_MODEL}  and try again."
        )
        vision_text = ""
    except Exception as e:
        print(
            f"ERROR: Image analysis failed for '{file_path}': {e}\n"
            "  Make sure Ollama is running:  ollama serve"
        )
        vision_text = ""

    combined_text = f"--- OCR Text ---\n{ocr_text}\n\n--- Visual Description ---\n{vision_text}"

    if not combined_text.strip() or combined_text.strip() == "--- OCR Text ---\n\n\n--- Visual Description ---":
        print(f"WARNING: Could not extract any text or description for '{file_path}'.")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.create_documents(
        texts=[combined_text],
        metadatas=[{"source": file_path, "type": "image"}],
    )

    print(f"Image processed into {len(chunks)} searchable chunk(s).")
    return chunks