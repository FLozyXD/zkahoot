"""Базовые тесты для викторин"""


class TestQuizBasic:
    def test_search_quiz_no_auth(self, client):
        """Поиск викторины без авторизации"""
        response = client.get("/api/quiz/search?query=test")
        assert response.status_code == 401

    def test_create_quiz_no_auth(self, client):
        """Создание викторины без авторизации"""
        response = client.post(
            "/api/quiz/register", json={"quiz_name": "Test", "questions": []}
        )
        assert response.status_code == 401

    def test_search_quiz_no_query(self, client):
        """Поиск викторины без query параметра (без авторизации)"""
        response = client.get("/api/quiz/search")
        assert response.status_code == 401
