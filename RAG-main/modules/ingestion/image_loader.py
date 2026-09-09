import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import VISION_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

_IMAGE_PROMPT = (
    "Extract all readable text from this image. "
    "Then provide a detailed description of any charts, diagrams, tables, "
    "or visual data present. Be thorough."
)


def load_and_chunk_image(file_path: str,
                          chunk_size: int = CHUNK_SIZE,
                          chunk_overlap: int = CHUNK_OVERLAP) -> list:
    """
    Uses a local vision model (LLaVA via Ollama) to extract text and descriptions
    from an image file, then splits the output into vector-store-ready chunks.

    Returns a list of LangChain Document objects with metadata:
        {"source": file_path, "type": "image"}

    Returns an empty list if Ollama is unavailable or analysis fails.
    """
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
        extracted_text = response.message.content

    except ollama.ResponseError as e:
        # Model not pulled, or model name wrong
        print(
            f"ERROR: Ollama model '{VISION_MODEL}' returned an error: {e}\n"
            f"  Fix: Run  ollama pull {VISION_MODEL}  and try again."
        )
        return []
    except Exception as e:
        # Ollama not running, network error, corrupt image, etc.
        print(
            f"ERROR: Image analysis failed for '{file_path}': {e}\n"
            "  Make sure Ollama is running:  ollama serve"
        )
        return []

    if not extracted_text or not extracted_text.strip():
        print(f"WARNING: Vision model returned empty text for '{file_path}'.")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.create_documents(
        texts=[extracted_text],
        metadatas=[{"source": file_path, "type": "image"}],
    )

    print(f"Image processed into {len(chunks)} searchable chunk(s).")
    return chunks