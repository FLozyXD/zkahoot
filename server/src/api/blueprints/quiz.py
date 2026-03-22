from src.classes.Quiz import Quiz
from src.classes.Question import TextQuestion
from src.classes.Answer import Answer
from src.classes.DBWrapper import DBWrapper
from src.api.blueprints.auth import require_token

from flask import Blueprint, request, abort, g
from werkzeug.datastructures import ImmutableDict
from contextlib import suppress

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")
quiz_bp.before_request(require_token)


@quiz_bp.route("/create", methods=["POST"])
def create() -> tuple[dict, int]:
    body = dict(request.get_json())
    body["creator_id"] = g.user.id
    body = ImmutableDict(body)
    try:
        quiz = Quiz.from_json(body)
    except KeyError as e:
        print(e)
        abort(400)
    quiz.to_database()
    return quiz.to_json(), 200


@quiz_bp.route("/delete", methods=["DELETE"])
def delete() -> int:
    body = request.get_json()
    try:
        quiz_id = body["quiz_id"]
    except KeyError:
        abort(400)

    dw = DBWrapper()
    quiz = Quiz.from_database(id=quiz_id)

    if g.user.id != quiz.creator_id:
        abort(403)

    for question in quiz.questions:
        q_id = question.id
        a_id = question.answer.id
        dw.delete(TextQuestion, id=q_id)
        dw.delete(Answer, id=a_id)
    dw.delete(Quiz, id=quiz.id)
    return "", 200


@quiz_bp.route("/change", methods=["POST"])
def change() -> int:
    body = request.get_json()
    try:
        changed_quiz = Quiz.from_json(body)
    except KeyError:
        abort(400)

    old_quiz = Quiz.from_database(id=changed_quiz.id)
    if g.user.id != old_quiz.creator_id:
        abort(403)
    dw = DBWrapper()

    for question in old_quiz.questions:
        q_id = question.id
        a_id = question.answer.id
        dw.delete(TextQuestion, id=q_id)
        dw.delete(Answer, id=a_id)
    dw.delete(Quiz, id=old_quiz.id)

    changed_quiz.to_database()
    return "", 200


@quiz_bp.route("/search", methods=["GET"])
def search() -> tuple[list[dict], int]:
    args = dict(request.args)
    with suppress(KeyError):
        args["quiz_name"] = args["query"]
        del args["query"]

    if not args:
        abort(400)

    quizzes = []
    dw = DBWrapper()

    selected = dw.select(Quiz, **args)

    for q in selected:
        questions = [
            TextQuestion.from_tuple(q)
            for q in dw.select(TextQuestion, quiz_id=q[0])
        ]
        quizzes.append(Quiz(q[0], q[1], q[2], questions=questions))
    return [q.to_json() for q in quizzes], 200
