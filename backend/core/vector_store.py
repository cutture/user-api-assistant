import chromadb
from chromadb.config import Settings
import os
from functools import lru_cache
from utils.timing import measure_time
from dotenv import load_dotenv

load_dotenv()

# Resolve Robust Path to project_root/data/chroma_db
# __file__ = backend/core/vector_store.py
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CORE_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

CHROMA_PATH = os.getenv("CHROMA_PATH", os.path.join(PROJECT_ROOT, "data", "chroma_db"))

class VectorStore:
    def __init__(self):
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        
        # Use a simple default embedding function for now (All-MiniLM-L6-v2)
        from chromadb.utils import embedding_functions
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # NOTE: We do NOT cache self.collection here.
        # ChromaDB collections become stale after delete/recreate.
        # Always fetch fresh via _get_collection().

    def _get_collection(self):
        """Always fetch the latest collection from client. This avoids stale references."""
        return self.client.get_or_create_collection(
            name="api_docs",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        """Adds documents to the Vector Store."""
        self._get_collection().add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Added {len(documents)} documents to ChromaDB.")

    @measure_time
    @lru_cache(maxsize=100)
    def query(self, query_text: str, n_results: int = 3):
        """
        Queries the vector store for relevant documents.
        Cached with LRU to speed up repeated queries for same context.
        """
        collection = self._get_collection()
        print(f"🔍 Querying Vector DB: '{query_text}'")
        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"⚠️ Vector Store Query Error: {e}")
            return None
        
    def reset(self):
        """Clears the entire Vector Store."""
        try:
            self.client.delete_collection("api_docs")
            # Next call to _get_collection() will recreate it.
            print("✅ Vector Store Reset Successfully.")
        except Exception as e:
            print(f"❌ Failed to reset Vector Store: {e}")

# Singleton Instance to be shared across modules
store = VectorStore()
