import requests
from langchain_ollama import OllamaLLM
from modules.retrieval.vector_store import get_vector_store

# Step 8: Cache the LLM so it initializes only once per session
_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        _llm = OllamaLLM(model="llama3")
    return _llm

def ask_question(question: str):
    # Step 10: Check if Ollama background server is running before attempting retrieval or inference
    try:
        requests.get("http://localhost:11434", timeout=2)
    except Exception:
        return "Ollama is not running. Please start Ollama before querying.", []

    # Retrieve the top 3 most relevant chunks from ChromaDB
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    
    # Step 3: Safety check if no documents match
    if not docs:
        return "I could not find any relevant information in the database.", []
    
    # Format retrieved chunks into a context string
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Force the LLM to strictly use the offline context
    prompt = f"""You are a secure, offline AI assistant. Answer the question based ONLY on the context below. 
If the answer is not in the context, say "I don't know."

Context:
{context}

Question: {question}
Answer:"""

    llm = _get_llm()
    response = llm.invoke(prompt)
    return response, docs