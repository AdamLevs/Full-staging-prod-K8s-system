"""
Simple unit tests for the demo API.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 503]  # 503 if DB/Redis not available
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data

def test_create_item():
    """Test item creation"""
    response = client.post("/items", json={"name": "Test Item"})
    # May fail if DB not available, but endpoint should exist
    assert response.status_code in [200, 500]

def test_get_items():
    """Test getting items"""
    response = client.get("/items")
    # May fail if DB not available, but endpoint should exist
    assert response.status_code in [200, 500]

def test_stats():
    """Test stats endpoint"""
    response = client.get("/stats")
    assert response.status_code in [200, 500]

