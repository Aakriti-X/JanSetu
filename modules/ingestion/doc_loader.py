import pymupdf as fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_chunk_pdf(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    doc = fitz.open(file_path)
    all_chunks = []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    for page_num in range(len(doc)):
        text = doc.load_page(page_num).get_text()
        if text:
            # Step 5: Add precise page numbers to the metadata
            page_chunks = splitter.create_documents(
                texts=[text],
                metadatas=[{"source": file_path, "type": "pdf", "page": page_num + 1}]
            )
            all_chunks.extend(page_chunks)
            
    # Step 6: Close the file handle to prevent leaks
    doc.close() 
    return all_chunks