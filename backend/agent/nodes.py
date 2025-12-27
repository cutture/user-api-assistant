from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from core.vector_store import store as vector_store
from core.llm_client import LLMFactory
from agent.state import AgentState
from core.resilience import with_resilience

@with_resilience(max_retries=3)
def invoke_llm_safe(llm, messages):
    return llm.invoke(messages)

# --- SHIM for LangChain compatibility with recent duckduckgo-search ---
try:
    import duckduckgo_search
    import sys
    if "ddgs" not in sys.modules:
        sys.modules["ddgs"] = duckduckgo_search
except ImportError:
    pass
# ---------------------------------------------------------------------

from langchain_community.tools import DuckDuckGoSearchRun

# Initialize tools
# vector_store is imported as singleton
web_search = DuckDuckGoSearchRun() # Web Search Tool
reasoning_llm = LLMFactory.create_llm("reasoning")
coding_llm = LLMFactory.create_llm("coding")
chat_llm = LLMFactory.create_llm("chat")

import re
import requests
from bs4 import BeautifulSoup

def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 1: Research.
    Priorities:
    1. Extract & Scrape URLs from user message.
    2. Query Vector DB (ChromaDB).
    3. Fallback to Web Search (DuckDuckGo).
    """
    last_message = state["messages"][-1].content
    existing_context = state.get("context", []) or [] # Ensure it's a list
    new_documents = []
    
    print(f"🔍 Analyzing Request: {last_message[:50]}...")

    # A. Check for URLs
    urls = re.findall(r'https?://[^\s]+', last_message)
    if urls:
        print(f"🔗 Found URLs: {urls}")
        for url in urls:
            # 1. Filter out Search Engine URLs
            if "google.com" in url or "bing.com" in url or "search.yahoo" in url:
                print(f"   ⚠️ Skipping Search Engine URL: {url}")
                continue

            try:
                print(f"   Downloading: {url}")
                # 2. Robust Scraper (Impersonate Googlebot for better SPA access)
                headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
                resp = requests.get(url, timeout=15, headers=headers)
                
                scraped_content = ""
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    # Remove noise
                    for script in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
                        script.decompose()
                    
                    text = soup.get_text(separator=' ')
                    # Collapse whitespace
                    scraped_content = " ".join(text.split())
                    
                    # Stricter check for SPA/Blocked content
                    is_too_short = len(scraped_content) < 1000
                    has_js_warning = "enable javascript" in scraped_content.lower() or "javascript is required" in scraped_content.lower()
                    
                    if not is_too_short and not has_js_warning:
                         new_documents.append(f"Source URL: {url}\nContent:\n{scraped_content[:15000]}") # Increased limit
                         print(f"   ✅ Scrape Success ({len(scraped_content)} chars)")
                    else:
                        print(f"   ⚠️ Content unusable ({len(scraped_content)} chars, JS warning={has_js_warning}). Triggering fallback.")
                        scraped_content = "" # Force fallback
                else:
                    print(f"   ❌ Scrape Failed (Status {resp.status_code})")

                # 3. Fallback: Smart Search if Scrape Failed
                if not scraped_content:
                    print(f"   🔄 Triggering Fallback Search for URL: {url}")
                    
                    # Extract keywords from URL path
                    clean_url = url.split('?')[0] # Remove query params
                    last_segment = clean_url.rstrip('/').split('/')[-1]
                    
                    # If last segment is generic (index.html), take parent
                    if len(last_segment) < 5 or "index" in last_segment.lower():
                        last_segment = clean_url.rstrip('/').split('/')[-2]
                        
                    keywords = re.sub(r'[-_.]', ' ', last_segment)
                    # MORE TECHNICAL SEARCH QUERY
                    search_query = f"{keywords} API endpoints code example"
                    
                    print(f"   🕵️ Fallback Query: '{search_query}'")
                    
                    try:
                        search_res = web_search.invoke(search_query)
                        new_documents.append(f"Fallback Search Result for {url}:\nQuery: {search_query}\nResult: {search_res}")
                        print("   ✅ Fallback Search Success")
                    except Exception as e:
                        print(f"   ❌ Fallback Search Failed: {e}")

            except Exception as e:
                print(f"   ❌ Scrape Exception: {e}")
                new_documents.append(f"Source URL: {url}\nError: {str(e)}")

    # B. Query Vector DB
    results = vector_store.query(last_message, n_results=3)
    if results and results['documents']:
        for doc_list in results['documents']:
            new_documents.extend(doc_list)

    # C. Fallback to Web Search (General)
    if not new_documents and not urls:
        print("⚠️ No local docs or URLs. Searching the web...")
        try:
            search_prompt = f"""
            Task: Convert the following user request into a CONCISE, KEYWORD-FOCUSED web search query.
            User Request: {last_message}
            Output ONLY the search query string.
            """
            optimized_query = invoke_llm_safe(reasoning_llm, [HumanMessage(content=search_prompt)]).content.strip()
            print(f"🕵️ Optimized Search Query: {optimized_query}")
            
            search_result = web_search.invoke(optimized_query)
            new_documents.append(f"Web Search Result (Query: {optimized_query}): {search_result}")
        except Exception as e:
            print(f"❌ Web Search failed: {e}")
            
    combined_docs = existing_context + new_documents
    unique_docs = sorted(list(set(combined_docs)), key=lambda x: combined_docs.index(x))
    
    return {"context": unique_docs}

def get_smart_history(messages: list) -> str:
    """
    Implements Adaptive History Summarization:
    - Keeps First 3 messages (Root Context).
    - Keeps Last 3 messages (Immediate Context).
    - Summarizes the Middle messages to save tokens.
    """
    if len(messages) <= 10:
        # Return full history if short
        history_str = ""
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            history_str += f"{role}: {msg.content}\n"
        return history_str

    # Slice the conversation
    head = messages[:3]
    tail = messages[-3:]
    middle = messages[3:-3]
    
    # Format middle for summarization
    middle_str = ""
    for msg in middle:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        middle_str += f"{role}: {msg.content}\n"
        
    print(f"🧹 Summarizing {len(middle)} middle messages...")
    
    summary_prompt = f"""
    Summarize the following conversation log into a concise paragraph. 
    Focus ONLY on:
    1. Key technical decisions made.
    2. User requirements defined.
    3. Code structures established.
    Ignore chit-chat.
    
    Log:
    {middle_str}
    """
    
    try:
        summary = invoke_llm_safe(chat_llm, [HumanMessage(content=summary_prompt)]).content
    except Exception as e:
        print(f"❌ Summarization failed: {e}")
        summary = "Error generating summary."

    # Reconstruct History
    history_str = ""
    
    # Head
    for msg in head:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        history_str += f"{role}: {msg.content}\n"
        
    # Summary
    history_str += f"\n--- [Summary of Middle Conversation ({len(middle)} messages)] ---\n{summary}\n------------------------------------------------------\n\n"
    
    # Tail
    for msg in tail:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        history_str += f"{role}: {msg.content}\n"
        
    return history_str

def plan_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 2: Plan.
    Uses the Reasoning LLM to analyze the request and retrieved docs.
    Decides on the integration strategy, respecting user constraints (language, framework).
    """
    context_str = "\n\n".join(state["context"])
    
    # Use Smart History Slicing
    history_str = get_smart_history(state["messages"])
    
    prompt = f"""
    You are an Expert Software Architect.
    
    Chat History:
    {history_str}
    
    Available API Documentation Context:
    {context_str}
    
    Task:
    Analyze the *entire* conversation history and the documentation. 
    Determine if you have enough information to generate the code.
    
    CRITICAL DECISION:
    1. **CHECK HISTORY**: Is this a request to rewrite/translate code that ALREADY EXISTS in the Chat History?
       - **Yes (Code found in history)** -> STATUS: READY (Plan: Translate existing logic to [Target Language])

    2. **CHECK LANGUAGE**: Did the user request MULTIPLE languages (e.g. "Python and C#")?
       - **Yes** -> Your PLAN must explicitly list steps to generate code for ALL requested languages.
       
    3. **CHECK GAPS**: Do you have the specific API endpoints, parameters, and base URLs needed?
       - **Specific URLs/text provided in context?** -> STATUS: READY
       - **Good Web Search results?** -> STATUS: READY (Include "Note: Based on search results..." in plan)
       - **Ambiguous inputs?** -> STATUS: INCOMPLETE (Ask specific questions)
       - **Zero Info?** -> STATUS: INCOMPLETE
    
    Output Format:
    
    If READY (or APPROXIMATE):
    STATUS: READY
    PLAN:
    
    ```mermaid
    sequenceDiagram
        participant User
        participant App
        participant API
        User->>App: Request Action
        App->>API: Call Endpoint
        API-->>App: Return Data
    ```
    
    1. [Step-by-step implementation plan]
    
    If BLOCKED (Missing Base URL, Auth info, or specific endpoints):
    STATUS: INCOMPLETE
    QUESTION:
    [Ask 1-3 specific clarifying questions to narrow down the search. e.g. "I found multiple APIs for 'Acme'. Did you mean Acme V1 or V2?"]
    """
    
    response = invoke_llm_safe(reasoning_llm, [HumanMessage(content=prompt)])
    return {"plan": response.content}

def generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 3: Code.
    Uses the Coding LLM to generate the actual implementation based on the plan.
    """
    plan = state["plan"]
    context_str = "\n\n".join(state["context"])
    
    prompt = f"""
    You are a Senior Developer.
    
    Context:
    {context_str}
    
    Architect's Plan:
    {plan}
    
    Task:
    Write the complete, working code to implement the plan.
    
    CRITICAL INSTRUCTIONS:
    - Follow the Architect's Plan for LANGUAGE selection.
    - If Multi-Language is requested (e.g. Python AND C#), you MUST write separate code blocks for EACH language.
    - If the plan specifies JavaScript/Node.js, do NOT write Python.
    - Include comments.
    - Handle errors.
    
    """
    
    # Check for feedback (Self-Correction)
    feedback = state.get("feedback", "")
    if feedback and feedback != "PASS":
        print(f"🔄 Refining code based on feedback (Attempt {state.get('attempt_count', 0)})...")
        prompt += f"""
        PREVIOUS ATTEMPT REJECTED.
        
        Feedback from Code Reviewer:
        {feedback}
        
        Action:
        Rewrite the code to FIX the issues mentioned above.
        """

    prompt += "\nOutput ONLY the code block(s)."



    # SDK Mode Check
    if "SDK" in plan or "Library" in plan:
        prompt += """
        
        SPECIAL INSTRUCTION: SDK GENERATION REQUESTED.
        1. Encapsulate logic in a `Client` class.
        2. Use Pydantic models for request/response validation.
        3. Structure methods logically (e.g., `get_user`, `create_order`).
        4. Include a `config` parameter for API keys.
        """
    
    response = invoke_llm_safe(coding_llm, [HumanMessage(content=prompt)])
    return {"generated_code": response.content}

def validate_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 4: Critique (Self-Correction).
    Reviews the generated code for logical errors, security issues, and completeness.
    """
    code = state["generated_code"]
    attempt = state.get("attempt_count", 0)
    
    print(f"🕵️ Validating code (Attempt {attempt + 1})...")
    
    prompt = f"""
    You are a Senior Code Reviewer.
    Review the following code for:
    1. Syntax errors.
    2. Infinite loops.
    3. Hardcoded secrets/API keys (Security Risk).
    4. Missing imports.
    5. Logical correctness based on the user's intent.
    
    Code:
    {code}
    
    Output Format:
    - If the code looks correct and safe, output ONLY: PASS
    - If there are issues, list them clearly as bullet points.
    """
    
    feedback = invoke_llm_safe(coding_llm, [HumanMessage(content=prompt)]).content.strip()
    
    # Safety Check: If feedback contains "PASS", treat as pass.
    if "PASS" in feedback:
        feedback = "PASS"
    else:
        print(f"❌ Validation Failed: {feedback[:100]}...")
        
    return {"feedback": feedback, "attempt_count": attempt + 1}
