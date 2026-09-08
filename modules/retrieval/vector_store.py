from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

# Using a lightweight local embedding model perfect for offline RAG
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

def get_vector_store(persist_directory: str = "./my_vectordb"):
    """Initializes or loads the local ChromaDB vector store."""
    return Chroma(
        embedding_function=embedding_model,
        persist_directory=persist_directory
    )

def add_chunks_to_db(chunks, persist_directory: str = "./my_vectordb"):
    """Embeds and saves document chunks to the database."""
    vector_store = get_vector_store(persist_directory)
    vector_store.add_documents(documents=chunks)
    print(f"Successfully saved {len(chunks)} chunks to the vector database at {persist_directory}.")
    return vector_store