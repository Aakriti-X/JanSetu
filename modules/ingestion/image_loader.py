import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_chunk_image(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    print(f"Analyzing image with local LLaVA model: {file_path}...")
    
    # Prompt the local vision model to perform OCR and describe visual context
    response = ollama.chat(
        model='llava',
        messages=[
            {
                'role': 'user',
                'content': 'Extract all readable text from this image and provide a detailed description of any charts, diagrams, or visual data present.',
                'images': [file_path]
            }
        ]
    )
    
    extracted_text = response['message']['content']
    
    # Split the description into chunks for vector indexing
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.create_documents(
        texts=[extracted_text],
        metadatas=[{"source": file_path, "type": "image"}]
    )
    
    print(f"Successfully processed image into {len(chunks)} searchable chunks.")
    return chunks