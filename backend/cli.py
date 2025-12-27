
import typer
import sys
import os
from typing import Optional
from pathlib import Path
from termcolor import colored

# Add backend to path
sys.path.append(os.path.dirname(__file__))

# Import Core Modules
try:
    # When imported as backend.cli or from root with backend source
    from backend.core.hybrid import hybrid_retriever
    from backend.core.vector_store import store as vector_store
    from backend.core.parsers.factory import parser_factory
    from backend.core.sessions import session_manager
except ImportError:
    # Fallback for direct execution
    from core.hybrid import hybrid_retriever
    from core.vector_store import store as vector_store
    from core.parsers.factory import parser_factory
    from core.sessions import session_manager

app = typer.Typer(help="API Assistant CLI - Manage your Knowledge Base")
session_app = typer.Typer(help="Manage Chat Sessions")
app.add_typer(session_app, name="session")

@session_app.command("create")
def create_session_cmd(user_id: str = "cli_user"):
    s = session_manager.create_session(user_id)
    print(colored(f"✅ Session Created: {s.id}", "green"))

@session_app.command("list")
def list_sessions_cmd(user_id: str = None):
    sessions = session_manager.list_sessions(user_id)
    if not sessions:
        print("No sessions found.")
        return
    
    print(f"Found {len(sessions)} sessions:")
    for s in sessions:
        print(f"- {s.id} (User: {s.user_id}, Msgs: {len(s.messages)})")

@session_app.command("chat")
def chat_session_cmd(session_id: str):
    """
    Interactive chat within a session.
    """
    s = session_manager.get_session(session_id)
    if not s:
        print(colored("❌ Session not found", "red"))
        raise typer.Exit(1)
        
    print(colored(f"💬 Chatting in Session: {session_id}", "cyan"))
    print(colored("Type 'exit' or 'quit' to stop.", "yellow"))
    
    # Replay history
    for m in s.messages:
        color = "green" if m.role == "user" else "cyan"
        print(colored(f"{m.role.title()}: {m.content}", color))
        
    # Interactive Loop
    # Note: For CLI, we need to invoke the agent directly similar to API
    # To keep it DRY, we might want to call the API function or duplicate the logic slightly.
    # Calling API logic requires async context or direct agent invocation.
    
    # We will import agent graph (lazy load to avoid startup cost globally?)
    try:
        from backend.agent.graph import app_graph
        from langchain_core.messages import HumanMessage, AIMessage
    except ImportError:
        from agent.graph import app_graph
        from langchain_core.messages import HumanMessage, AIMessage
        
    while True:
        query = typer.prompt("You")
        if query.lower() in ["exit", "quit"]:
            break
            
        session_manager.add_message(session_id, "user", query)
        
        # Build history
        history_msgs = []
        # Reload session to get latest msg
        s = session_manager.get_session(session_id)
        for m in s.messages:
             if m.role == "user": history_msgs.append(HumanMessage(content=m.content))
             else: history_msgs.append(AIMessage(content=m.content))
             
        inputs = {
            "messages": history_msgs,
            "intent": "general", "context": [], "plan": "", "generated_code": "", "error": ""
        }
        
        print(colored("Thinking...", "magenta"))
        try:
            result = app_graph.invoke(inputs)
            response = result.get("generated_code", "")
            if not response: response = result.get("plan", "No response.")
            
            print(colored(f"Assistant: {response}", "cyan"))
            session_manager.add_message(session_id, "assistant", response)
            
        except Exception as e:
            print(colored(f"Error: {e}", "red"))

@app.command()
def search(
    query: str, 
    limit: int = 3, 
    filter_key: str = typer.Option(None, help="Metadata filter key"),
    filter_val: str = typer.Option(None, help="Metadata filter value")
):
    """
    Search the Knowledge Base using Hybrid Search.
    """
    print(colored(f"🔍 Searching for: '{query}'", "cyan"))
    
    filters = None
    if filter_key and filter_val:
        filters = {filter_key: filter_val}
        print(colored(f"🔎 Filter: {filters}", "yellow"))

    try:
        results = hybrid_retriever.search(query, n_results=limit, filters=filters)
        
        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        
        if not docs:
             print(colored("No results found.", "red"))
             return

        for i, (doc, doc_id) in enumerate(zip(docs, ids)):
            print("-" * 40)
            print(colored(f"Result {i+1} [ID: {doc_id}]", "green", attrs=["bold"]))
            print(doc[:300] + "..." if len(doc) > 300 else doc)
            
    except Exception as e:
        print(colored(f"❌ Error: {e}", "red"))

