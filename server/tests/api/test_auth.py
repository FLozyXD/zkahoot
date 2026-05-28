import psycopg2
import unittest
from src.api import create_app
from src.utils import UnifiedDict


class AuthTest(unittest.TestCase):
    def setUp(self):

        UnifiedDict(name="token_user").clear()
        UnifiedDict(name="user_token").clear()
        self.conn = psycopg2.connect("postgresql://localhost/zkahoot-test")
        self.conn.autocommit = True
        cur = self.conn.cursor()
        cur.execute(
            "TRUNCATE TABLE questions, answers, quizzes, users RESTART IDENTITY CASCADE"
        )
        cur.close()

        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

        self.valid_user = {"login": "evgeniy", "password": "evgeniy123"}
        self.invalid_user = {"login": "evgeniy", "password": "jenya1234"}
        self.user1 = {"login": "user1", "password": "password123"}
        self.user2 = {"login": "user2", "password": "password123"}

        def tearDown(self):
            self.conn.close()

    def test_registration(self):
        response = self.client.post("/api/auth/register", json=self.valid_user)
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/auth/register", json=self.valid_user)
        self.assertEqual(response.status_code, 418)

    def test_token(self):
        response = self.client.post("/api/auth/register", json=self.valid_user)
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/auth/get-token", json=self.valid_user)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assertIn("token", response.json)

        response = self.client.post("/api/auth/get-token", json=self.invalid_user)
        self.assertEqual(response.status_code, 403)

    def test_change_login_success(self):
        response = self.client.post("/api/auth/register", json=self.valid_user)
        self.assertEqual(response.status_code, 200)

        new_login = "jenya"
        payload = {
            "login": self.valid_user["login"],
            "password": self.valid_user["password"],
            "new_login": new_login,
        }
        response = self.client.post("/api/auth/change-login", json=payload)
        self.assertEqual(response.status_code, 200)

        new_creds = {"login": new_login, "password": self.valid_user["password"]}
        resp_token = self.client.post("/api/auth/get-token", json=new_creds)
        self.assertEqual(resp_token.status_code, 200)
        self.assertIn("token", resp_token.json)

    def test_change_login_duplicate(self):
        self.client.post("/api/auth/register", json=self.user1)
        self.client.post("/api/auth/register", json=self.user2)

        payload = {
            "login": self.user2["login"],
            "password": self.user2["password"],
            "new_login": self.user1["login"],
        }
        response = self.client.post("/api/auth/change-login", json=payload)
        self.assertEqual(response.status_code, 403)

    def test_change_login_invalid(self):
        self.client.post("/api/auth/register", json=self.valid_user)

        payload = {
            "login": self.valid_user["login"],
            "password": self.valid_user["password"],
            "new_login": "",
        }
        response = self.client.post("/api/auth/change-login", json=payload)
        self.assertEqual(response.status_code, 400)

        payload = {
            "login": self.valid_user["login"],
            "password": self.valid_user["password"],
        }
        response = self.client.post("/api/auth/change-login", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_change_password_success(self):
        response = self.client.post("/api/auth/register", json=self.valid_user)
        self.assertEqual(response.status_code, 200)

        new_password = "jenya12321"
        payload = {
            "login": self.valid_user["login"],
            "password": self.valid_user["password"],
            "new_password": new_password,
        }
        response = self.client.post("/api/auth/change-password", json=payload)
        self.assertEqual(response.status_code, 200)

        new_creds = {"login": self.valid_user["login"], "password": new_password}
        resp_token = self.client.post("/api/auth/get-token", json=new_creds)
        self.assertEqual(resp_token.status_code, 200)
        self.assertIn("token", resp_token.json)

    def test_change_password_short(self):
        self.client.post("/api/auth/register", json=self.valid_user)

        payload = {
            "login": self.valid_user["login"],
            "password": self.valid_user["password"],
            "new_password": "short",
        }
        response = self.client.post("/api/auth/change-password", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_change_password_missing_field(self):
        self.client.post("/api/auth/register", json=self.valid_user)

        payload = {
            "login": self.valid_user["login"],
            "password": self.valid_user["password"],
        }
        response = self.client.post("/api/auth/change-password", json=payload)
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
