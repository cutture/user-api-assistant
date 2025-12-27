
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from core.hybrid import hybrid_retriever
from termcolor import colored

def demo_filtering():
    print(colored("🔍 Advanced Filtering Demo", "cyan", attrs=["bold"]))
    
    # query = "login errors type:guide"
    query = "api authentication source:manual"
    
    print(f"Query: '{query}'")
    print("-" * 40)
    
    # In a real scenario, we'd need documents with 'source' metadata.
    # Since our mock data might not have it, this demo mostly runs the valid code path.
    # But let's assume valid data exists or just show emptiness if none found.
    
    try:
        results = hybrid_retriever.search(query, n_results=3)
        
        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        
        if not docs:
            print(colored("No documents found (Expected if no data has 'source:manual' metadata).", "yellow"))
        else:
            for i, doc in enumerate(docs):
                print(f"Result {i+1} [ID: {ids[i]}]: {doc[:100]}...")
                
    except Exception as e:
        print(colored(f"❌ Error: {e}", "red"))

if __name__ == "__main__":
    demo_filtering()
