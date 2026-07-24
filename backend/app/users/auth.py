from __future__ import annotations

import hashlib
import secrets
import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Protocol
from uuid import uuid4

from backend.app.core.dates import local_now
from backend.app.persistence.sqlite import SQLitePersistence
from backend.app.users.service import UserProfile, UserService


class VerificationEmailSender(Protocol):
    def send_code(self, email: str, code: str) -> None:
        ...


class ConsoleEmailSender:
    """Development sender; codes stay in process for tests and local setup."""

    def __init__(self) -> None:
        self.last_codes: dict[str, str] = {}

    def send_code(self, email: str, code: str) -> None:
        self.last_codes[email] = code


class SMTPEmailSender:
    def __init__(self, *, host: str, port: int, username: str, password: str, sender: str) -> None:
        if not all((host, username, password, sender)):
            raise ValueError("SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD and SMTP_FROM are required")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender = sender

    def send_code(self, email: str, code: str) -> None:
        message = EmailMessage()
        message["Subject"] = "Universe OS email verification code"
        message["From"] = self.sender
        message["To"] = email
        message.set_content(f"Your Universe OS verification code is {code}. It expires in 10 minutes.")
        with smtplib.SMTP_SSL(self.host, self.port, timeout=20) as client:
            client.login(self.username, self.password)
            client.send_message(message)


@dataclass(frozen=True)
class AuthSession:
    token: str
    user: UserProfile


