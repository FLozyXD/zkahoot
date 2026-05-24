"""Базовые тесты авторизации"""


class TestAuthBasic:
    def test_register_success(self, client):
        """Успешная регистрация"""
        response = client.post(
            "/api/auth/register",
            json={"login": "newuser123", "password": "securepass123"},
        )
        assert response.status_code == 200

    def test_register_duplicate_login(self, client):
        """Регистрация с существующим логином"""
        # Первая регистрация
        client.post(
            "/api/auth/register",
            json={"login": "duplicate_user", "password": "pass123456"},
        )

        # Вторая регистрация с тем же логином
        response = client.post(
            "/api/auth/register",
            json={"login": "duplicate_user", "password": "pass123456"},
        )
        assert response.status_code == 418

    def test_register_password_too_short(self, client):
        """Регистрация с коротким паролем"""
        response = client.post(
            "/api/auth/register", json={"login": "testuser", "password": "short"}
        )
        assert response.status_code == 400

    def test_register_empty_login(self, client):
        """Регистрация с пустым логином"""
        response = client.post(
            "/api/auth/register", json={"login": "", "password": "password123"}
        )
        assert response.status_code == 400

    def test_register_missing_fields(self, client):
        """Регистрация без обязательных полей"""
        # Без пароля
        response = client.post("/api/auth/register", json={"login": "testuser"})
        assert response.status_code == 400

        # Без логина
        response = client.post("/api/auth/register", json={"password": "testpass"})
        assert response.status_code == 400

    def test_make_token_nonexistent_user(self, client):
        """Получение токена для несуществующего пользователя"""
        response = client.post(
            "/api/auth/make-token",
            json={"login": "nonexistent_user_12345", "password": "anypass"},
        )
        assert response.status_code == 400
