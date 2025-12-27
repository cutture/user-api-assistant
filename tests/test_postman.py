
import pytest
import json
from backend.utils.postman import convert_to_postman_collection

def test_postman_export_from_code():
    code = """
    import requests
    
    def get_pets():
        resp = requests.get("https://api.petstore.com/v1/pets")
        return resp.json()
        
    def create_pet():
        requests.post("https://api.petstore.com/v1/pets", json={"name": "fluffy"})
    """
    
    collection = convert_to_postman_collection("Plan: do stuff", code)
    
    assert collection["info"]["name"] == "API Assistant Generated Collection"
    assert len(collection["item"]) == 2
    
    item1 = collection["item"][0]
    assert item1["request"]["method"] == "GET"
    assert item1["request"]["url"]["raw"] == "https://api.petstore.com/v1/pets"
    
    item2 = collection["item"][1]
    assert item2["request"]["method"] == "POST"

def test_postman_fallback_plan():
    plan = """
    1. Call GET https://api.exa.com/search
    2. Then POST /analyze
    """
    collection = convert_to_postman_collection(plan, "")
    
    assert len(collection["item"]) >= 1
    # Check if regex caught valid URLs
