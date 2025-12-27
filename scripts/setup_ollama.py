import subprocess
import sys
import time

# Define the models we need for the Agentic Mesh
REQUIRED_MODELS = [
    "llama3.2:3b",        # Chat / Context / Intent
    "qwen2.5-coder:7b",   # Coding Agent
    "deepseek-r1:7b"      # Reasoning / Planning Agent
]

def pull_model(model_name):
    print(f"⬇️ Pulling model: {model_name}...")
    try:
        # Stream output to console
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        for line in process.stdout:
            print(line, end="")
            
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"❌ Failed to pull {model_name}")
            return False
            
    except FileNotFoundError:
        print("❌ Error: 'ollama' command not found. Is Ollama installed and added to PATH?")
        return False

def main():
    print("🦙 Initializing Ollama Model Setup...")
    print("Make sure Ollama is running in the background!")
    
    for model in REQUIRED_MODELS:
        success = pull_model(model)
        if not success:
            print("⚠️ Stopping setup due to error.")
            sys.exit(1)
            
    print("\n✨ All models are ready! You can now set LLM_PROVIDER=ollama in your .env file.")

if __name__ == "__main__":
    main()
