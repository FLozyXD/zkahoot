from flask import Blueprint, request, abort, session
from classes.User import User
from exceptions import UserExistsError, UserNotExistsError, LoginError

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


class AuthManager:
    def __init__(self, login: str, password: str) -> None:
        self.user = User(login, password)


class RegManager(AuthManager):
    def register(self) -> dict:
        try:
            self.exists()
        except UserExistsError as e:
            return {
                "status": "Forbidden",
                "cause": f"User with login {e.login} already exists.",
            }
        else:
            self.user.to_database()
            return {"status": "OK", "cause": None}

    def exists(self) -> None:
        try:
            User.from_database(login=self.login)
        except UserNotExistsError:
            pass
        else:
            raise UserExistsError(self.user.login)


class LoginManager(AuthManager):
    def verify(self) -> bool:
        trg = User(self.login, self.password)
        try:
            src = User.from_database(login=self.login)
        except UserNotExistsError:
            raise
        else:
            if trg != src:
                raise LoginError

    def set_session(self, session: dict) -> dict:
        try:
            self.verify()
        except UserNotExistsError as e:
            return {
                "status": "Forbidden",
                "cause": f"User with login {e.login} does not exist.",
            }
        except LoginError:
            return {
                "status": "Forbidden",
                "cause": "Invalid credentials.",
            }
        else:
            session["token"] = self.user.login
            return {"status": "OK", "cause": None}


@auth.route("/register", methods=["POST"])
def register() -> dict:
    body = request.get_json()
    try:
        login, password = body["user"]["login"], body["user"]["password"]
    except KeyError:
        abort(400)

    rm = RegManager(login, password)
    return rm.register()


@auth.route("/login", methods=["PUT"])
def login() -> dict:
    body = request.get_json()
    try:
        login, password = body["user"]["login"], body["user"]["password"]
    except KeyError:
        abort(400)

    lm = LoginManager(login, password)
    return lm.set_session(session)