class AuthService:
    def __init__(
        self,
        *,
        users: UserService,
        persistence: SQLitePersistence | None = None,
        sender: VerificationEmailSender | None = None,
    ) -> None:
        self._users = users
        self._db = persistence
        self._sender = sender or ConsoleEmailSender()
        self._accounts: dict[str, dict[str, object]] = {}
        self._codes: dict[str, dict[str, object]] = {}
        self._sessions: dict[str, dict[str, object]] = {}

    @property
    def dev_sender(self) -> ConsoleEmailSender | None:
        return self._sender if isinstance(self._sender, ConsoleEmailSender) else None

    def request_registration(self, *, email: str, password: str, display_name: str) -> dict[str, object]:
        email = self._normalize_email(email)
        if len(password) < 8:
            raise ValueError("password must be at least 8 characters")
        display_name = display_name.strip() or email.split("@", 1)[0]
        account = self._find_account(email)
        if account and account.get("emailVerifiedAt"):
            raise ValueError("email is already registered")
        if account:
            user_id = str(account["userId"])
        else:
            user_id = str(uuid4())
            self._users.create_user(user_id, display_name)
        password_hash = _hash_password(password)
        if self._db:
            with self._db.transaction() as db:
                db.execute(
                    """INSERT INTO auth_accounts(user_id,email,password_hash,created_at)
                       VALUES(?,?,?,CURRENT_TIMESTAMP)
                       ON CONFLICT(user_id) DO UPDATE SET email=excluded.email,password_hash=excluded.password_hash""",
                    (user_id, email, password_hash),
                )
        else:
            self._accounts[email] = {"userId": user_id, "passwordHash": password_hash, "displayName": display_name}
        code = f"{secrets.randbelow(1_000_000):06d}"
        code_id = str(uuid4())
        expires_at = local_now() + timedelta(minutes=10)
        if self._db:
            with self._db.transaction() as db:
                db.execute(
                    "INSERT INTO email_verification_codes(id,email,code_hash,expires_at,created_at) VALUES(?,?,?,?,?)",
                    (code_id, email, _hash_code(email, code), expires_at.isoformat(), local_now().isoformat()),
                )
        else:
            self._codes[email] = {"id": code_id, "hash": _hash_code(email, code), "expiresAt": expires_at}
        self._sender.send_code(email, code)
        return {"state": "verification_pending", "email": email, "expiresInSeconds": 600}

    def verify_registration(self, *, email: str, code: str) -> AuthSession:
        email = self._normalize_email(email)
        account = self._find_account(email)
        if not account:
            raise ValueError("registration request not found")
        verification = self._find_code(email)
        if not verification or verification.get("usedAt"):
            raise ValueError("verification code is invalid or already used")
        expires_at = verification["expiresAt"]
        expires_at = _as_datetime(expires_at)
        if expires_at < local_now() or not secrets.compare_digest(
            str(verification["hash"]), _hash_code(email, code)
        ):
            raise ValueError("verification code is invalid or expired")
        now = local_now()
        user_id = str(account["userId"])
        if self._db:
            with self._db.transaction() as db:
                db.execute("UPDATE auth_accounts SET email_verified_at = ? WHERE email = ?", (now.isoformat(), email))
                db.execute("UPDATE email_verification_codes SET used_at = ? WHERE id = ?", (now.isoformat(), verification["id"]))
        else:
            self._accounts[email]["emailVerifiedAt"] = now.isoformat()
            self._codes[email]["usedAt"] = now.isoformat()
        return self._new_session(user_id)

    def login(self, *, email: str, password: str) -> AuthSession:
        email = self._normalize_email(email)
        account = self._find_account(email)
        if not account or not account.get("emailVerifiedAt"):
            raise ValueError("email must be verified before login")
        if not _verify_password(password, str(account["passwordHash"])):
            raise ValueError("email or password is incorrect")
        return self._new_session(str(account["userId"]))

    def authenticate(self, token: str | None) -> UserProfile | None:
        if not token:
            return None
        token_hash = _hash_token(token)
        if self._db:
            row = self._db.connection.execute(
                "SELECT user_id, expires_at FROM auth_sessions WHERE token_hash = ?", (token_hash,)
            ).fetchone()
            if not row:
                return None
            if _as_datetime(row["expires_at"]) < local_now():
                return None
            return self._users.get_user(row["user_id"])
        session = self._sessions.get(token_hash)
        if not session or session["expiresAt"] < local_now():
            return None
        return self._users.get_user(str(session["userId"]))

    def _new_session(self, user_id: str) -> AuthSession:
        token = secrets.token_urlsafe(32)
        expires_at = local_now() + timedelta(days=30)
        if self._db:
            with self._db.transaction() as db:
                db.execute(
                    "INSERT INTO auth_sessions(id,user_id,token_hash,expires_at,created_at) VALUES(?,?,?,?,?)",
                    (str(uuid4()), user_id, _hash_token(token), expires_at.isoformat(), local_now().isoformat()),
                )
        else:
            self._sessions[_hash_token(token)] = {"userId": user_id, "expiresAt": expires_at}
        return AuthSession(token=token, user=self._users.get_user(user_id))

    def _find_account(self, email: str) -> dict[str, object] | None:
        if self._db:
            row = self._db.connection.execute(
                "SELECT user_id, email, password_hash, email_verified_at FROM auth_accounts WHERE email = ?",
                (email,),
            ).fetchone()
            if not row:
                return None
            return {
                "userId": row["user_id"],
                "passwordHash": row["password_hash"],
                "emailVerifiedAt": row["email_verified_at"],
            }
        return self._accounts.get(email)

    def _find_code(self, email: str) -> dict[str, object] | None:
        if self._db:
            row = self._db.connection.execute(
                "SELECT id, code_hash, expires_at, used_at FROM email_verification_codes WHERE email = ? ORDER BY created_at DESC LIMIT 1",
                (email,),
            ).fetchone()
            if not row:
                return None
            return {"id": row["id"], "hash": row["code_hash"], "expiresAt": row["expires_at"], "usedAt": row["used_at"]}
        return self._codes.get(email)

    @staticmethod
    def _normalize_email(email: str) -> str:
        email = email.strip().lower()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("valid email is required")
        return email


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return f"pbkdf2_sha256$240000${salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations))
        return secrets.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def _hash_code(email: str, code: str) -> str:
    return hashlib.sha256(f"{email}:{code}".encode()).hexdigest()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _as_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    from backend.app.core.dates import parse_datetime
    return parse_datetime(str(value))
