import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

import pytest
from typer.testing import CliRunner
from backend.cli import app
from unittest.mock import patch

runner = CliRunner()

@patch("backend.cli.hybrid_retriever")
def test_search_command(mock_retriever):
    mock_retriever.search.return_value = {
        "documents": [["Test Doc content"]], 
        "ids": [["1"]]
    }
    
    result = runner.invoke(app, ["search", "test query"])
    assert result.exit_code == 0
    assert "Searching for: 'test query'" in result.stdout
    assert "Test Doc content" in result.stdout

@patch("backend.cli.vector_store")
def test_reset_command(mock_store):
    # Test Abort
    result = runner.invoke(app, ["reset"], input="n\n")
    assert result.exit_code == 0
    assert "Aborted" in result.stdout
    mock_store.reset.assert_not_called()
    
    # Test Confirm
    result = runner.invoke(app, ["reset"], input="y\n")
    assert result.exit_code == 0
    assert "Vector Store Reset" in result.stdout
    mock_store.reset.assert_called_once()

# Parse Test requires a real file or complex mocking
# We skip for now or verify functionality manually via script
