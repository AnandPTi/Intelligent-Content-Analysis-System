# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_create_content():
    response = client.post(
        "/content",
        json={
            "text": "Example educational content",
            "metadata": {"subject": "science"},
            "tenant_id": "test-tenant"
        }
    )
    assert response.status_code == 200
    assert "id" in response.json()
    assert "analysis" in response.json()

def test_get_content():
    # First create content
    create_response = client.post(
        "/content",
        json={
            "text": "Test content",
            "metadata": {},
            "tenant_id": "test-tenant"
        }
    )
    content_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/content/{content_id}")
    assert response.status_code == 200
    assert response.json()["id"] == content_id

def test_search_content():
    response = client.post(
        "/content/search",
        json={
            "query": "example search",
            "tenant_id": "test-tenant",
            "filters": {}
        }
    )
    assert response.status_code == 200
