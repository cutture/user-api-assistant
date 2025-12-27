import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from core.text_splitter import APIDocSplitter

def test_splitting_logic():
    print("🧪 Testing JSON Splitting Logic...")
    
    # Load Data
    json_path = os.path.join(os.path.dirname(__file__), "data", "petstore.json")
    with open(json_path, "r", encoding="utf-8") as f:
        json_content = json.load(f)
    
    content_str = json.dumps(json_content, indent=2)
    
    splitter = APIDocSplitter()
    
    # 1. Simulate Current Faulty Logic (Naive String Split)
    from langchain_core.documents import Document
    input_doc = Document(page_content=content_str, metadata={"source": "petstore.json"})
    naive_chunks = splitter.base_splitter.split_documents([input_doc])
    
    print(f"\n[Naive Splitter] Generated {len(naive_chunks)} chunks.")
    print(f"Sample Chunk 0: {naive_chunks[0].page_content[:200]}...")
    
    # Check if "POST /pets" is well-bounded
    found_post = False
    for chunk in naive_chunks:
        if '"operationId": "createPet"' in chunk.page_content and "requestBody" in chunk.page_content:
            found_post = True
            break
            
    if not found_post:
        print("❌ FAILURE: Naive splitter likely split the 'createPet' operation across chunks!")
    else:
        print("⚠️ WARNING: Naive splitter found it, but context might be messy.")

    # 2. Test Smart Logic (split_json_spec)
    smart_chunks = splitter.split_json_spec(json_content)
    print(f"\n[Smart Splitter] Generated {len(smart_chunks)} chunks.")
    
    # Verify strict endpoint isolation
    post_chunk = next((c for c in smart_chunks if "Endpoint: POST /pets" in c), None)
    
    if post_chunk:
        print("✅ SUCCESS: Found explicit 'POST /pets' chunk.")
        print("-" * 40)
        print(post_chunk)
        print("-" * 40)
    else:
        print("❌ FAILURE: Smart splitter missed the endpoint.")

if __name__ == "__main__":
    test_splitting_logic()
