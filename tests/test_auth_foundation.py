import tempfile
import unittest
from pathlib import Path

from backend.app.api.routes import ApiFacade


class AuthFoundationTests(unittest.TestCase):
    def test_email_verification_registration_and_login(self):
        api = ApiFacade()
        pending = api.request_registration({
            "email": "learner@example.com",
            "password": "strong-pass-123",
            "displayName": "Learner",
        })
        self.assertEqual(pending["state"], "verification_pending")
        code = api.auth.dev_sender.last_codes["learner@example.com"]
        verified = api.verify_registration({"email": "learner@example.com", "code": code})
        self.assertEqual(verified["user"]["displayName"], "Learner")
        logged_in = api.login({"email": "learner@example.com", "password": "strong-pass-123"})
        self.assertTrue(logged_in["token"])
        self.assertEqual(api.authenticate(logged_in["token"]).id, verified["user"]["id"])

    def test_auth_records_survive_sqlite_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "universe.sqlite3")
            first = ApiFacade(database_path=path)
            first.request_registration({
                "email": "restart@example.com",
                "password": "strong-pass-123",
                "displayName": "Restart User",
            })
            code = first.auth.dev_sender.last_codes["restart@example.com"]
            verified = first.verify_registration({"email": "restart@example.com", "code": code})
            first.persistence.close()

            second = ApiFacade(database_path=path)
            logged_in = second.login({"email": "restart@example.com", "password": "strong-pass-123"})
            self.assertEqual(logged_in["user"]["id"], verified["user"]["id"])
            self.assertEqual(second.authenticate(logged_in["token"]).display_name, "Restart User")
            second.persistence.close()


if __name__ == "__main__":
    unittest.main()
