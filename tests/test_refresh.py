def test_refresh_access_token(client, auth_headers, random_email):
    from app.verification_token_handler import create_email_verification_token

    client.post("/register", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)
    
    token = create_email_verification_token(random_email)
    client.get(f"/verify-email?token={token}", headers=auth_headers)

    login = client.post("/login", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)
    tokens = login.json()

    refresh = client.post("/refresh", json=tokens["refresh_token"], headers=auth_headers)
    
    assert refresh.status_code == 200
    assert "access_token" in refresh.json()