@app.command()
def parse(file_path: Path):
    """
    Debug: Parse a file and show generated chunks.
    Does NOT add to Vector Store.
    """
    if not file_path.exists():
        print(colored(f"❌ File not found: {file_path}", "red"))
        raise typer.Exit(code=1)

    print(colored(f"📂 Parsing: {file_path.name}", "cyan"))
    
    # Simple mime detection by extension for CLI
    mime_type = "text/plain"
    if file_path.suffix == ".json":
        mime_type = "application/json"
    elif file_path.suffix == ".graphql" or file_path.suffix == ".gql":
        mime_type = "application/graphql"
    elif file_path.name.endswith(".postman_collection.json"):
        mime_type = "application/vnd.postman.collection+json"

    parser = parser_factory.get_parser(mime_type)
    
    content = file_path.read_text(encoding="utf-8")
    
    if parser:
        print(colored(f"⚙️ Using Parser: {parser.__class__.__name__}", "green"))
        # Parse inputs
        parse_input = content
        if mime_type == "application/json" or "json" in mime_type:
            import json
            try:
                parse_input = json.loads(content)
            except:
                pass
        
        chunks = parser.parse(parse_input)
        print(f"✅ Generated {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"-- Chunk {i+1} --")
            print(chunk[:100].replace("\n", " ") + "...")
    else:
        print(colored(f"⚠️ No specific parser found for {mime_type}. Using raw text.", "yellow"))
        print(content[:200])

@app.command()
def reset():
    """
    ⚠️ DANGER: Reset and clear the entire Vector Store.
    """
    confirm = typer.confirm("Are you sure you want to delete all data?")
    if not confirm:
        print("Aborted.")
        raise typer.Exit()
    
    vector_store.reset()
    print(colored("✅ Vector Store Reset.", "green"))

@app.command()
def batch(directory: Path):
    """
    Recursively ingest all supported files in a directory.
    """
    if not directory.exists() or not directory.is_dir():
         print(colored(f"❌ Valid directory required: {directory}", "red"))
         raise typer.Exit(code=1)
    
    print(colored(f"📦 Batch Ingesting from: {directory}", "cyan"))
    
    import uuid
    
    stats = {"success": 0, "skipped": 0, "error": 0}
    
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            # Skip hidden, git, venv
            if ".git" in str(file_path): continue
            
            # Identify MIME
            mime_type = "text/plain"
            if file_path.suffix == ".json": mime_type = "application/json"
            elif file_path.suffix == ".graphql": mime_type = "application/graphql"
            # Add more...
            
            parser = parser_factory.get_parser(mime_type)
            if not parser and file_path.suffix not in [".txt", ".md"]:
                # specific parser check + fallback check
                # If no parser and not txt/md, skip
                stats["skipped"] += 1
                continue
            
            try:
                # Read
                content = file_path.read_text(encoding="utf-8")
                
                # Parse
                chunks = []
                if parser:
                    parse_input = content
                    if "json" in mime_type:
                        import json
                        try:
                            parse_input = json.loads(content)
                        except: pass
                    chunks = parser.parse(parse_input)
                else: 
                     # Fallback Text
                     from langchain_text_splitters import RecursiveCharacterTextSplitter
                     splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                     chunks = splitter.split_text(content)
                
                if chunks:
                    ids = [str(uuid.uuid4()) for _ in chunks]
                    metas = [{"source": file_path.name, "path": str(file_path)} for _ in chunks]
                    vector_store.add_documents(chunks, metas, ids)
                    print(f"✅ Added {file_path.name} ({len(chunks)} chunks)")
                    stats["success"] += 1
                else:
                    stats["skipped"] += 1
                    
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                stats["error"] += 1

    print(colored(f"\nBatch Complete. {stats}", "green"))

@app.command()
def diagram(
    file_path: Path, 
    type: str = typer.Option("sequence", help="Type: sequence, erd, auth"),
    path: str = typer.Option(None, help="Endpoint path (for sequence)"),
    method: str = typer.Option("GET", help="HTTP Method (for sequence)"),
    output: Path = typer.Option(None, help="Output file to save mermaid code")
):
    """
    Generate Mermaid.js diagrams from OpenAPI/Swagger JSON.
    """
    if not file_path.exists():
         print(colored(f"❌ File not found: {file_path}", "red"))
         raise typer.Exit(code=1)
    
    # Import Generator
    try:
        from backend.core.diagrams.generator import mermaid_generator
    except ImportError:
        from core.diagrams.generator import mermaid_generator

    import json
    try:
        spec = json.loads(file_path.read_text(encoding="utf-8"))
    except:
        print(colored("❌ Invalid JSON file. Only OpenAPI JSON is supported currently.", "red"))
        raise typer.Exit(code=1)

    diagram_code = ""
    print(colored(f"🎨 Generating {type} diagram...", "cyan"))
    
    if type == "sequence":
        if not path:
             print(colored("❌ --path is required for sequence diagrams.", "red"))
             raise typer.Exit(code=1)
        diagram_code = mermaid_generator.generate_sequence(spec, path, method)
        
    elif type == "erd":
        diagram_code = mermaid_generator.generate_erd(spec)
        
    elif type == "auth":
        diagram_code = mermaid_generator.generate_auth_flow(spec)
        
    else:
        print(colored(f"❌ Unknown type: {type}", "red"))
        raise typer.Exit(code=1)

    if output:
        output.write_text(diagram_code, encoding="utf-8")
        print(colored(f"✅ Saved to: {output}", "green"))
    else:
        print("-" * 20)
        print(diagram_code)
        print("-" * 20)

if __name__ == "__main__":
    app()
