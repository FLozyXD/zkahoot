"""Базовые тесты для лобби"""


class TestLobbyBasic:
    def test_search_lobby_no_auth(self, client):
        """Поиск лобби без авторизации"""
        response = client.get("/api/lobby/search?query=test")
        assert response.status_code == 401

    def test_create_lobby_no_auth(self, client):
        """Создание лобби без авторизации"""
        response = client.post(
            "/api/lobby/create", json={"name": "Test Lobby", "quiz_id": 1}
        )
        assert response.status_code == 401

    def test_search_lobby_no_query(self, client):
        """Поиск лобби без query параметра (без авторизации)"""
        response = client.get("/api/lobby/search")
        assert response.status_code == 401

    def test_join_lobby_no_auth(self, client):
        """Присоединение к лобби без авторизации"""
        response = client.post("/api/lobby/join/test_token")
        assert response.status_code == 401

    def test_exit_lobby_no_auth(self, client):
        """Выход из лобби без авторизации"""
        response = client.post("/api/lobby/exit")
        assert response.status_code == 401

    def test_get_lobby_info_no_auth(self, client):
        """Получение информации о лобби без авторизации"""
        response = client.get("/api/lobby/get-info")
        assert response.status_code == 401
