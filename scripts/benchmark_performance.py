
import sys
import os
import time

# Shim to run from root
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from backend.core.llm_client import LLMFactory
from langchain_core.messages import HumanMessage

def benchmark():
    print("🚀 Starting Benchmark: LLM Response Time")
    llm = LLMFactory.create_llm("chat")
    
    prompt = "What is the capital of France? Answer in one word."
    
    # 1. Cold Cache
    print("\n❄️ Cold Cache Request...")
    start = time.perf_counter()
    resp1 = llm.invoke([HumanMessage(content=prompt)]).content
    cold_time = time.perf_counter() - start
    print(f"   Result: {resp1}")
    print(f"   Time: {cold_time:.4f}s")
    
    # 2. Warm Cache
    print("\n🔥 Warm Cache Request (Identical Prompt)...")
    start = time.perf_counter()
    resp2 = llm.invoke([HumanMessage(content=prompt)]).content
    warm_time = time.perf_counter() - start
    print(f"   Result: {resp2}")
    print(f"   Time: {warm_time:.4f}s")
    
    # Analysis
    if warm_time < cold_time * 0.1:
        print("\n✅ CACHE HIT CONFIRMED! (Speedup > 10x)")
    else:
        print("\n⚠️ CACHE MISS or Slow Cache.")
        
    speedup = cold_time / warm_time if warm_time > 0 else 0
    print(f"\n📊 Summary:\n   Cold: {cold_time:.4f}s\n   Warm: {warm_time:.4f}s\n   Speedup: {speedup:.1f}x")

if __name__ == "__main__":
    benchmark()
