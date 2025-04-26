# tests/test_auth.py

def test_register_user(client, auth_headers, random_email):
    response = client.post("/register", json={
        "email": random_email,
        "password": "SuperSecurePassword123"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data

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
