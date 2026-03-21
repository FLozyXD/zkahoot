from src.api.classes import TokenManager, RegistrationManager, ChangeCredentialsManager
from src.utils import UnifiedDict
from flask import Blueprint, request, abort, g

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register() -> dict:
    body = request.get_json()
    try:
        login, password = body["login"], body["password"]
    except KeyError:
        abort(400)
    rm = RegistrationManager(login, password)
    return rm.register()


@auth_bp.route("/change_login", methods=["POST"])
def change_login() -> dict:
    body = request.get_json()
    try:
        login = body["login"]
        password = body["password"]
        new_login = body["new_login"]
    except KeyError:
        abort(400)
    cm = ChangeCredentialsManager(login, password, new_login=new_login)
    return cm.change_login()


@auth_bp.route("/change_password", methods=["POST"])
def change_password() -> dict:
    body = request.get_json()
    try:
        login = body["login"]
        password = body["password"]
        new_password = body["new_password"]
    except KeyError:
        abort(400)
    cm = ChangeCredentialsManager(login, password, new_password=new_password)
    return cm.change_password()


@auth_bp.route("/make-token", methods=["POST"])
@auth_bp.route("/get-token", methods=["POST"])
def make_token() -> dict:
    body = request.get_json()
    try:
        login, password = body["login"], body["password"]
    except KeyError:
        abort(400)
    tm = TokenManager(login, password)
    return tm.make_token()


@auth_bp.route("/revoke-token", methods=["POST"])
def revoke_token() -> dict:
    body = request.get_json()
    try:
        login, password = body["login"], body["password"]
    except KeyError:
        abort(400)
    tm = TokenManager(login, password)
    return tm.revoke_token()


def require_token() -> None:
    """The function, needed to use with all the protected
    endpoints. Just call `blueprint.before_request(require_token)' and
    that will do all the setup. To get the user, who made the request,
    import `g' and do `user = g.user'. From this object you can get
    other information, such as id, login and password hash."""

    token_user_ud = UnifiedDict(name="token_user")
    try:
        token = request.headers["Authorization"]
        g.user = token_user_ud[token]
    except KeyError:
        abort(401)
