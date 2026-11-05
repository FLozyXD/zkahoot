import os
import unittest
import uuid
from src.api import create_app
from src.utils.DBWrapper import DBWrapper
from src.utils import UnifiedDict


TEST_DSN = os.getenv("ZKAHOOT_TEST_DSN", "postgresql://localhost/zkahoot-test")


class QuizTest(unittest.TestCase):
    def setUp(self):
        self.dw = DBWrapper(TEST_DSN)
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
        return {"Authorization": response.get_json()["token"]}

    def _new_question(self, text, answer):
        return {"text": text, "answer": answer}

    def _stored_question(self, text, answer):
        return {
            "id": None,
            "quiz_id": None,
            "question": text,
            "answer": {"id": None, "answer": answer},
            "type_dependent": None,
        }

    def _register(self, name, questions=None):
        return self.client.post(
            "/api/quiz/register",
            json={"name": name, "questions": questions or []},
            headers=self.header_host,
        )

    def _search(self, name):
        return self.client.get(
            "/api/quiz/search",
            query_string={"query": name},
            headers=self.header_host,
        )

    def _first_quiz_id(self, name):
        response = self._search(name)
        return response.get_json()[0]["id"]

    def test_register_quiz_success_empty_questions(self):
        response = self._register("Просто квиз")
        self.assertEqual(response.status_code, 200)

    def test_register_quiz_with_questions(self):
        response = self._register(
            "Квиз с вопросами",
            [
                self._new_question("Вопросы?", "ответы"),
                self._new_question("Опять вопросы?", "Снова ответы"),
            ],
        )
        self.assertEqual(response.status_code, 200)

        quizzes = self._search("Квиз с вопросами").get_json()
        self.assertEqual(len(quizzes), 1)
        self.assertEqual(len(quizzes[0]["questions"]), 2)

    def test_register_quiz_missing_name(self):
        response = self.client.post(
            "/api/quiz/register",
            json={"questions": []},
            headers=self.header_host,
        )
        self.assertEqual(response.status_code, 400)

    def test_register_quiz_missing_questions_field(self):
        response = self.client.post(
            "/api/quiz/register",
            json={"name": "Вопросов нет."},
            headers=self.header_host,
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_quiz_success(self):
        name = "Квиз для удаления"
        self._register(name)
        quiz_id = self._first_quiz_id(name)

        response = self.client.delete(
            "/api/quiz/delete", json={"quiz_id": quiz_id}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_quiz_not_owner(self):
        name = "Чужой квиз"
        self._register(name)
        quiz_id = self._first_quiz_id(name)

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
        self._register(name)
        quiz_id = self._first_quiz_id(name)

        payload = {
            "quiz_id": quiz_id,
            "quiz_name": "Сменил имя зачем-то",
            "questions": [self._stored_question("Очередной вопрос?", "another one ответ")],
        }
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

        quizzes = self._search("Сменил имя зачем-то").get_json()
        self.assertEqual(len(quizzes), 1)
        self.assertEqual(quizzes[0]["id"], quiz_id)

    def test_change_quiz_not_owner(self):
        name = "Чужой квиз"
        self._register(name)
        quiz_id = self._first_quiz_id(name)

        payload = {
            "quiz_id": quiz_id,
            "quiz_name": "Хорошая попытка",
            "questions": [self._stored_question("Вопрос?", "ответ")],
        }
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_player
        )
        self.assertEqual(response.status_code, 404)

    def test_change_quiz_not_found(self):
        payload = {
            "quiz_id": 999999,
            "quiz_name": "Мнимый квиз",
            "questions": [self._stored_question("Вопрос?", "ответ")],
        }
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 404)

    def test_change_quiz_missing_fields(self):
        response = self.client.post(
            "/api/quiz/change", json={"quiz_id": 1}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_search_quiz_success(self):
        name = "Квиз в активном поиске"
        self._register(name)

        response = self._search(name)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.get_json()), 1)

    def test_search_quiz_partial_match(self):
        self._register("Квиз про космос")
        self._register("Квиз про океан")

        response = self._search("космос")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)
        self.assertEqual(response.get_json()[0]["quiz_name"], "Квиз про космос")

    def test_search_all_with_empty_query(self):
        self._register("Первый квиз")
        self._register("Второй квиз")

        response = self._search("")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_search_quiz_not_found(self):
        response = self._search("Полностью вымышленное название qqq")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_search_quiz_missing_field(self):
        response = self.client.get("/api/quiz/search", headers=self.header_host)
        self.assertEqual(response.status_code, 400)

    def test_delete_quiz_with_questions(self):
        name = "Квиз с вопросами на удаление"
        self._register(name, [self._new_question("вопросы?", "ответы")])
        quiz_id = self._first_quiz_id(name)

        response = self.client.delete(
            "/api/quiz/delete", json={"quiz_id": quiz_id}, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

        search_after = self._search(name)
        self.assertEqual(search_after.get_json(), [])

    def test_change_quiz_only_name(self):
        name = "Квиз только название"
        self._register(name)
        quiz_id = self._first_quiz_id(name)

        payload = {"quiz_id": quiz_id, "quiz_name": "Новое имя"}
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_change_quiz_only_questions(self):
        name = "Квиз только вопросы"
        self._register(name)
        quiz_id = self._first_quiz_id(name)

        payload = {
            "quiz_id": quiz_id,
            "questions": [self._stored_question("Новый вопрос?", "новый ответ")],
        }
        response = self.client.post(
            "/api/quiz/change", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)

    def test_no_token(self):
        payload = {"name": "Без токена", "questions": []}
        response = self.client.post("/api/quiz/register", json=payload)
        self.assertEqual(response.status_code, 401)

    def test_register_quiz_invalid_question_missing_answer(self):
        payload = {
            "name": "Плохой квиз",
            "questions": [{"text": "Вопрос, на который нет ответа"}],
        }
        response = self.client.post(
            "/api/quiz/register", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
