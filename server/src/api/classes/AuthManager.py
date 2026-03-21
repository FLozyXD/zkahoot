from src.classes.User import User
from src.exceptions import UserNotExistsError, UserExistsError, LoginError
from src.utils import UnifiedDict

from contextlib import suppress
import secrets


class AuthManager:
    def __init__(self, login: str, password: str) -> None:
        self.user = User(None, login, password)


class RegistrationManager(AuthManager):
    def validate(self) -> None:
        try:
            User.from_database(login=self.user.login)
        except UserNotExistsError:
            pass
        else:
            raise UserExistsError(self.user.login)

    def verify(self) -> tuple[dict, int] | None:
        try:
            self.validate()
        except UserExistsError as e:
            return {
                "status": "Forbidden",
                "cause": f"User with login {e.login} already exists.",
            }, 403
        return None

    def register(self) -> tuple[dict, int]:
        response = self.verify()
        if response is not None:
            return response
        else:
            self.user.to_database()
            return {"status": "OK"}, 200


class TokenManager(AuthManager):
    def validate(self) -> None:
        src = User.from_database(login=self.user.login)
        if self.user != src:
            raise LoginError

    def verify(self) -> tuple[dict, int] | None:
        try:
            self.validate()
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
        return None

    def make_token(self) -> tuple[dict, int]:
        response = self.verify()
        if response is not None:
            return response
        else:
            token_user_ud = UnifiedDict(name="token_user")
            user_token_ud = UnifiedDict(name="user_token")
            user = User.from_database(
                login=self.user.login, password_hash=self.user.password
            )
            try:
                token = user_token_ud[user.login]
            except KeyError:
                token = f"Bearer {secrets.token_hex()}"
                token_user_ud[token] = user
                user_token_ud[user.login] = token
            return {"status": "OK", "token": token}, 200

    def revoke_token(self) -> tuple[dict, int]:
        response = self.verify()
        if response is not None:
            return response
        else:
            token_user_ud = UnifiedDict(name="token_user")
            user_token_ud = UnifiedDict(name="user_token")
            with suppress(KeyError):
                token = user_token_ud[self.user.login]
                del token_user_ud[token]
                del user_token_ud[self.user.login]
            return {"status": "OK"}, 200
