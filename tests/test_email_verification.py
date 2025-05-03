def test_verify_email_flow(client, auth_headers, random_email):
    from app.verification_token_handler import create_email_verification_token

    # 1. Register user
    register = client.post("/register", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)
    assert register.status_code == 200

    # 2. Create a valid verification token
    token = create_email_verification_token(random_email)

    # 3. Verify email
    verify = client.get(f"/verify-email?token={token}", headers=auth_headers)
    assert verify.status_code == 200
    assert "verified" in verify.json()["message"].lower()

def test_resend_verification_email(client, auth_headers, random_email):
    # 1. Register user
    register = client.post("/register", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)
    assert register.status_code == 200

    # 2. Request to resend
    resend = client.post("/resend-verification-email", json={"email": random_email}, headers=auth_headers)
    assert resend.status_code == 200
    assert "verification email" in resend.json()["message"].lower()

def test_verify_with_invalid_token(client, auth_headers):
    # 1. Try to verify with an obviously invalid token
    verify = client.get("/verify-email?token=invalid_token", headers=auth_headers)
    assert verify.status_code == 400
    assert "invalid or expired" in verify.json()["detail"].lower()

def test_verify_already_verified_user(client, auth_headers, random_email):
    from app.verification_token_handler import create_email_verification_token

    # 1. Register user
    client.post("/register", json={
        "email": random_email,
        "password": "Test1234"
    }, headers=auth_headers)

    # 2. Create token
    token = create_email_verification_token(random_email)

    # 3. First verification attempt (valid)
    client.get(f"/verify-email?token={token}", headers=auth_headers)

    # 4. Try to verify again (should return message about already verified)
    second_attempt = client.get(f"/verify-email?token={token}", headers=auth_headers)
    assert second_attempt.status_code == 200
    assert "already verified" in second_attempt.json()["message"].lower()
