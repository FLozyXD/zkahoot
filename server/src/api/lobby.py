from src.utils import DBWrapper, UnifiedDict
from src.classes import Lobby, Quiz, Answer
from src.api.auth import Authorizer

from flask import Blueprint, request, abort, g
from flask.views import MethodView
from time import sleep

lobby_bp = Blueprint("lobby", __name__, url_prefix="/lobby")
lobby_bp.before_request(Authorizer.require_token)


class LobbyAPI(MethodView):
    def __init__(self) -> None:
        self.token_lobby_ud = UnifiedDict(name="lobby_user")
        self.user_lobby_ud = UnifiedDict(name="user_lobby")
        self._verify_request()

    def _verify_request(self) -> None:
        pass


class InnerLobbyAPI(LobbyAPI):
    def __init__(self) -> None:
        super().__init__()
        if g.user.login not in self.user_lobby_ud:
            abort(404)


class OuterLobbyAPI(LobbyAPI):
    def __init__(self) -> None:
        super().__init__()
        if g.user.login in self.user_lobby_ud:
            abort(403)


class CreateLobbyAPI(OuterLobbyAPI):
    def __init__(self) -> None:
        super().__init__()
        body = request.get_json()
        self.name = body["name"]
        quiz_id = body["quiz_id"]
        with DBWrapper() as dbw:
            try:
                quizzes = dbw.select(Quiz, id=quiz_id)
                self.quiz = quizzes[0]
            except IndexError:
                abort(404)

    def _verify_request(self) -> None:
        body = request.get_json()
        try:
            body["name"]
            body["quiz_id"]
        except KeyError:
            abort(400)

    def post(self) -> tuple[dict, int]:
        lobby = Lobby(None, self.name, g.user.id, [g.user], self.quiz)
        self.user_lobby_ud[g.user.login] = lobby
        self.token_lobby_ud[lobby.token] = lobby
        return {"token": lobby.token}, 200


class JoinLobbyAPI(OuterLobbyAPI):
    def post(self, token: str) -> tuple[dict, int]:
        try:
            lobby = self.token_lobby_ud[token]
        except KeyError:
            abort(404)
        lobby.join(g.user)
        self.user_lobby_ud[g.user.login] = lobby
        return "", 200


class ExitLobbyAPI(InnerLobbyAPI):
    def post(self) -> tuple[dict, int]:
        lobby = self.user_lobby_ud[g.user.login]
        lobby.kick(g.user)
        del self.user_lobby_ud[g.user.login]
        if not lobby.users:
            del self.token_lobby_ud[lobby.token]
        return "", 200


class RunLobbyAPI(InnerLobbyAPI):
    def post(self) -> tuple[dict, int]:
        lobby = self.user_lobby_ud[g.user.login]
        if g.user.id == lobby.owner_id:
            lobby.run()
            return "", 200
        else:
            abort(403)


class InfoLobbyAPI(InnerLobbyAPI):
    def get(self) -> tuple[dict, int]:
        lobby = self.user_lobby_ud[g.user.login]
        return lobby.to_json(), 200


class PollRunningLobbyAPI(LobbyAPI):
    def get(self, token: str) -> tuple[dict, int]:
        try:
            lobby = self.token_lobby_ud[token]
        except KeyError:
            abort(404)
        while True:
            if lobby.running:
                return "", 200
            sleep(3)


class CompareLobbyAPI(InnerLobbyAPI):
    def __init__(self) -> None:
        super().__init__()
        body = request.get_json()
        self.answers = [Answer(None, answer) for answer in body["answers"]]

    def _verify_request(self) -> None:
        body = request.get_json()
        try:
            body["answers"]
        except KeyError:
            abort(400)

    def put(self) -> tuple[dict, int]:
        lobby = self.user_lobby_ud[g.user.login]
        if lobby.running:
            compared = lobby.compare(self.answers)
            return compared, 200
        abort(403)


class SearchLobbyAPI(LobbyAPI):
    def __init__(self) -> None:
        super().__init__()
        self.query = request.args["query"]

    def _verify_request(self) -> None:
        try:
            request.args["query"]
        except KeyError:
            abort(400)

    def get(self) -> tuple[list[dict], int]:
        return [
            lobby.to_json()
            for lobby in self.token_lobby_ud.values()
            if self.query in lobby.name
        ], 200


lobby_bp.add_url_rule("/create", view_func=CreateLobbyAPI.as_view("create"))
lobby_bp.add_url_rule("/join/<token>", view_func=JoinLobbyAPI.as_view("join"))
lobby_bp.add_url_rule("/exit", view_func=ExitLobbyAPI.as_view("exit"))
lobby_bp.add_url_rule("/run", view_func=RunLobbyAPI.as_view("run"))
lobby_bp.add_url_rule("/get-info", view_func=InfoLobbyAPI.as_view("get-info"))
lobby_bp.add_url_rule(
    "/poll-running/<token>",
    view_func=PollRunningLobbyAPI.as_view("poll-running"),
)
lobby_bp.add_url_rule("/compare", view_func=CompareLobbyAPI.as_view("compare"))
lobby_bp.add_url_rule("/search", view_func=SearchLobbyAPI.as_view("search"))
