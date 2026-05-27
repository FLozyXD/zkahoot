from flask.testing import FlaskClient


# /api/auth/register
def test_valid_registration(client: FlaskClient, valid_user):
    response = client.post("/api/auth/register", json=valid_user)
    assert response.status_code == 200


def test_invalid_registration_short_password(
    client: FlaskClient, valid_user, short_password
):
    response = client.post(
        "/api/auth/register",
        json={"login": valid_user["login"], "password": short_password},
    )
    assert response.status_code == 400


def test_invalid_registration_empty_login(client: FlaskClient, valid_user, empty_login):
    response = client.post(
        "/api/auth/register",
        json={"login": empty_login, "password": valid_user["password"]},
    )
    assert response.status_code == 400


def test_unique_registration(client: FlaskClient, valid_user):
    client.post("/api/auth/register", json=valid_user)
    response = client.post("/api/auth/register", json=valid_user)
    assert response.status_code == 418  # UniqueViolation → I'm a teapot


# /api/auth/change-login
def test_valid_login_changing(client: FlaskClient, valid_user, new_valid_login):
    client.post("/api/auth/register", json=valid_user)
    response = client.post(
        "/api/auth/change-login",
        json={
            "login": valid_user["login"],
            "password": valid_user["password"],
            "new_login": new_valid_login,
        },
    )
    assert response.status_code == 200


def test_invalid_login_changing_wrong_password(
    client: FlaskClient, valid_user, new_valid_login, wrong_password
):
    client.post("/api/auth/register", json=valid_user)
    response = client.post(
        "/api/auth/change-login",
        json={
            "login": valid_user["login"],
            "password": wrong_password,
            "new_login": new_valid_login,
        },
    )
    assert response.status_code == 403


def test_invalid_login_changing_empty_new_login(
    client: FlaskClient, valid_user, empty_login
):
    client.post("/api/auth/register", json=valid_user)
    response = client.post(
        "/api/auth/change-login",
        json={
            "login": valid_user["login"],
            "password": valid_user["password"],
            "new_login": empty_login,
        },
    )
    assert response.status_code == 400


def test_invalid_login_changing_missing_new_login(client: FlaskClient, valid_user):
    client.post("/api/auth/register", json=valid_user)
    response = client.post(
        "/api/auth/change-login",
        json={"login": valid_user["login"], "password": valid_user["password"]},
    )
    assert response.status_code == 400


def test_duplicate_login_changing(client: FlaskClient, valid_user, another_user):
    client.post("/api/auth/register", json=valid_user)
    client.post("/api/auth/register", json=another_user)
    response = client.post(
        "/api/auth/change-login",
        json={
            "login": valid_user["login"],
            "password": valid_user["password"],
            "new_login": another_user["login"],
        },
    )
    assert response.status_code == 403


def test_change_login_nonexistent_user(
    client: FlaskClient, nonexistent_login, dummy_new_login
):
    response = client.post(
        "/api/auth/change-login",
        json={
            "login": nonexistent_login,
            "password": "test_password",  # пароль не проверяется, т.к. пользователь не найден
            "new_login": dummy_new_login,
        },
    )
    assert response.status_code == 404


# /api/auth/change-password
def test_valid_password_changing(client: FlaskClient, valid_user, new_valid_password):
    client.post("/api/auth/register", json=valid_user)
    response = client.post(
        "/api/auth/change-password",
        json={
            "login": valid_user["login"],
            "password": valid_user["password"],
            "new_password": new_valid_password,
        },
    )
    assert response.status_code == 200


def test_invalid_password_changing_wrong_old_password(
    client: FlaskClient, valid_user, new_valid_password, wrong_password
):
    client.post("/api/auth/register", json=valid_user)
    response = client.post(
        "/api/auth/change-password",
        json={
            "login": valid_user["login"],
            "password": wrong_password,
            "new_password": new_valid_password,
        },
    )
    assert response.status_code == 403


def test_invalid_password_changing_short_new_password(
    client: FlaskClient, valid_user, short_new_password
):
    client.post("/api/auth/register", json=valid_user)
    response = client.post(
        "/api/auth/change-password",
        json={
            "login": valid_user["login"],
            "password": valid_user["password"],
            "new_password": short_new_password,
        },
    )
    assert response.status_code == 400


def test_invalid_password_changing_missing_new_password(
    client: FlaskClient, valid_user
):
    client.post("/api/auth/register", json=valid_user)
    response = client.post(
        "/api/auth/change-password",
        json={"login": valid_user["login"], "password": valid_user["password"]},
    )
    assert response.status_code == 400


def test_change_password_nonexistent_user(
    client: FlaskClient, nonexistent_login, another_new_password
):
    response = client.post(
        "/api/auth/change-password",
        json={
            "login": nonexistent_login,
            "password": "test_password",  # пароль не проверяется
            "new_password": another_new_password,
        },
    )
    assert response.status_code == 404
