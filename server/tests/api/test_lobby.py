import unittest
from src.api import create_app
from src.classes.DBWrapper import DBWrapper
from src.utils import UnifiedDict
from postgres import Postgres


class LobbyTest(unittest.TestCase):
    def setUp(self):
        self.dw = DBWrapper("postgresql://localhost/zkahoot-test")

        self.dw.db.run("DELETE FROM Questions")
        self.dw.db.run("DELETE FROM Answers")
        self.dw.db.run("DELETE FROM Quizzes")
        self.dw.db.run("DELETE FROM Users")

        self.dw.db.run(
            "INSERT INTO Users (id, login, password_hash) VALUES (999, 'db_user', 'hash')"
        )
        self.dw.db.run(
            "INSERT INTO Quizzes (id, quiz_name, creator_id) VALUES (1, 'Quiz_1', 999)"
        )
        self.dw.db.run("INSERT INTO Answers (id, answer) VALUES (1, 'ответы')")
        self.dw.db.run(
            "INSERT INTO Questions (id, quiz_id, question, question_type, answer_id) VALUES (1, 1, 'вопросы?', 'prompt', 1)"
        )

        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

        self.user_host = {"user": {"login": "host_api", "password": "123"}}
        self.user_player = {"user": {"login": "player_api", "password": "123"}}

        self.header_host = self._get_auth_header(self.user_host)
        self.header_player = self._get_auth_header(self.user_player)

    def tearDown(self):
        UnifiedDict("lobby").clear()
        UnifiedDict("user_lobby").clear()

    def _get_auth_header(self, user_data) -> dict:
        self.client.post("/api/auth/register", json=user_data)
        response = self.client.post("/api/auth/get-token", json=user_data)
        return {"Authorization": response.json["token"]}

    def test_create_lobby(self):
        payload = {"name": "Test Room", "quiz_id": 1}
        response = self.client.post(
            "/lobby/create", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)

    def test_create_lobby_already_in_lobby(self):
        payload = {"name": "First", "quiz_id": 1}
        self.client.post("/lobby/create", json=payload, headers=self.header_host)

        payload = {"name": "Second", "quiz_id": 1}
        response = self.client.post(
            "/lobby/create", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 403)

    def test_create_lobby_invalid_quiz(self):
        payload = {"name": "Invalid", "quiz_id": 999}
        response = self.client.post(
            "/lobby/create", json=payload, headers=self.header_host
        )
        self.assertIn(response.status_code, [404, 500])

    def test_join_and_get_info(self):
        res = self.client.post(
            "/lobby/create",
            json={"name": "JoinTest", "quiz_id": 1},
            headers=self.header_host,
        )
        token = res.json["token"]

        self.client.post(f"/lobby/join/{token}", headers=self.header_player)

        response = self.client.get("/lobby/get-info", headers=self.header_player)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "JoinTest")
        self.assertEqual(len(response.json["users"]), 2)

    def test_run_logic(self):
        self.client.post(
            "/lobby/create",
            json={"name": "RunTest", "quiz_id": 1},
            headers=self.header_host,
        )
        response = self.client.post("/lobby/run", headers=self.header_host)
        self.assertEqual(response.status_code, 200)

    def test_run_not_owner(self):
        res = self.client.post(
            "/lobby/create",
            json={"name": "RunTest", "quiz_id": 1},
            headers=self.header_host,
        )
        token = res.json["token"]
        self.client.post(f"/lobby/join/{token}", headers=self.header_player)

        response = self.client.post("/lobby/run", headers=self.header_player)
        self.assertEqual(response.status_code, 403)

    def test_exit_and_delete(self):
        self.client.post(
            "/lobby/create",
            json={"name": "DeleteTest", "quiz_id": 1},
            headers=self.header_host,
        )
        self.client.post("/lobby/exit", headers=self.header_host)

        response = self.client.get("/lobby/get-info", headers=self.header_host)
        self.assertEqual(response.status_code, 404)

    def test_compare_answers(self):
        self.client.post(
            "/lobby/create",
            json={"name": "QuizTest", "quiz_id": 1},
            headers=self.header_host,
        )
        self.client.post("/lobby/run", headers=self.header_host)

        payload = {"answers": ["4"]}
        response = self.client.post(
            "/lobby/compare", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        UnifiedDict("lobby").clear()
        self.client.post(
            "/lobby/create",
            json={"name": "FindMe", "quiz_id": 1},
            headers=self.header_host,
        )

        response = self.client.get("/lobby/search?q=Find", headers=self.header_player)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "FindMe")


if __name__ == "__main__":
    unittest.main()
