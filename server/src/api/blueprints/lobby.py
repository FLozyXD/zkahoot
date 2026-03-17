from src.utils import UnifiedDict
from src.classes.Lobby import Lobby
from src.classes.Quiz import Quiz
from src.classes.Answer import Answer
from src.api.blueprints.auth import require_token

from flask import Blueprint, request, abort, g
import secrets

lobby_bp = Blueprint("lobby", __name__, "/lobby")
lobby_bp.before_request(require_token)


@lobby_bp.route("/search", methods=["GET"])
def search() -> tuple[dict, int]:
    lobby_ud = UnifiedDict(name="lobbies")
    try:
        q = request.args["q"]
    except KeyError:
        q = ""
    lobbies = [
        (lobby[0], lobby[1].to_json())
        for lobby in lobby_ud.items()
        if q in lobby_bp[1].quiz.quiz_name
    ]
    return dict(lobbies), 200


@lobby_bp.route("/create", methods=["POST"])
def create() -> tuple[dict, int]:
    lobby_ud = UnifiedDict(name="lobbies")
    body = request.get_json()
    try:
        quiz_id = body["quiz_id"]
    except KeyError:
        abort(400)
    try:
        quiz = Quiz.from_database(id=quiz_id)
    except IndexError:
        abort(404)
    lobby = Lobby(g.user.id, [g.user], quiz)
    token = secrets.token_hex()
    lobby_ud[token] = lobby
    return {"token": token}, 200


@lobby_bp.route("/join/<token>", methods=["POST"])
def join(token: str) -> tuple[str, int]:
    lobby_ud = UnifiedDict(name="lobbies")
    try:
        lobby = lobby_ud[token]
    except KeyError:
        abort(404)
    lobby.join(g.user)
    return "", 200


@lobby_bp.route("/exit/<token>", methods=["POST"])
def exit(token: str) -> tuple[str, int]:
    lobby_ud = UnifiedDict(name="lobbies")
    try:
        lobby = lobby_ud[token]
    except KeyError:
        abort(404)
    try:
        lobby.kick(g.user)
    except ValueError:
        abort(404)
    else:
        if not lobby.users:
            del lobby[token]
    return "", 200


@lobby_bp.route("/run/<token>", methods=["POST"])
def run(token: str) -> tuple[str, int]:
    lobby_ud = UnifiedDict(name="lobbies")
    user_quiz_ud = UnifiedDict(name="user_quiz")
    user = g.user
    try:
        lobby = lobby_ud[token]
    except KeyError:
        abort(404)
    if lobby.owner_id == user.id:
        lobby.run()
        for u in lobby.users:
            user_quiz_ud[u.login] = lobby.quiz
    else:
        abort(401)
    return "", 200


@lobby_bp.route("/compare", methods=["POST"])
def compare() -> tuple[dict, int]:
    body = request.get_json()
    try:
        answers = [Answer(None, answer) for answer in body["answers"]]
    except KeyError:
        abort(400)
    user_quiz_ud = UnifiedDict(name="user_quiz")
    user = g.user
    try:
        compared = user_quiz_ud[user.login].check(answers)
    except KeyError:
        abort(404)
    return {"answers": compared}, 200
