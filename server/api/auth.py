# если будет хрень, она здесь

from ..classes import User
from ..exceptions import UserExistsError, UserNotExistsError, LoginError
from ..utils import UnifiedDict
from flask import Blueprint, request, abort
import secrets

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


class AuthManager:
    def __init__(self, login: str, password: str) -> None:
        self.user = User(login, password)


class RegistrationManager(AuthManager):
    def register(self) -> dict:
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
            User.from_database(login=self.login)
        except UserNotExistsError:
            pass
        else:
            raise UserExistsError(self.user.login)


class TokenManager(AuthManager):
    def verify(self) -> bool:
        trg = User(self.login, self.password)
        try:
            src = User.from_database(login=self.login)
        except UserNotExistsError:
            raise
        else:
            if trg != src:
                raise LoginError

    def make_token(self) -> dict:
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
            sessions = UnifiedDict("sessions")
            active = [
                item for item in sessions.items() if item[1] == self.user.login
            ]
            for key, _ in active:
                del sessions[key]
            token = secrets.token_hex()
            sessions[token] = self.user.login
            return {"status": "OK", "Token": token}, 200


@auth.route("/register", methods=["POST"])
def register() -> dict:
    body = request.get_json()
    try:
        login, password = body["user"]["login"], body["user"]["password"]
    except KeyError:
        abort(400)
    rm = RegistrationManager(login, password)
    return rm.register()


@auth.route("/get-token", methods=["POST"])
def get_token() -> dict:
    body = request.get_json()
    try:
        login, password = body["user"]["login"], body["user"]["password"]
    except KeyError:
        abort(400)
    tm = TokenManager(login, password)
    return tm.make_token()
