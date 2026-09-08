from langchain_ollama import OllamaLLM
from modules.retrieval.vector_store import get_vector_store

def ask_question(question: str):
    # Connect to the local Llama 3 model downloaded via Ollama
    llm = OllamaLLM(model="llama3")
    
    # Retrieve the top 3 most relevant chunks from ChromaDB
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    
    # Format the retrieved chunks into a single context string
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Force the LLM to strictly use the offline context
    prompt = f"""You are a secure, offline AI assistant. Answer the question based ONLY on the context below. 
If the answer is not in the context, say "I don't know."

Context:
{context}

Question: {question}
Answer:"""

    response = llm.invoke(prompt)
    return response, docs