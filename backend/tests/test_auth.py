def test_register_success(client, test_user_payload):
    res = client.post("/api/auth/register", json=test_user_payload)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == test_user_payload["email"]
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email_fails(client, test_user_payload):
    client.post("/api/auth/register", json=test_user_payload)
    res = client.post("/api/auth/register", json=test_user_payload)
    assert res.status_code == 409


def test_register_weak_password_fails(client, test_user_payload):
    payload = {**test_user_payload, "email": "other@example.com", "password": "allletters"}
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 422


def test_login_success(client, test_user_payload):
    client.post("/api/auth/register", json=test_user_payload)
    res = client.post(
        "/api/auth/login",
        data={
            "grant_type": "password",
            "username": test_user_payload["email"],
            "password": test_user_payload["password"],
        },
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password_fails(client, test_user_payload):
    client.post("/api/auth/register", json=test_user_payload)
    res = client.post(
        "/api/auth/login",
        data={
            "grant_type": "password",
            "username": test_user_payload["email"],
            "password": "wrongpassword1",
        },
    )
    assert res.status_code == 401


def test_login_nonexistent_user_fails(client):
    res = client.post(
        "/api/auth/login",
        data={
            "grant_type": "password",
            "username": "nobody@example.com",
            "password": "whatever123",
        },
    )
    assert res.status_code == 401