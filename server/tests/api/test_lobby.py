import unittest
import uuid
import psycopg2
from src.api import create_app
from src.utils import UnifiedDict


class LobbyTest(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect("postgresql://localhost/zkahoot-test")
        self.conn.autocommit = True
        cur = self.conn.cursor()

        cur.execute(
            "TRUNCATE TABLE questions, answers, quizzes, users RESTART IDENTITY CASCADE"
        )

        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

        self.user_host = {
            "login": f"host_{uuid.uuid4().hex[:8]}",
            "password": "qqqqqq123",
        }
        self.user_player = {
            "login": f"player_{uuid.uuid4().hex[:8]}",
            "password": "qqqqqqqqq123",
        }

        self.client.post("/api/auth/register", json=self.user_host)
        self.client.post("/api/auth/register", json=self.user_player)

        cur.execute("SELECT id FROM users WHERE login = %s", (self.user_host["login"],))
        host_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO quizzes (id, quiz_name, creator_id) VALUES (1, 'Quiz_1', %s)",
            (host_id,),
        )
        cur.execute("INSERT INTO answers (id, answer) VALUES (1, 'ответы')")
        cur.execute(
            "INSERT INTO questions (id, quiz_id, question, question_type, answer_id) "
            "VALUES (1, 1, 'вопросы?', 'prompt', 1)"
        )
        cur.close()

        self.header_host = self._get_auth_header(self.user_host)
        self.header_player = self._get_auth_header(self.user_player)

    def tearDown(self):
        self.conn.close()
        UnifiedDict(name="lobby").clear()
        UnifiedDict(name="user_lobby").clear()

    def _get_auth_header(self, user_data):
        response = self.client.post("/api/auth/get-token", json=user_data)
        return {"Authorization": response.json["token"]}

    def test_create_lobby(self):
        payload = {"name": "Test Room", "quiz_id": 1}
        response = self.client.post(
            "/api/lobby/create", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)

    def test_create_lobby_already_in_lobby(self):
        payload = {"name": "First", "quiz_id": 1}
        self.client.post("/api/lobby/create", json=payload, headers=self.header_host)

        response = self.client.post(
            "/api/lobby/create", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 403)

    def test_create_lobby_invalid_quiz(self):
        payload = {"name": "Invalid", "quiz_id": 999}
        response = self.client.post(
            "/api/lobby/create", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 404)

    def test_join_and_get_info(self):
        res = self.client.post(
            "/api/lobby/create",
            json={"name": "JoinTest", "quiz_id": 1},
            headers=self.header_host,
        )
        token = res.json["token"]

        self.client.post(f"/api/lobby/join/{token}", headers=self.header_player)

        response = self.client.get("/api/lobby/get-info", headers=self.header_player)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "JoinTest")
        self.assertEqual(len(response.json["users"]), 2)

    def test_run_logic(self):
        self.client.post(
            "/api/lobby/create",
            json={"name": "RunTest", "quiz_id": 1},
            headers=self.header_host,
        )
        response = self.client.post("/api/lobby/run", headers=self.header_host)
        self.assertEqual(response.status_code, 200)

    def test_run_not_owner(self):
        res = self.client.post(
            "/api/lobby/create",
            json={"name": "RunTest", "quiz_id": 1},
            headers=self.header_host,
        )
        token = res.json["token"]
        self.client.post(f"/api/lobby/join/{token}", headers=self.header_player)

        response = self.client.post("/api/lobby/run", headers=self.header_player)
        self.assertEqual(response.status_code, 403)

    def test_exit_and_delete(self):
        self.client.post(
            "/api/lobby/create",
            json={"name": "DeleteTest", "quiz_id": 1},
            headers=self.header_host,
        )
        self.client.post("/api/lobby/exit", headers=self.header_host)

        response = self.client.get("/api/lobby/get-info", headers=self.header_host)
        self.assertEqual(response.status_code, 404)

    def test_compare_answers(self):
        self.client.post(
            "/api/lobby/create",
            json={"name": "QuizTest", "quiz_id": 1},
            headers=self.header_host,
        )
        self.client.post("/api/lobby/run", headers=self.header_host)

        payload = {"answers": ["4"]}
        response = self.client.put(
            "/api/lobby/compare", json=payload, headers=self.header_host
        )
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        UnifiedDict(name="lobby").clear()
        self.client.post(
            "/api/lobby/create",
            json={"name": "FindMe", "quiz_id": 1},
            headers=self.header_host,
        )

        response = self.client.get(
            "/api/lobby/search?query=Find", headers=self.header_player
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "FindMe")


if __name__ == "__main__":
    unittest.main()
