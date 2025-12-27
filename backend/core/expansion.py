
from typing import List
from langchain_core.messages import HumanMessage
from core.llm_client import LLMFactory

class QueryExpander:
    def __init__(self):
        self.llm = LLMFactory.create_llm("reasoning")
        
    def expand(self, original_query: str) -> List[str]:
        """
        Generates 2-3 semantic variations of the query to improve recall.
        Example: "Auth error" -> ["Authentication failure", "Login timeout", "401 Unauthorized"]
        """
        prompt = f"""
        You are an AI Search Optimizer.
        Task: Generate 2 alternative search queries for the user's input.
        Focus on: Synonyms, technical terms, and error codes related to the intent.
        
        User Query: "{original_query}"
        
        Output format: A simple list separated by newlines. NO numbering. NO explanations.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            # Split lines and clean
            variations = [line.strip().strip('- ') for line in response.content.split('\n') if line.strip()]
            # Limit to top 2 + original
            final_queries = [original_query] + variations[:2]
            # Dedupe
            return list(dict.fromkeys(final_queries))
            
        except Exception as e:
            print(f"⚠️ Query Expansion Failed: {e}")
            return [original_query]

# Singleton
expander = QueryExpander()
