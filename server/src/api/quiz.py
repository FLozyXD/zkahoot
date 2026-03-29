from flask import Blueprint, request, abort, g
from flask.views import MethodView
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from werkzeug.datastructures import ImmutableDict

from src.classes import Quiz, TextQuestion
from src.utils import DBWrapper
from src.api.auth import Authorizer

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")
quiz_bp.before_request(Authorizer.require_token)


class QuizAPI(MethodView):
    def __init__(self) -> None:
        self._verify_request()

    def _verify_request(self) -> None:
        pass


class RegisterQuiz(QuizAPI):
    def _verify_request(self) -> None:
        body = dict(request.get_json())

        resolved_body = {
            "id": None,
            "quiz_name": body["name"],
            "creator_id": g.user.id,
            "questions": [],
        }
        for q in body["questions"]:
            resolved_body["questions"].append({
                "id": None,
                "quiz_id": None,
                "question": q["text"],
                "answer": {
                    "id": None,
                    "answer": q["answer"],
                },
                "type_dependent": None,
            })

        body = ImmutableDict(resolved_body)
        try:
            self.quiz = Quiz.from_json(body)
        except KeyError:
            abort(400)

    def post(self) -> tuple[dict, int]:
        with DBWrapper() as dbw:
            try:
                dbw.insert(self.quiz)
            except UniqueViolation:
                abort(403)
        return {"status": "OK"}, 200


class DeleteQuiz(QuizAPI):
    def _verify_request(self) -> None:
        body = request.get_json()
        if not body:
            abort(400)
        try:
            self.quiz_id = body["id"]
        except KeyError:
            abort(400)

    def delete(self) -> tuple[dict, int]:
        with DBWrapper() as dbw:
            try:
                quizzes = dbw.select(Quiz, id=self.quiz_id, creator_id=g.user.id)
                if not quizzes:
                    abort(404)
                quiz = quizzes[0]
            except IndexError:
                abort(404)
            try:
                dbw.delete(quiz)
            except ForeignKeyViolation:
                abort(400)
        return {"status": "OK"}, 200


class ChangeQuiz(QuizAPI):
    def _verify_request(self) -> None:
        body = request.get_json()
        if not body:
            abort(400)
        try:
            self.quiz_id = body["quiz_id"]
            self.quiz_name = body["quiz_name"]
            self.questions = body["questions"]
        except KeyError:
            abort(400)

    def post(self) -> tuple[dict, int]:
        with DBWrapper() as dbw:
            try:
                quizzes = dbw.select(Quiz, id=self.quiz_id, creator_id=g.user.id)
                if not quizzes:
                    abort(404)
                existing_quiz = quizzes[0]
            except IndexError:
                abort(404)
            updated_quiz = Quiz(
                existing_quiz.id,
                self.quiz_name,
                existing_quiz.creator_id,
                [TextQuestion.from_json(q) for q in self.questions],
            )
            dbw.update(updated_quiz)
        return {"status": "OK"}, 200


class SearchQuiz(MethodView):
    def post(self) -> tuple[dict, int]:
        body = request.get_json()
        if not body:
            abort(400)
        try:
            quiz_name = body["quiz_name"]
        except KeyError:
            abort(400)
        with DBWrapper() as dbw:
            quizzes = dbw.select(Quiz, quiz_name=quiz_name)
            if not quizzes:
                return {"quizzes": []}, 200
            quizzes_json = [quiz.to_json() for quiz in quizzes]
        return {"quizzes": quizzes_json}, 200


quiz_bp.add_url_rule("/register", view_func=RegisterQuiz.as_view("register_quiz"))
quiz_bp.add_url_rule("/delete", view_func=DeleteQuiz.as_view("delete_quiz"))
quiz_bp.add_url_rule("/change", view_func=ChangeQuiz.as_view("change_quiz"))
quiz_bp.add_url_rule("/search", view_func=SearchQuiz.as_view("search_quiz"))
