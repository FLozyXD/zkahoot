from flask import Blueprint, request, abort, g
from flask.views import MethodView
from psycopg2.errors import UniqueViolation
from secrets import token_hex
from contextlib import suppress

from src.classes import User
from src.utils import DBWrapper, UnifiedDict

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


class UserAPI(MethodView):
    def __init__(self) -> None:
        body = request.get_json()
        try:
            login, password = body["login"], body["password"]
        except KeyError:
            abort(400)
        self.user = User(None, login, password)


class AuthorizedUserAPI(UserAPI):
    def __init__(self) -> None:
        super().__init__()
        with DBWrapper() as dbw:
            try:
                user = dbw.select(User, login=self.user.login)[0]
            except IndexError:
                abort(404)
        if user == self.user:
            self.user = user
            self.token_user_ud = UnifiedDict(name="token_user")
            self.user_token_ud = UnifiedDict(name="user_token")
        else:
            abort(403)


class RegisterAPI(UserAPI):
    def post(self) -> tuple[dict, int]:
        with DBWrapper() as dbw:
            try:
                dbw.insert(self.user)
            except UniqueViolation:
                abort(403)
        return {"status": "OK"}, 200


class TokenMakerAPI(AuthorizedUserAPI):
    def generate_token(self) -> str:
        return f"Bearer {token_hex()}"

    def authorize(self) -> str:
        try:
            return self.user_token_ud[self.user.login]
        except KeyError:
            token = self.generate_token()
            self.token_user_ud[token] = self.user
            self.user_token_ud[self.user.login] = token
            return token

    def post(self) -> tuple[dict, int]:
        return {"status": "OK", "token": self.authorize()}


class TokenRevokerAPI(AuthorizedUserAPI):
    def __init__(self) -> None:
        super().__init__()
        self.revoke()

    def revoke(self) -> None:
        with suppress(KeyError):
            token = self.user_token_ud[self.user.login]
            del self.token_user_ud[token]
            del self.user_token_ud[self.user.login]

    def post(self) -> tuple[dict, int]:
        return {"status": "OK"}


class Authorizer:
    @staticmethod
    def require_token() -> None:
        """The function, needed to use with all the protected
        endpoints. Just call `bp.before_request(Authorizer.require_token)' and
        that will do all the setup. To get the user, who made the request,
        import `g' and do `user = g.user'. From this object you can get
        other information, such as id, login and password hash."""

        token_user_ud = UnifiedDict(name="token_user")
        try:
            token = request.headers["Authorization"]
            g.user = token_user_ud[token]
        except KeyError:
            abort(401)


auth_bp.add_url_rule("/register", view_func=RegisterAPI.as_view("register"))
auth_bp.add_url_rule(
    "/make-token", view_func=TokenMakerAPI.as_view("make-token")
)
auth_bp.add_url_rule(
    "/get-token", view_func=TokenMakerAPI.as_view("get-token")
)
auth_bp.add_url_rule(
    "/revoke-token", view_func=TokenRevokerAPI.as_view("revoke-token")
)
