import sys
from pathlib import Path
import csv
import tqdm

# Add backend to path so we can import core modules
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from core.vector_store import VectorStore

DATA_DIR = Path("../data/raw")
CSV_FILE = DATA_DIR / "api_data.csv"

def main():
    print("🚀 Starting Ingestion Process (CSV Catalog)...")
    
    if not CSV_FILE.exists():
        print(f"❌ Error: {CSV_FILE} not found. Did the download finish?")
        return

    vector_store = VectorStore()
    
    documents = []
    metadatas = []
    ids = []
    
    BATCH_SIZE = 20
    
    print(f"📂 processing {CSV_FILE}...")
    
    with open(CSV_FILE, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"📊 Found {len(rows)} APIs in catalog.")
        
        for i, row in enumerate(tqdm.tqdm(rows, unit="api")):
            # Construct meaningful text for embedding
            # "API: Cat Facts\nCategory: Animals\nDescription: Daily cat facts"
            text_content = (
                f"API: {row.get('API', 'Unknown')}\n"
                f"Category: {row.get('Category', 'Uncategorized')}\n"
                f"Description: {row.get('Description', '')}\n"
                f"Auth: {row.get('Auth', 'None')}"
            )
            
            # Metadata for retrieval filter/context
            meta = {
                "source": "api_data.csv",
                "title": row.get("API", "Unknown"),
                "link": row.get("Link", ""),
                "category": row.get("Category", ""),
                "auth": row.get("Auth", "")
            }
            
            documents.append(text_content)
            metadatas.append(meta)
            ids.append(f"api_{i}")
            
            # Batch flush
            if len(documents) >= BATCH_SIZE:
                vector_store.add_documents(documents, metadatas, ids)
                documents = []
                metadatas = []
                ids = []

    # Final flush
    if documents:
        vector_store.add_documents(documents, metadatas, ids)

    print("✅ Ingestion Complete! API Catalog is indexed in ChromaDB.")

if __name__ == "__main__":
    main()
