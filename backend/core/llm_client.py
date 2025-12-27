from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama
import os

from langchain_community.cache import SQLiteCache
from langchain_community.cache import SQLiteCache
import langchain
import os

# Enable Local Caching (Semantic Cache)
cache_db_path = os.path.join(os.path.dirname(__file__), "..", ".langchain.db")
langchain.llm_cache = SQLiteCache(database_path=cache_db_path)

class LLMFactory:
    @staticmethod
    def create_llm(model_type: str = "reasoning"):
        """
        Creates an LLM instance based on the .env config and the requested type.
        types: 'reasoning' (DeepSeek/R1), 'coding' (Qwen), 'chat' (Fast)
        """
        provider = os.getenv("LLM_PROVIDER", "groq").lower()
        
        if provider == "ollama":
            # FASTEST CONFIGURATION for 16GB RAM (Prevents Timeout)
            # Using 3B model for everything until performance is validated
            return ChatOllama(model="llama3.2:3b", temperature=0.7)
                
        else:
            # Default to Groq (Cloud)
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                print("❌ Error: GROQ_API_KEY is missing in .env")
                raise ValueError("GROQ_API_KEY not set in .env. Please add it to use Cloud Models.")
                
            if model_type == "coding":
                # Fallback to Llama 3.1 8B (Mixtral decommissioned, 70B rate limited)
                return ChatGroq(model="llama-3.1-8b-instant", api_key=api_key, temperature=0.1)
            elif model_type == "reasoning":
                # Fallback to Llama 3.1 8B
                return ChatGroq(model="llama-3.1-8b-instant", api_key=api_key, temperature=0.6)
            else:
                # Fast model for routine tasks
                return ChatGroq(model="llama-3.1-8b-instant", api_key=api_key, temperature=0.5)

# Singleton instance access pattern if needed
llm_factory = LLMFactory()
