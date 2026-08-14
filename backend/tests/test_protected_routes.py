def test_me_requires_auth(client):
    res = client.get("/api/users/me")
    assert res.status_code == 401


def test_me_with_valid_token(client, registered_user_token, test_user_payload):
    res = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {registered_user_token}"},
    )
    assert res.status_code == 200
    assert res.json()["email"] == test_user_payload["email"]


def test_me_with_invalid_token(client):
    res = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert res.status_code == 401


def test_admin_route_blocks_regular_user(client, registered_user_token):
    res = client.get(
        "/api/admin/analytics",
        headers={"Authorization": f"Bearer {registered_user_token}"},
    )
    assert res.status_code == 403