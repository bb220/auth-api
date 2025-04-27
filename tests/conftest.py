import os

os.environ["DATABASE_URL"] = "sqlite:///test.db"

import uuid
import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.database import get_db

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")

# --- Test DB Setup ---
engine = create_engine(
    os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the DB override
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {
        "x-api-key": API_KEY
    }

@pytest.fixture(autouse=True)
def mock_sendgrid_emails():
    with patch("app.email_sender.send_verification_email") as mock_verify_email, \
         patch("app.email_sender.send_reset_email") as mock_reset_email:
        mock_verify_email.return_value = None
        mock_reset_email.return_value = None
        yield

@pytest.fixture
def random_email():
    return f"testuser_{uuid.uuid4().hex[:8]}@example.com"
