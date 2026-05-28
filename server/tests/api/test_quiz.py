import unittest
import uuid
import psycopg2
from src.api import create_app
from src.utils import UnifiedDict


class QuizTest(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect("postgresql://localhost/zkahoot-test")
        self.conn.autocommit = True
        cur = self.conn.cursor()
        cur.execute(
            "TRUNCATE TABLE questions, answers, quizzes, users RESTART IDENTITY CASCADE"
        )
        cur.close()

        UnifiedDict(name="token_user").clear()
        UnifiedDict(name="user_token").clear()
        UnifiedDict(name="lobby").clear()
        UnifiedDict(name="user_lobby").clear()

        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

        unique_id = str(uuid.uuid4())[:8]
        self.user_host = {"login": f"host_{unique_id}", "password": "qqqqqq123"}
        self.user_player = {"login": f"player_{unique_id}", "password": "qqqqqqqqq123"}

        self.client.post("/api/auth/register", json=self.user_host)
        self.client.post("/api/auth/register", json=self.user_player)

        self.header_host = self._get_auth_header(self.user_host)
        self.header_player = self._get_auth_header(self.user_player)

    def tearDown(self):
        self.conn.close()
        UnifiedDict(name="lobby").clear()
        UnifiedDict(name="user_lobby").clear()
        UnifiedDict(name="token_user").clear()
        UnifiedDict(name="user_token").clear()

    def _get_auth_header(self, user_data):
        response = self.client.post("/api/auth/get-token", json=user_data)
        return {"Authorization": response.json["token"]}

    def test_register_quiz_success_empty_questions(self):
        payload = {"name": "Просто квиз", "questions": []}
        response = self.client.post(
            "/api/quiz/register", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_register_quiz_with_questions(self):
        payload = {
            "name": "Квиз с вопросами",
            "questions": [
                {"text": "Вопросы?", "answer": "ответы"},
                {"text": "Опять вопросы?", "answer": "Снова ответы"},
            ],
        }
        response = self.client.post(
            "/api/quiz/register", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_quiz_success(self):
        name = "Квиз для удаления"
        self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        quiz_id = response.json[0]["id"]

        response = self.client.delete(
            "/api/quiz/delete", json={"quiz_id": quiz_id}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_quiz_not_owner(self):
        name = "Чужой квиз"
        self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        quiz_id = response.json[0]["id"]

        response = self.client.delete(
            "/api/quiz/delete", json={"quiz_id": quiz_id}, headers=self.header_player
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_quiz_not_found(self):
        response = self.client.delete(
            "/api/quiz/delete", json={"quiz_id": 999999}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_quiz_no_id(self):
        response = self.client.delete(
            "/api/quiz/delete", json={}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_change_quiz_success(self):
        name = "Квиз для изменения"
        self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        quiz_id = response.json[0]["id"]

        payload = {
            "quiz_id": quiz_id,
            "quiz_name": "Новое имя квиза",
            "questions": [
                {
                    "id": None,
                    "quiz_id": quiz_id,
                    "question": "Новый вопрос",
                    "answer": {"id": None, "answer": "Новый ответ"},
                    "type_dependent": None,
                }
            ],
        }
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_change_quiz_not_owner(self):
        name = "Чужой квиз"
        self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        quiz_id = response.json[0]["id"]

        payload = {"quiz_id": quiz_id, "quiz_name": "Хорошая попытка", "questions": []}
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_player
        )
        self.assertEqual(response.status_code, 404)

    def test_change_quiz_not_found(self):
        payload = {"quiz_id": 999999, "quiz_name": "Мнимый квиз", "questions": []}
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 404)

    def test_change_quiz_missing_fields(self):
        payload = {"quiz_id": 1}
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_change_quiz_only_name(self):
        name = "Квиз только название"
        self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        quiz_id = response.json[0]["id"]

        payload = {"quiz_id": quiz_id, "quiz_name": "Новое имя"}
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_change_quiz_only_questions(self):
        name = "Квиз только вопросы"
        self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        quiz_id = response.json[0]["id"]

        payload = {
            "quiz_id": quiz_id,
            "questions": [
                {
                    "id": None,
                    "quiz_id": quiz_id,
                    "question": "Новый вопрос",
                    "answer": {"id": None, "answer": "Новый ответ"},
                    "type_dependent": None,
                }
            ],
        }
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_search_quiz_success(self):
        name = "Квиз для поиска"
        self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)

    def test_search_quiz_not_found(self):
        response = self.client.get(
            "/api/quiz/search?query=несуществующий_квиз", headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_search_quiz_missing_query(self):
        response = self.client.get("/api/quiz/search", headers=self.header_host)
        self.assertEqual(response.status_code, 400)

    def test_search_quiz_with_creator_id(self):
        name = "Квиз с создателем"
        self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.get(
            f"/api/quiz/search?query={name}&creator_id=1", headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_quiz_with_questions(self):
        name = "Квиз с вопросами на удаление"
        payload = {
            "name": name,
            "questions": [{"text": "вопрос?", "answer": "ответ"}],
        }
        self.client.post("/api/quiz/register", json=payload, headers=self.header_host)

        response = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        quiz_id = response.json[0]["id"]

        response = self.client.delete(
            "/api/quiz/delete", json={"quiz_id": quiz_id}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

        response_after = self.client.get(
            f"/api/quiz/search?query={name}", headers=self.header_host
        )
        self.assertEqual(response_after.json, [])

    def test_no_token(self):
        payload = {"name": "Без токена", "questions": []}
        response = self.client.post("/api/quiz/register", json=payload)
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
