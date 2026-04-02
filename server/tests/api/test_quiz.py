import unittest
import uuid
from src.api import create_app
from src.utils.DBWrapper import DBWrapper
from src.utils import UnifiedDict


class QuizTest(unittest.TestCase):
    def setUp(self):
        self.dw = DBWrapper("postgresql://localhost/zkahoot-test")
        self.dw.cur.execute("DELETE FROM Questions")
        self.dw.cur.execute("DELETE FROM Answers")
        self.dw.cur.execute("DELETE FROM Quizzes")
        self.dw.cur.execute("DELETE FROM Users")
        self.dw.commit()
        self.dw.close()

        UnifiedDict(name="token_user").clear()
        UnifiedDict(name="user_token").clear()

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
        UnifiedDict(name="lobby").clear()
        UnifiedDict(name="user_lobby").clear()
        UnifiedDict(name="token_user").clear()
        UnifiedDict(name="user_token").clear()

    def _get_auth_header(self, user_data):
        response = self.client.post("/api/auth/get-token", json=user_data)
        return {"Authorization": response.json["token"]}

    def test_register_quiz_success_empty_questions(self):
        payload = {"id": None, "quiz_name": "Просто квиз", "questions": []}
        response = self.client.post(
            "/api/quiz/register", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("status"), "OK")

    def test_register_quiz_with_questions(self):
        payload = {
            "id": None,
            "quiz_name": "Квиз с вопросами",
            "questions": [
                {
                    "id": None,
                    "quiz_id": None,
                    "question": "Вопросы?",
                    "question_type": "prompt",
                    "answer": {"id": None, "answer": "ответы"},
                    "type_dependent": "",
                },
                {
                    "id": None,
                    "quiz_id": None,
                    "question": "Опять вопросы?",
                    "question_type": "prompt",
                    "answer": {"id": None, "answer": "Снова ответы"},
                    "type_dependent": "",
                },
            ],
        }
        response = self.client.post(
            "/api/quiz/register", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("status"), "OK")

    def test_register_quiz_missing_name(self):
        payload = {"id": None, "questions": []}
        response = self.client.post(
            "/api/quiz/register", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_register_quiz_missing_questions_field(self):
        payload = {"id": None, "quiz_name": "Вопросов нет."}
        response = self.client.post(
            "/api/quiz/register", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_quiz_success(self):
        name = "Квиз для удаления"
        self.client.post(
            "/api/quiz/register",
            json={"id": None, "quiz_name": name, "questions": []},
            headers=self.header_host,
        )

        search = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        quiz_id = search.json["quizzes"][0]["id"]

        response = self.client.delete(
            "/api/quiz/delete", json={"id": quiz_id}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_quiz_not_owner(self):
        name = "Чужой квиз"
        self.client.post(
            "/api/quiz/register",
            json={"id": None, "quiz_name": name, "questions": []},
            headers=self.header_host,
        )

        search = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        quiz_id = search.json["quizzes"][0]["id"]

        response = self.client.delete(
            "/api/quiz/delete", json={"id": quiz_id}, headers=self.header_player
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_quiz_not_found(self):
        response = self.client.delete(
            "/api/quiz/delete", json={"id": 999999}, headers=self.header_host
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
            json={"id": None, "quiz_name": name, "questions": []},
            headers=self.header_host,
        )

        search = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        quiz_id = search.json["quizzes"][0]["id"]

        payload = {
            "quiz_id": quiz_id,
            "quiz_name": "Сменил имя зачем-то",
            "questions": [
                {
                    "id": None,
                    "quiz_id": quiz_id,
                    "question": "Этого не может быть, очередной вопрос?",
                    "question_type": "prompt",
                    "answer": {"id": None, "answer": "another one ответ"},
                    "type_dependent": "",
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
            json={"id": None, "quiz_name": name, "questions": []},
            headers=self.header_host,
        )

        search = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        quiz_id = search.json["quizzes"][0]["id"]

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

    def test_search_quiz_success(self):
        name = "Квиз в активном поиске"
        self.client.post(
            "/api/quiz/register",
            json={"id": None, "quiz_name": name, "questions": []},
            headers=self.header_host,
        )

        response = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json.get("quizzes", [])), 1)

    def test_search_quiz_not_found(self):
        response = self.client.post(
            "/api/quiz/search",
            json={"quiz_name": "Полностью вымышленное название qqq"},
            headers=self.header_host,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("quizzes"), [])

    def test_search_quiz_missing_field(self):
        response = self.client.post(
            "/api/quiz/search", json={}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_quiz_with_questions(self):
        name = "Квиз с вопросами на удаление"
        payload = {
            "id": None,
            "quiz_name": name,
            "questions": [
                {
                    "id": None,
                    "quiz_id": None,
                    "question": "вопросы?",
                    "question_type": "prompt",
                    "answer": {"id": None, "answer": "ответы"},
                    "type_dependent": "",
                }
            ],
        }
        self.client.post("/api/quiz/register", json=payload, headers=self.header_host)

        search = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        quiz_id = search.json["quizzes"][0]["id"]

        response = self.client.delete(
            "/api/quiz/delete", json={"id": quiz_id}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

        search_after = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        self.assertEqual(search_after.json.get("quizzes"), [])

    def test_change_quiz_only_name(self):
        name = "Квиз только название"
        create_payload = {"id": None, "quiz_name": name, "questions": []}
        self.client.post(
            "/api/quiz/register", json=create_payload, headers=self.header_host
        )

        search = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        quiz_id = search.json["quizzes"][0]["id"]

        payload = {"quiz_id": quiz_id, "quiz_name": "Новое имя"}
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_change_quiz_only_questions(self):
        name = "Квиз только вопросы"
        create_payload = {"id": None, "quiz_name": name, "questions": []}
        self.client.post(
            "/api/quiz/register", json=create_payload, headers=self.header_host
        )

        search = self.client.post(
            "/api/quiz/search", json={"quiz_name": name}, headers=self.header_host
        )
        quiz_id = search.json["quizzes"][0]["id"]

        payload = {
            "quiz_id": quiz_id,
            "questions": [
                {
                    "id": None,
                    "quiz_id": quiz_id,
                    "question": "Новый вопрос?",
                    "question_type": "prompt",
                    "answer": {"id": None, "answer": "новый ответ"},
                    "type_dependent": "",
                }
            ],
        }
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_no_token(self):
        payload = {"id": None, "quiz_name": "Без токена", "questions": []}
        response = self.client.post("/api/quiz/register", json=payload)
        self.assertEqual(response.status_code, 401)

    def test_register_quiz_invalid_question_missing_answer(self):
        payload = {
            "id": None,
            "quiz_name": "Плохой квиз",
            "questions": [
                {
                    "id": None,
                    "quiz_id": None,
                    "question": "Вопрос, на который нет ответа",
                    "question_type": "prompt",
                    "type_dependent": "",
                }
            ],
        }
        response = self.client.post(
            "/api/quiz/register", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
