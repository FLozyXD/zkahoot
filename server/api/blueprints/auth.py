from api.classes import TokenManager, RegistrationManager
from flask import Blueprint, request, abort

auth = Blueprint("auth", __name__, url_prefix="/auth")


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
