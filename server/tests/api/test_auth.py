from api import create_app
from classes.DBWrapper import DBWrapper
import unittest


class AuthTest(unittest.TestCase):
    def setUp(self):
        dw = DBWrapper("postgresql://localhost/zkahoot-test")
        dw.db.run("delete from users")

        app = create_app()
        app.config["TESTING"] = True

        self.client = app.test_client()
        self.valid_user = {
            "user": {
                "login": "evgeniy",
                "password": "evgeniy",
            }
        }
        self.invalid_user = {
            "user": {
                "login": "evgeniy",
                "password": "jenya",
            }
        }

    def test_registration(self):
        response = self.client.post("/api/auth/register", json=self.valid_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "OK")

        response = self.client.post("/api/auth/register", json=self.valid_user)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json["status"], "Forbidden")

    def test_token(self):
        self.client.post("/api/auth/register", json=self.valid_user)
        response = self.client.post(
            "/api/auth/get-token", json=self.valid_user
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "OK")
        self.assertIn("token", response.json)

        response = self.client.post(
            "/api/auth/get-token", json=self.invalid_user
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json["status"], "Forbidden")
        self.assertNotIn("token", response.json)
