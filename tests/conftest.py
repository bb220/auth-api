import os
import pytest
import uuid
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from app.main import app

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {
        "x-api-key": API_KEY
    }

@pytest.fixture
def random_email():
    return f"testuser_{uuid.uuid4().hex[:8]}@example.com"