VALID_SYMPTOMS = {
    "age": 34,
    "swollen_lymph_nodes": "MODERATE",
    "fever": "MILD",
    "night_sweats": "NOT_PRESENT",
    "weight_loss": "MILD",
    "fatigue": "MODERATE",
    "itching": "NOT_PRESENT",
    "shortness_of_breath": "NOT_PRESENT",
    "chest_discomfort": "NOT_PRESENT",
    "cough": "NOT_PRESENT",
    "abdominal_symptoms": "NOT_PRESENT",
    "loss_of_appetite": "MILD",
}


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_assessment_requires_auth(client):
    res = client.post("/api/assessments", json={"symptoms": VALID_SYMPTOMS})
    assert res.status_code == 401


def test_create_assessment_success(client, registered_user_token):
    res = client.post(
        "/api/assessments",
        json={"symptoms": VALID_SYMPTOMS},
        headers=auth_headers(registered_user_token),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["symptoms"]["age"] == 34
    assert "prediction" in body


def test_create_assessment_invalid_age_fails(client, registered_user_token):
    bad_symptoms = {**VALID_SYMPTOMS, "age": 200}
    res = client.post(
        "/api/assessments",
        json={"symptoms": bad_symptoms},
        headers=auth_headers(registered_user_token),
    )
    assert res.status_code == 422


def test_list_assessments(client, registered_user_token):
    client.post(
        "/api/assessments",
        json={"symptoms": VALID_SYMPTOMS},
        headers=auth_headers(registered_user_token),
    )
    res = client.get("/api/assessments", headers=auth_headers(registered_user_token))
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_assessment_by_id(client, registered_user_token):
    create_res = client.post(
        "/api/assessments",
        json={"symptoms": VALID_SYMPTOMS},
        headers=auth_headers(registered_user_token),
    )
    assessment_id = create_res.json()["id"]

    res = client.get(f"/api/assessments/{assessment_id}", headers=auth_headers(registered_user_token))
    assert res.status_code == 200
    assert res.json()["id"] == assessment_id


def test_get_nonexistent_assessment_404(client, registered_user_token):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/api/assessments/{fake_id}", headers=auth_headers(registered_user_token))
    assert res.status_code == 404


def test_cannot_access_other_users_assessment(client, test_user_payload):
    client.post("/api/auth/register", json=test_user_payload)
    login_a = client.post(
        "/api/auth/login",
        data={"grant_type": "password", "username": test_user_payload["email"], "password": test_user_payload["password"]},
    )
    token_a = login_a.json()["access_token"]

    create_res = client.post(
        "/api/assessments",
        json={"symptoms": VALID_SYMPTOMS},
        headers=auth_headers(token_a),
    )
    assessment_id = create_res.json()["id"]

    user_b_payload = {**test_user_payload, "email": "userb@example.com"}
    client.post("/api/auth/register", json=user_b_payload)
    login_b = client.post(
        "/api/auth/login",
        data={"grant_type": "password", "username": user_b_payload["email"], "password": user_b_payload["password"]},
    )
    token_b = login_b.json()["access_token"]

    res = client.get(f"/api/assessments/{assessment_id}", headers=auth_headers(token_b))
    assert res.status_code == 404