import os
import shutil
import tempfile
import unittest

from werkzeug.security import check_password_hash

TEST_DIR = tempfile.mkdtemp(prefix="ethereal-test-")
os.environ["DATABASE_PATH"] = os.path.join(TEST_DIR, "test.db")
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ.pop("APP_ENV", None)
os.environ.pop("RAILWAY_ENVIRONMENT_NAME", None)

from app import app, get_db  # noqa: E402


class EtherealAppTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

        with app.app_context():
            db = get_db()
            db.execute("DELETE FROM user_bubbles")
            db.execute("DELETE FROM users")
            db.commit()

    def test_account_session_and_bubbles_flow(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

        response = self.client.post(
            "/register",
            data={
                "name": "Maria",
                "email": "maria@example.com",
                "password": "beautiful123",
                "confirmation": "beautiful123",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Bubbles", response.data)

        with app.app_context():
            user = get_db().execute(
                "SELECT * FROM users WHERE email = ?",
                ("maria@example.com",),
            ).fetchone()
            self.assertIsNotNone(user)
            self.assertNotEqual(user["password_hash"], "beautiful123")
            self.assertTrue(check_password_hash(user["password_hash"], "beautiful123"))

        response = self.client.post("/api/bubbles/1/toggle")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["saved"])

        response = self.client.get("/my-bubbles")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Saved", response.data)

        response = self.client.post("/logout")
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/my-bubbles")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

        response = self.client.post(
            "/login",
            data={
                "email": "maria@example.com",
                "password": "beautiful123",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Bubbles", response.data)


if __name__ == "__main__":
    unittest.main()
