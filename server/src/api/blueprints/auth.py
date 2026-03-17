from src.api.classes import TokenManager, RegistrationManager
from src.utils import UnifiedDict
from flask import Blueprint, request, abort, g

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register() -> dict:
    body = request.get_json()
    try:
        login, password = body["user"]["login"], body["user"]["password"]
    except KeyError:
        abort(400)
    rm = RegistrationManager(login, password)
    return rm.register()


@auth_bp.route("/get-token", methods=["POST"])
def get_token() -> dict:
    body = request.get_json()
    try:
        login, password = body["user"]["login"], body["user"]["password"]
    except KeyError:
        abort(400)
    tm = TokenManager(login, password)
    return tm.make_token()


def require_token() -> None:
    """The function, needed to use with all the protected
    endpoints. Just call `blueprint.before_request(require_token)' and
    that will do all the setup. To get the user, who made the request,
    import `g' and do `user = g.user'. From this object you can get
    other information, such as id, login and password hash."""

    sessions = UnifiedDict(name="sessions")
    try:
        token = request.headers["Authorization"]
        g.user = sessions[token]
    except KeyError:
        abort(401)
