from modules.llm.query_engine import ask_question

def main():
    print("Welcome to your offline RAG system!")
    print("Note: Skipping ingestion because my_vectordb already exists.")

    while True:
        user_input = input("\nAsk a question about your PDF (or type 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
            
        print("Searching database and generating answer...")
        answer, sources = ask_question(user_input)
        
        print("\n=== ANSWER ===")
        print(answer)
        print("\n=== CITED SOURCES ===")
        for i, doc in enumerate(sources):
            # Proves to judges that the system knows exactly where the data came from
            print(f"- {doc.metadata.get('source', 'Unknown')}: {doc.page_content[:75]}...")

if __name__ == "__main__":
    main()