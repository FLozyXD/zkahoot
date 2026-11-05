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
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            abort(400)

        name = body.get("name")
        questions = body.get("questions")
        if not isinstance(name, str) or not name.strip():
            abort(400)
        if not isinstance(questions, list):
            abort(400)

        resolved_body = {
            "id": None,
            "quiz_name": name,
            "creator_id": g.user.id,
            "questions": [],
        }
        for q in questions:
            if not isinstance(q, dict):
                abort(400)
            text = q.get("text")
            answer = q.get("answer")
            if not isinstance(text, str) or not text.strip():
                abort(400)
            if not isinstance(answer, str) or not answer.strip():
                abort(400)
            resolved_body["questions"].append(
                {
                    "id": None,
                    "quiz_id": None,
                    "question": text,
                    "answer": {
                        "id": None,
                        "answer": answer,
                    },
                    "type_dependent": None,
                }
            )

        body = ImmutableDict(resolved_body)
        try:
            self.quiz = Quiz.from_json(body)
        except KeyError:
            abort(400)

    def post(self) -> tuple[str, int]:
        with DBWrapper() as dbw:
            try:
                dbw.insert(self.quiz)
            except UniqueViolation:
                abort(403)
        return "", 200


class DeleteQuiz(QuizAPI):
    def _verify_request(self) -> None:
        body = request.get_json()
        if not body:
            abort(400)
        try:
            self.quiz_id = body["quiz_id"]
        except KeyError:
            abort(400)

    def delete(self) -> tuple[str, int]:
        with DBWrapper() as dbw:
            try:
                quizzes = dbw.select(
                    Quiz, id=self.quiz_id, creator_id=g.user.id
                )
                if not quizzes:
                    abort(404)
                quiz = quizzes[0]
            except IndexError:
                abort(404)
            try:
                dbw.delete(quiz)
            except ForeignKeyViolation:
                abort(400)
        return "", 200


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

    def post(self) -> tuple[str, int]:
        with DBWrapper() as dbw:
            try:
                quizzes = dbw.select(
                    Quiz, id=self.quiz_id, creator_id=g.user.id
                )
                if not quizzes:
                    abort(404)
                existing_quiz = quizzes[0]
            except IndexError:
                abort(404)

            if not self.questions:
                abort(400)

            existing_questions = {
                question.id: question for question in existing_quiz.questions
            }
            resolved_questions = []

            try:
                for question in self.questions:
                    question = dict(question)
                    answer = dict(question["answer"])
                    question_id = question["id"]

                    if question_id is None:
                        answer["id"] = None
                    elif question_id in existing_questions:
                        answer["id"] = existing_questions[
                            question_id
                        ].answer.id
                    else:
                        abort(400)

                    question["quiz_id"] = existing_quiz.id
                    question["answer"] = answer
                    question.setdefault("type_dependent", None)
                    resolved_questions.append(question)
            except KeyError:
                abort(400)

            updated_quiz = Quiz(
                existing_quiz.id,
                self.quiz_name,
                existing_quiz.creator_id,
                [TextQuestion.from_json(q) for q in resolved_questions],
            )
            try:
                dbw.update(updated_quiz)
            except UniqueViolation:
                abort(403)
        return "", 200


class SearchQuiz(MethodView):
    def get(self) -> tuple[list[dict], int]:
        quiz_name = request.args.get("query")
        if quiz_name is None:
            abort(400)

        creator_id = request.args.get("creator_id")
        if creator_id is not None:
            try:
                creator_id = int(creator_id)
            except ValueError:
                abort(400)

        with DBWrapper() as dbw:
            quizzes = dbw.search_quizzes(quiz_name, creator_id)
            quizzes_json = [quiz.to_json() for quiz in quizzes]
        return quizzes_json, 200


quiz_bp.add_url_rule(
    "/register", view_func=RegisterQuiz.as_view("register_quiz")
)
quiz_bp.add_url_rule("/delete", view_func=DeleteQuiz.as_view("delete_quiz"))
quiz_bp.add_url_rule("/change", view_func=ChangeQuiz.as_view("change_quiz"))
quiz_bp.add_url_rule("/search", view_func=SearchQuiz.as_view("search_quiz"))
