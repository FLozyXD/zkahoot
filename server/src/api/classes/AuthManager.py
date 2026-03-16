from src.classes.User import User
from src.exceptions import UserNotExistsError, UserExistsError, LoginError
from src.utils import UnifiedDict

import secrets


class AuthManager:
    def __init__(self, login: str, password: str) -> None:
        self.user = User(None, login, password)


class RegistrationManager(AuthManager):
    def register(self) -> tuple(dict, int):
        try:
            self.exists()
        except UserExistsError as e:
            return {
                "status": "Forbidden",
                "cause": f"User with login {e.login} already exists.",
            }, 403
        else:
            self.user.to_database()
            return {"status": "OK"}, 200

    def exists(self) -> None:
        try:
            User.from_database(login=self.user.login)
        except UserNotExistsError:
            pass
        else:
            raise UserExistsError(self.user.login)


class TokenManager(AuthManager):
    def verify(self) -> bool:
        try:
            src = User.from_database(login=self.user.login)
        except UserNotExistsError:
            raise
        else:
            if self.user != src:
                raise LoginError

    def make_token(self) -> tuple(dict, int):
        try:
            self.verify()
        except UserNotExistsError as e:
            return {
                "status": "Forbidden",
                "cause": f"User with login {e.login} does not exist.",
            }, 403
        except LoginError:
            return {
                "status": "Forbidden",
                "cause": "Invalid credentials.",
            }, 403
        else:
            sessions = UnifiedDict(name="sessions")
            active = [
                item for item in sessions.items() if item[1] == self.user
            ]
            for key, _ in active:
                del sessions[key]
            token = f"Bearer {secrets.token_hex()}"
            sessions[token] = User.from_database(
                login=self.user.login, password_hash=self.user.password
            )
            return {"status": "OK", "token": token}, 200
