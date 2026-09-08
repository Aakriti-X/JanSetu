import sys
from modules.llm.query_engine import ask_question
from modules.retrieval.vector_store import get_vector_store
from ingest_manager import ingest_file  # Import your unified router

def main():
    print("Welcome to your offline RAG system!")
    
    # Step 11: Check if a file was passed as a command-line argument
    if len(sys.argv) > 1:
        file_to_ingest = sys.argv[1]
        print(f"\n--- Ingesting New File: {file_to_ingest} ---")
        ingest_file(file_to_ingest)
        print("--- Ingestion Complete ---\n")

    # 1. Check if the database has data before starting
    vector_store = get_vector_store()
    if vector_store._collection.count() == 0:
        print("\nERROR: Vector database is empty. Run with a file to ingest it: python main.py <file_path>")
        return

    print("Database loaded successfully. Ready for queries!")

    # 2. Interactive Chat Loop
    while True:
        user_input = input("\nAsk a question about your files (or type 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
            
        print("Searching database and generating answer...")
        answer, sources = ask_question(user_input)
        
        print("\n=== ANSWER ===")
        print(answer)
        print("\n=== CITED SOURCES ===")
        
        for doc in sources:
            print(f"- {doc.metadata.get('source', 'Unknown')}: {doc.page_content[:75]}...")

if __name__ == "__main__":
    main()