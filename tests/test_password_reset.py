from app.verification_token_handler import create_email_verification_token
from app.reset_token_handler import create_password_reset_token
from unittest.mock import patch, ANY

def test_request_password_reset_sends_email(client, auth_headers, random_email):
    # First, register the user (patch send_verification_email to avoid real email)
    with patch("app.main.send_verification_email"):
        client.post("/register", json={
            "email": random_email,
            "password": "Test1234"
        }, headers=auth_headers)

    # Now patch send_reset_email for the password reset email
    with patch("app.main.send_reset_email") as mock_send_reset_email:
        response = client.post("/request-password-reset", params={"email": random_email}, headers=auth_headers)

        assert response.status_code == 200, response.json()
        mock_send_reset_email.assert_called_once_with(random_email, ANY)

def test_password_reset_flow(client, auth_headers, random_email):
    # Register and verify user
    client.post("/register", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)

    token = create_email_verification_token(random_email)
    client.get(f"/verify-email?token={token}", headers=auth_headers)

    # Request password reset
    client.post("/request-password-reset", params={"email": random_email}, headers=auth_headers)

    # Perform actual reset
    reset_token = create_password_reset_token(random_email)
    reset = client.post("/reset-password", params={
        "token": reset_token,
        "new_password": "NewTest1234"
    }, headers=auth_headers)
    
    assert reset.status_code == 200
    assert "successful" in reset.json()["message"].lower()