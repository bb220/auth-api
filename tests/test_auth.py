from unittest.mock import patch, ANY

def test_access_without_api_key(client):
    response = client.get("/register")  # No headers

    assert response.status_code == 403 
    assert "Forbidden. Invalid or missing API Key." in response.json()["detail"]

def test_register_user(client, auth_headers, random_email):
    response = client.post("/register", json={
        "email": random_email,
        "password": "SuperSecurePassword123"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data

def test_register_sends_verification_email(client, auth_headers, random_email):
    with patch("app.main.send_verification_email") as mock_send_email:
        response = client.post("/register", json={
            "email": random_email,
            "password": "Test1234"
        }, headers=auth_headers)

        assert response.status_code == 200, response.json()
        mock_send_email.assert_called_once_with(random_email, ANY)

def test_register_duplicate_email(client, auth_headers, random_email):
    client.post("/register", json={
        "email": random_email,
        "password": "Password123"
    }, headers=auth_headers)

    response = client.post("/register", json={
        "email": random_email,
        "password": "AnotherPassword456"
    }, headers=auth_headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_unverified_user(client, auth_headers, random_email):
    client.post("/register", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)
    response = client.post("/login", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)
    assert response.status_code == 403

def test_login_invalid_password(client, auth_headers, random_email):
    client.post("/register", json={
        "email": random_email,
        "password": "CorrectPassword123"
    }, headers=auth_headers)

    response = client.post("/login", json={
        "email": random_email,
        "password": "WrongPassword456"
    }, headers=auth_headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_email_not_found(client, auth_headers):
    response = client.post("/login", json={
        "email": "nonexistentuser@example.com",
        "password": "DoesNotMatter123"
    }, headers=auth_headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_successful(client, auth_headers, random_email):
    from app.verification_token_handler import create_email_verification_token

    # 1. Register user
    client.post("/register", json={
        "email": random_email,
        "password": "SuperSecurePassword123"
    }, headers=auth_headers)

    # 2. Verify user
    token = create_email_verification_token(random_email)
    client.get(f"/verify-email?token={token}", headers=auth_headers)

    # 3. Login with correct credentials
    response = client.post("/login", json={
        "email": random_email,
        "password": "SuperSecurePassword123"
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_protected_route_without_token(client, auth_headers):
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 403

def test_protected_route_with_invalid_token(client, auth_headers):
    invalid_headers = {
        **auth_headers,
        "Authorization": "Bearer invalidtoken123"
    }
    response = client.get("/protected", headers=invalid_headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token."

def test_protected_route_with_valid_token(client, auth_headers, random_email):
    from app.verification_token_handler import create_email_verification_token

    # 1. Register user
    client.post("/register", json={
        "email": random_email,
        "password": "SecurePassword123"
    }, headers=auth_headers)

    # 2. Verify user
    token = create_email_verification_token(random_email)
    client.get(f"/verify-email?token={token}", headers=auth_headers)

    # 3. Login to get access token
    login = client.post("/login", json={
        "email": random_email,
        "password": "SecurePassword123"
    }, headers=auth_headers)
    tokens = login.json()

    # 4. Access protected route with valid token
    protected_headers = {
        **auth_headers,
        "Authorization": f"Bearer {tokens['access_token']}"
    }
    protected_response = client.get("/protected", headers=protected_headers)

    assert protected_response.status_code == 200
    assert "Welcome user" in protected_response.json()["message"]
