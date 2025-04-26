import os
import pytest
import uuid
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from app.main import app

load_dotenv()

client = TestClient(app)

# Shared test data
test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
test_password = "supersecurepassword"

# Shared headers for tests
headers = {
    "x-api-key": os.getenv("API_KEY")
}

def test_register_user():
    response = client.post("/register", json={
        "email": test_email,
        "password": test_password
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_email
    assert "id" in data

def test_login_unverified_user():
    response = client.post("/login", json={
        "email": test_email,
        "password": test_password
    }, headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Please verify your email before logging in."

def test_protected_route_without_token():
    response = client.get("/protected", headers=headers)
    assert response.status_code == 403  # Still missing Bearer token here

def test_protected_route_invalid_token():
    response = client.get("/protected", headers={
        **headers,
        "Authorization": "Bearer invalidtoken"
    })
    assert response.status_code == 401  # Now expecting token invalidation correctly
