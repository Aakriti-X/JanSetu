import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
import sys

def load_and_chunk_pdf(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    doc = pymupdf.open(file_path)
    full_text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if text:
            full_text += f"\n--- Page {page_num + 1} ---\n" + text

    # Split text into overlapping chunks for semantic retrieval
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.create_documents(
        texts=[full_text],
        metadatas=[{"source": file_path, "type": "pdf"}]
    )
    return chunks

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python doc_loader.py <path_to_pdf>")
    else:
        file_path = sys.argv[1]
        print(f"Loading and chunking {file_path}...")
        chunks = load_and_chunk_pdf(file_path)
        print(f"Created {len(chunks)} chunks.")
        if chunks:
            print(f"Sample chunk: {chunks[0].page_content[:200]}...")