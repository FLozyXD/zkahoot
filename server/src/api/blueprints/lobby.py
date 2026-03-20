from src.utils import UnifiedDict
from src.classes.Lobby import Lobby
from src.classes.Quiz import Quiz
from src.classes.Answer import Answer
from src.api.blueprints.auth import require_token

from flask import Blueprint, request, abort, g
from time import sleep

lobby_bp = Blueprint("lobby", __name__, url_prefix="/lobby")
lobby_bp.before_request(require_token)


@lobby_bp.route("/create", methods=["POST"])
def create() -> tuple[dict, int]:
    body = request.get_json()
    lobby_ud = UnifiedDict(name="lobby")
    user_lobby_ud = UnifiedDict(name="user_lobby")
    if user_lobby_ud.get(g.user.login) is None:
        quiz = Quiz.from_database(id=body["quiz_id"])
        lobby = Lobby(
            name=body["name"], owner_id=g.user.id, users=[g.user], quiz=quiz
        )
        lobby_ud[lobby.token] = lobby
        user_lobby_ud[g.user.login] = lobby
        return {"token": lobby.token}
    else:
        abort(403)


@lobby_bp.route("/join/<token>", methods=["POST"])
def join(token: str) -> tuple[str, int]:
    lobby_ud = UnifiedDict(name="lobby")
    user_lobby_ud = UnifiedDict(name="user_lobby")
    try:
        lobby = lobby_ud[token]
    except KeyError:
        abort(404)
    lobby.join(g.user)
    user_lobby_ud[g.user.login] = lobby
    return "", 200


@lobby_bp.route("/get-info", methods=["GET"])
def get_info() -> tuple[dict, int]:
    user_lobby_ud = UnifiedDict(name="user_lobby")
    try:
        lobby = user_lobby_ud[g.user.login]
    except KeyError:
        abort(404)
    return lobby.to_json(), 200


@lobby_bp.route("/exit", methods=["POST"])
def exit() -> tuple[str, int]:
    user_lobby_ud = UnifiedDict(name="user_lobby")
    lobby_ud = UnifiedDict(name="lobby")
    try:
        lobby = user_lobby_ud[g.user.login]
    except KeyError:
        abort(404)
    try:
        lobby.kick(g.user)
    except ValueError:
        abort(404)
    del user_lobby_ud[g.user.login]
    if not lobby.users:
        del lobby_ud[lobby.token]
    return "", 200


@lobby_bp.route("/run", methods=["POST"])
def run() -> tuple[str, int]:
    user_lobby_ud = UnifiedDict(name="user_lobby")
    try:
        lobby = user_lobby_ud[g.user.login]
    except KeyError:
        abort(404)
    if g.user.id == lobby.owner_id:
        lobby.run()
    else:
        abort(403)
    return "", 200


@lobby_bp.route("/compare", methods=["POST"])
def compare() -> tuple[dict, int]:
    body = request.get_json()
    try:
        answers = [Answer(None, a) for a in body["answers"]]
    except KeyError:
        abort(400)
    user_lobby_ud = UnifiedDict(name="user_lobby")
    lobby = user_lobby_ud[g.user.login]
    try:
        compared = lobby.check(answers)
    except ValueError:
        abort(403)
    return compared, 200


@lobby_bp.route("/poll-running/<token>", methods=["GET"])
def poll_running(token: str) -> tuple[str, int]:
    lobby_ud = UnifiedDict(name="lobby")
    try:
        lobby = lobby_ud[token]
    except KeyError:
        abort(404)
    while True:
        if lobby.running:
            return "", 200
        sleep(3)


@lobby_bp.route("/search", methods=["GET"])
def search() -> tuple[dict, int]:
    try:
        query = request.args["q"]
    except KeyError:
        abort(400)
    lobby_ud = UnifiedDict("lobby")
    return [
        lobby.to_json() for lobby in lobby_ud.items() if query in lobby.name
    ], 200
