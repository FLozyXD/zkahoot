from src.classes.Quiz import Quiz
from src.classes.Question import TextQuestion
from src.classes.Answer import Answer
from src.classes.DBWrapper import DBWrapper
from src.api.blueprints.auth import require_token

from flask import Blueprint, request, abort, g
import secrets

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")
quiz_bp.before_request(require_token)

@quiz_bp.route("/create", methods=["POST"])
def create() -> tuple[Quiz, int]:
    body = request.get_json()
    try:
        questions = body["questions"]
    except KeyError:
        abort(404)
    try:
        quiz_name = body["quiz_name"]
    except KeyError:
        abort(404)
    quiz = Quiz(None, quiz_name, g.user.id, questions)
    quiz.to_database()
    return quiz, 200

@quiz_bp.route("/delete", methods=["POST"])
def delete() -> int:
    body = request.get_json()
    try:
        quiz_id = body["quiz_id"]
    except KeyError:
        abort(404) 
    db = DBWrapper() 
    # начинается сомнительный движ
    quiz = Quiz.from_database(id = quiz_id)
    for question in quiz.questions:
        db.delete(Answer, answer=question.answer.answer)
        db.delete(TextQuestion, id=question.id)
    db.delete(Quiz, id=quiz_id)
    return 200

@quiz_bp.route("/change", methods=["POST"])
def change() -> int:
    body = request.get_json()
    try:
        quiz_id = body["quiz_id"]
        quiz_name = body["quiz_name"]
        questions = body.get("questions", [])
    except KeyError:
        abort(404)
    quiz = Quiz.from_database(id = quiz_id)
    quiz.quiz_name = quiz_name
    quiz.questions = questions
    return 200

@quiz_bp.route("/search", methods=["GET"])
def search() -> tuple[list[Quiz], int]:
    body = request.get_json()
    try:
        quiz_name = body["quiz_name"]
    except KeyError:
        abort(404)
    quizes = []
    db = DBWrapper()
    result = db.select(Quiz, quiz_name = quiz_name)
    for part in result:
        questions = [
            TextQuestion.from_tuple(q)
            for q in db.select(TextQuestion, quiz_id=part[0])
        ]
        quizes.append(Quiz(result[0], result[1], result[2], questions=questions))
    return quizes, 200