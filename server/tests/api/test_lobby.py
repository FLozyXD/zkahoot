import os
import unittest
import uuid
from src.api import create_app
from src.utils.DBWrapper import DBWrapper
from src.utils import UnifiedDict


TEST_DSN = os.getenv("ZKAHOOT_TEST_DSN", "postgresql://localhost/zkahoot-test")


class LobbyTest(unittest.TestCase):
    def setUp(self):
        self.dw = DBWrapper(TEST_DSN)
        self.dw.cur.execute("DELETE FROM Questions")
        self.dw.cur.execute("DELETE FROM Answers")
        self.dw.cur.execute("DELETE FROM Quizzes")
        self.dw.cur.execute("DELETE FROM Users")
        self.dw.commit()
        self.dw.close()

        for name in (
            "token_user",
            "user_token",
            "lobby",
            "token_lobby",
            "user_lobby",
        ):
            UnifiedDict(name=name).clear()

        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

        suffix = str(uuid.uuid4())[:8]
        self.host = {"login": f"host_{suffix}", "password": "password_123"}
        self.player = {"login": f"player_{suffix}", "password": "password_123"}
        self.client.post("/api/auth/register", json=self.host)
        self.client.post("/api/auth/register", json=self.player)
        self.host_header = self._auth_header(self.host)
        self.player_header = self._auth_header(self.player)

        response = self.client.post(
            "/api/quiz/register",
            json={
                "name": "Квиз для лобби",
                "questions": [
                    {"text": "Два плюс два?", "answer": "Четыре"},
                    {"text": "Столица Франции?", "answer": "Париж"},
                ],
            },
            headers=self.host_header,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/api/quiz/search",
            query_string={"query": "Квиз для лобби"},
            headers=self.host_header,
        )
        self.quiz_id = response.get_json()[0]["id"]

    def tearDown(self):
        for name in (
            "token_user",
            "user_token",
            "lobby",
            "token_lobby",
            "user_lobby",
        ):
            UnifiedDict(name=name).clear()

    def _auth_header(self, creds):
        response = self.client.post("/api/auth/get-token", json=creds)
        return {"Authorization": response.get_json()["token"]}

    def _create_lobby(self, name="Моё лобби"):
        response = self.client.post(
            "/api/lobby/create",
            json={"name": name, "quiz_id": self.quiz_id},
            headers=self.host_header,
        )
        return response

    def test_create_and_search_lobby(self):
        response = self._create_lobby()
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["token"]
        self.assertTrue(token)

        response = self.client.get(
            "/api/lobby/search",
            query_string={"query": "лобби"},
            headers=self.player_header,
        )
        self.assertEqual(response.status_code, 200)
        lobbies = response.get_json()
        self.assertEqual(len(lobbies), 1)
        self.assertEqual(lobbies[0]["token"], token)
        self.assertEqual(lobbies[0]["name"], "Моё лобби")

    def test_create_lobby_missing_fields(self):
        response = self.client.post(
            "/api/lobby/create",
            json={"name": "Без квиза"},
            headers=self.host_header,
        )
        self.assertEqual(response.status_code, 400)

    def test_create_lobby_unknown_quiz(self):
        response = self.client.post(
            "/api/lobby/create",
            json={"name": "Лобби", "quiz_id": 999999},
            headers=self.host_header,
        )
        self.assertEqual(response.status_code, 404)

    def test_join_get_info_and_exit(self):
        token = self._create_lobby().get_json()["token"]

        response = self.client.post(
            f"/api/lobby/join/{token}", headers=self.player_header
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/api/lobby/get-info", headers=self.host_header
        )
        self.assertEqual(response.status_code, 200)
        info = response.get_json()
        self.assertEqual(len(info["users"]), 2)
        self.assertIn(self.host["login"], info["users"])
        self.assertIn(self.player["login"], info["users"])
        self.assertEqual(info["quiz"]["id"], self.quiz_id)

        response = self.client.post("/api/lobby/exit", headers=self.player_header)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/api/lobby/get-info", headers=self.player_header
        )
        self.assertEqual(response.status_code, 404)

    def test_join_unknown_lobby(self):
        response = self.client.post(
            "/api/lobby/join/does-not-exist", headers=self.player_header
        )
        self.assertEqual(response.status_code, 404)

    def test_only_owner_can_run_and_compare(self):
        token = self._create_lobby().get_json()["token"]
        self.client.post(f"/api/lobby/join/{token}", headers=self.player_header)

        response = self.client.post("/api/lobby/run", headers=self.player_header)
        self.assertEqual(response.status_code, 403)

        response = self.client.post("/api/lobby/run", headers=self.host_header)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            f"/api/lobby/poll-running/{token}", headers=self.player_header
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.put(
            "/api/lobby/compare",
            json={"answers": ["четыре", "ПАРИЖ"]},
            headers=self.player_header,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [True, True])

    def test_compare_requires_running_lobby(self):
        token = self._create_lobby().get_json()["token"]
        self.client.post(f"/api/lobby/join/{token}", headers=self.player_header)

        response = self.client.put(
            "/api/lobby/compare",
            json={"answers": ["четыре", "париж"]},
            headers=self.player_header,
        )
        self.assertEqual(response.status_code, 403)

    def test_compare_rejects_wrong_answer_count(self):
        token = self._create_lobby().get_json()["token"]
        self.client.post(f"/api/lobby/join/{token}", headers=self.player_header)
        self.client.post("/api/lobby/run", headers=self.host_header)

        response = self.client.put(
            "/api/lobby/compare",
            json={"answers": ["четыре"]},
            headers=self.player_header,
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
