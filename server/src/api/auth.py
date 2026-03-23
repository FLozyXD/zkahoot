from flask import Blueprint, request, abort, g
from flask.views import MethodView
from psycopg2.errors import UniqueViolation

from src.classes import User
from utils import DBWrapper

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


class RegisterAPI(MethodView):
    def post(self) -> tuple[dict, int]:
        body = request.get_json()
        try:
            login, password = body["login"], body["password"]
        except KeyError:
            abort(400)
        user = User(None, login, password)
        with DBWrapper() as dbw:
            try:
                dbw.insert(user)
            except UniqueViolation:
                abort(403)
        return {"status": "OK"}, 200


auth_bp.add_url_rule("/register", view_func=RegisterAPI.as_view())
