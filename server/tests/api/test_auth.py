import pytest
from flask.testing import FlaskClient

# HTTP статусы
OK = 200
BAD = 400
FORBIDDEN = 403
NOT_FOUND = 404
TEAPOT = 418

# Константы тестовых данных
LOGIN = "client0"
PASSWORD = "test_password"
OTHER_LOGIN = "client1"
OTHER_PASSWORD = "87654321"
NEW_LOGIN = "client_new"
NEW_PASSWORD = "newsecurepass123"
WRONG_PASSWORD = "wrongpassword"
SHORT_PASSWORD = "1234567"
NONEXISTENT_LOGIN = "ghost"


def register_user(client: FlaskClient, login: str, password: str):
    """Вспомогательная функция для регистрации пользователя."""
    return client.post(
        "/api/auth/register", json={"login": login, "password": password}
    )


# ---------- /api/auth/register ----------
def test_register_ok(client: FlaskClient):
    resp = register_user(client, LOGIN, PASSWORD)
    assert resp.status_code == OK


@pytest.mark.parametrize(
    "login,password,status",
    [
        (LOGIN, SHORT_PASSWORD, BAD),  # короткий пароль
        ("", PASSWORD, BAD),  # пустой логин
    ],
)
def test_register_bad_input(client: FlaskClient, login, password, status):
    resp = client.post(
        "/api/auth/register", json={"login": login, "password": password}
    )
    assert resp.status_code == status


def test_register_duplicate(client: FlaskClient):
    register_user(client, LOGIN, PASSWORD)
    resp = register_user(client, LOGIN, PASSWORD)
    assert resp.status_code == TEAPOT


# ---------- /api/auth/change-login ----------
def test_change_login_ok(client: FlaskClient):
    register_user(client, LOGIN, PASSWORD)
    resp = client.post(
        "/api/auth/change-login",
        json={
            "login": LOGIN,
            "password": PASSWORD,
            "new_login": NEW_LOGIN,
        },
    )
    assert resp.status_code == OK


@pytest.mark.parametrize(
    "wrong_pwd,new_login_val,expected",
    [
        (WRONG_PASSWORD, NEW_LOGIN, FORBIDDEN),  # неверный пароль
        (None, "", BAD),  # пустой новый логин
        (None, None, BAD),  # нет поля new_login
    ],
)
def test_change_login_fail(client: FlaskClient, wrong_pwd, new_login_val, expected):
    register_user(client, LOGIN, PASSWORD)
    payload = {
        "login": LOGIN,
        "password": wrong_pwd if wrong_pwd else PASSWORD,
    }
    if new_login_val is not None:
        payload["new_login"] = new_login_val
    resp = client.post("/api/auth/change-login", json=payload)
    assert resp.status_code == expected


def test_change_login_duplicate(client: FlaskClient):
    register_user(client, LOGIN, PASSWORD)
    register_user(client, OTHER_LOGIN, OTHER_PASSWORD)
    resp = client.post(
        "/api/auth/change-login",
        json={
            "login": LOGIN,
            "password": PASSWORD,
            "new_login": OTHER_LOGIN,
        },
    )
    assert resp.status_code == FORBIDDEN


def test_change_login_nonexistent(client: FlaskClient):
    resp = client.post(
        "/api/auth/change-login",
        json={"login": NONEXISTENT_LOGIN, "password": PASSWORD, "new_login": NEW_LOGIN},
    )
    assert resp.status_code == NOT_FOUND


# ---------- /api/auth/change-password ----------
def test_change_password_ok(client: FlaskClient):
    register_user(client, LOGIN, PASSWORD)
    resp = client.post(
        "/api/auth/change-password",
        json={
            "login": LOGIN,
            "password": PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )
    assert resp.status_code == OK


@pytest.mark.parametrize(
    "wrong_old,new_pwd_val,expected",
    [
        (WRONG_PASSWORD, NEW_PASSWORD, FORBIDDEN),
        (None, "short", BAD),  # слишком короткий новый пароль
        (None, None, BAD),  # нет new_password
    ],
)
def test_change_password_fail(client: FlaskClient, wrong_old, new_pwd_val, expected):
    register_user(client, LOGIN, PASSWORD)
    payload = {
        "login": LOGIN,
        "password": wrong_old if wrong_old else PASSWORD,
    }
    if new_pwd_val is not None:
        payload["new_password"] = new_pwd_val
    resp = client.post("/api/auth/change-password", json=payload)
    assert resp.status_code == expected


def test_change_password_nonexistent(client: FlaskClient):
    resp = client.post(
        "/api/auth/change-password",
        json={
            "login": NONEXISTENT_LOGIN,
            "password": PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )
    assert resp.status_code == NOT_FOUND
