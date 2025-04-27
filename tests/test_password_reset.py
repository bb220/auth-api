def test_password_reset_flow(client, auth_headers, random_email):
    from app.verification_token_handler import create_email_verification_token
    from app.reset_token_handler import create_password_reset_token

    client.post("/register", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)

    token = create_email_verification_token(random_email)
    client.get(f"/verify-email?token={token}", headers=auth_headers)

    client.post("/request-password-reset", params={"email": random_email}, headers=auth_headers)

    reset_token = create_password_reset_token(random_email)

    reset = client.post("/reset-password", params={
        "token": reset_token,
        "new_password": "NewTest1234"
    }, headers=auth_headers)
    
    assert reset.status_code == 200
    assert "successful" in reset.json()["message"].lower()

