from src.classes.User import User
from src.exceptions import UserNotExistsError, UserExistsError, LoginError
from src.classes.DBWrapper import DBWrapper
from src.utils import UnifiedDict

from contextlib import suppress
from abc import ABC, abstractmethod
import secrets


class AuthManager(ABC):
    def __init__(self, login: str, password: str) -> None:
        self.user = User(None, login, password)

    @abstractmethod
    def validate(self) -> None: ...

    @abstractmethod
    def verify(self) -> tuple[dict, int] | None: ...


class AccountManager(AuthManager):
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


class TokenManager(AccountManager):
    def make_token(self) -> tuple[dict, int]:
        response = self.verify()
        if response is not None:
            return response
        else:
            token_user_ud = UnifiedDict(name="token_user")
            user_token_ud = UnifiedDict(name="user_token")
            user = User.from_database(
                login=self.user.login, password_hash=self.user.password_hash
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

class ChangeCredentialsManager(AccountManager):
    def __init__(self, login: str, password: str, new_login: str = None, new_password: str = None) -> None:
        super().__init__(login, password)
        self.new_login = new_login
        self.new_password = new_password
    
    def change_login(self) -> tuple[dict, int]:
        response = self.verify()
        if response is not None:
            return response
        try:
            User.from_database(login=self.new_login)
        except UserNotExistsError:
            pass  # логин свободен
        else:
            return {
                "status": "Forbidden",
                "cause": f"User with login {self.new_login} already exists.",
            }, 403
        user = User.from_database(login=self.user.login, password_hash=self.user.password_hash)
        old_login = user.login
        user.login = self.new_login

        dw = DBWrapper()
        dw.modify(user, login=user.login) 

        self._revoke_tokens(old_login)
        return {"status": "OK"}, 200

    def change_password(self) -> tuple[dict, int]:
        response = self.verify()
        if response is not None:
            return response
        user = User.from_database(login=self.user.login, password_hash=self.user.password_hash)
        user.password_hash = User._hash(self.new_password)

        dw = DBWrapper()
        dw.modify(user, password_hash=user.password_hash) 

        self._revoke_tokens(user.login)
        return {"status": "OK"}, 200

    def _revoke_tokens(self, login: str) -> None:
        token_user_ud = UnifiedDict(name="token_user")
        user_token_ud = UnifiedDict(name="user_token")
        try:
            token = user_token_ud[login]
            del token_user_ud[token]
            del user_token_ud[login]
        except KeyError:
            pass
