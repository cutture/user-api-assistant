
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

print(f"System Path: {sys.path}")

try:
    from backend.cli import app
    print("✅ Import Successful")
except Exception as e:
    import traceback
    traceback.print_exc()
