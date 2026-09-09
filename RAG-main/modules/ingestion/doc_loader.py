import os
import tempfile
import pymupdf as fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP


def load_and_chunk_pdf(file_path: str,
                        chunk_size: int = CHUNK_SIZE,
                        chunk_overlap: int = CHUNK_OVERLAP) -> list:
    """
    Opens a PDF file, extracts text page-by-page, and splits it into chunks.
    If no text is found (scanned/image-based PDF), falls back to rendering each
    page as an image and running it through the LLaVA vision model for OCR.

    Returns a list of LangChain Document objects with metadata:
        {"source": file_path, "type": "pdf", "page": <page_number>}

    Returns an empty list if the file cannot be opened or contains no text.
    """
    try:
        doc = fitz.open(file_path)
    except fitz.FileDataError as e:
        print(f"ERROR: Cannot open PDF '{file_path}' — corrupt or password-protected: {e}")
        return []
    except Exception as e:
        print(f"ERROR: Unexpected error opening '{file_path}': {e}")
        return []

    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    try:
        for page_num in range(len(doc)):
            text = doc.load_page(page_num).get_text()
            if isinstance(text, str) and text.strip():
                page_chunks = splitter.create_documents(
                    texts=[text],
                    metadatas=[{
                        "source": file_path,
                        "type": "pdf",
                        "page": page_num + 1,
                    }],
                )
                all_chunks.extend(page_chunks)
    finally:
        doc.close()

    if not all_chunks:
        print(f"WARNING: No extractable text in '{file_path}'. "
              "Attempting OCR via LLaVA vision model (this may take a while)...")
        all_chunks = _ocr_pdf_with_llava(file_path, splitter)

    return all_chunks


def _ocr_pdf_with_llava(file_path: str, splitter: RecursiveCharacterTextSplitter,
                         max_pages: int = 5) -> list:
    """
    Renders each page of a scanned PDF as a PNG and sends it to LLaVA for OCR.
    Processes up to max_pages pages to avoid hanging on large documents.
    Returns chunked Document objects tagged with the original PDF source.
    """
    from modules.ingestion.image_loader import load_and_chunk_image

    all_chunks = []
    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        pages_to_process = min(total_pages, max_pages)
        print(f"  OCR: Processing {pages_to_process}/{total_pages} page(s) through LLaVA...")

        with tempfile.TemporaryDirectory() as tmpdir:
            for page_num in range(pages_to_process):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR accuracy
                pix = page.get_pixmap(matrix=mat)
                img_path = os.path.join(tmpdir, f"page_{page_num + 1}.png")
                pix.save(img_path)

                print(f"  OCR: Page {page_num + 1}/{pages_to_process}...")
                page_chunks = load_and_chunk_image(img_path)
                for chunk in page_chunks:
                    chunk.metadata["source"] = file_path
                    chunk.metadata["type"] = "pdf_ocr"
                    chunk.metadata["page"] = page_num + 1
                all_chunks.extend(page_chunks)

        doc.close()
    except Exception as e:
        print(f"ERROR: OCR fallback failed for '{file_path}': {e}")

    if all_chunks:
        print(f"  OCR complete: {len(all_chunks)} chunk(s) extracted.")
    else:
        print(f"  OCR returned no text from '{file_path}'.")

    return all_chunks