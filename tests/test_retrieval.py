import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from core.vector_store import VectorStore

def test_retrieval():
    print("🔍 Testing Retrieval Logic...")
    
    vs = VectorStore()
    
    query = "How do I connect with Pets API Post request?"
    print(f"Query: '{query}'")
    
    results = vs.query(query, n_results=5)
    
    if not results or not results['documents']:
        print("❌ No results found.")
        return

    print(f"Found {len(results['documents'][0])} documents.\n")
    
    for i, doc in enumerate(results['documents'][0]):
        meta = results['metadatas'][0][i]
        print(f"--- Result {i+1} (Source: {meta.get('source')}) ---")
        print(doc[:500] + "...") # Print start of doc
        
        if "Base URLs" in doc:
            print("✅ Contains Base URL info.")
        else:
            print("⚠️ MISSING Base URL info.")
            
        print("\n")

if __name__ == "__main__":
    test_retrieval()
