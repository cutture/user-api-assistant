
import sys
import os
import pytest
from dotenv import load_dotenv

# Load env vars for all tests
load_dotenv()

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)

# Also add root to path?
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_path)

@pytest.fixture(scope="session", autouse=True)
def setup_path():
    pass
