from src.utils import DBWrapper, LobbyDictMgr
from src.classes import Quiz, Answer
from src.api.auth import Authorizer
from src.exceptions import LobbyNotExistsError

from flask import Blueprint, request, abort, g
from flask.views import MethodView
from time import sleep

lobby_bp = Blueprint("lobby", __name__, url_prefix="/lobby")
lobby_bp.before_request(Authorizer.require_token)


class LobbyAPI(MethodView):
    lobby_mgr_cls = LobbyDictMgr

    def __init__(self) -> None:
        self._verify_request()

    def _verify_request(self) -> None:
        pass


class InnerLobbyAPI(LobbyAPI):
    def __init__(self) -> None:
        super().__init__()
        with self.lobby_mgr_cls() as lobby_mgr:
            try:
                lobby_mgr.select_by_user(g.user)
            except LobbyNotExistsError:
                abort(404)


class OuterLobbyAPI(LobbyAPI):
    def __init__(self) -> None:
        super().__init__()
        with self.lobby_mgr_cls() as lobby_mgr:
            try:
                lobby_mgr.select_by_user(g.user)
            except LobbyNotExistsError:
                pass
            else:
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
        with self.lobby_mgr_cls() as lobby_mgr:
            lobby = lobby_mgr.create(self.name, g.user, self.quiz)
        return {"token": lobby.token}, 200


class JoinLobbyAPI(OuterLobbyAPI):
    def post(self, token: str) -> tuple[dict, int]:
        with self.lobby_mgr_cls() as lobby_mgr:
            try:
                lobby_mgr.join(token, g.user)
            except LobbyNotExistsError:
                abort(404)
        return "", 200


class ExitLobbyAPI(InnerLobbyAPI):
    def post(self) -> tuple[dict, int]:
        with self.lobby_mgr_cls() as lobby_mgr:
            lobby_mgr.kick(g.user)
        return "", 200


class RunLobbyAPI(InnerLobbyAPI):
    def post(self) -> tuple[dict, int]:
        with self.lobby_mgr_cls() as lobby_mgr:
            lobby = lobby_mgr.select_by_user(g.user)
        if g.user.id == lobby.owner_id:
            lobby.run()
            return "", 200
        else:
            abort(403)


class InfoLobbyAPI(InnerLobbyAPI):
    def get(self) -> tuple[dict, int]:
        with self.lobby_mgr_cls() as lobby_mgr:
            lobby = lobby_mgr.select_by_user(g.user)
        return lobby.to_json(), 200


class PollRunningLobbyAPI(LobbyAPI):
    def get(self, token: str) -> tuple[dict, int]:
        with self.lobby_mgr_cls() as lobby_mgr:
            try:
                lobby = lobby_mgr.select_by_token(token)
            except LobbyNotExistsError:
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
        except KeyError, TypeError:
            abort(400)

    def put(self) -> tuple[dict, int]:
        with self.lobby_mgr_cls() as lobby_mgr:
            lobby = lobby_mgr.select_by_user(g.user)
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
        with self.lobby_mgr_cls() as lobby_mgr:
            return [
                lobby.to_json()
                for lobby in lobby_mgr.select_by_name(self.query)
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
