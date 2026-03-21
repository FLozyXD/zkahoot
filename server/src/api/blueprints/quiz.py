from src.classes.Quiz import Quiz
from src.classes.Question import TextQuestion
from src.classes.Answer import Answer
from src.classes.DBWrapper import DBWrapper
from src.api.blueprints.auth import require_token

from flask import Blueprint, request, abort, g

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")
quiz_bp.before_request(require_token)

@quiz_bp.route("/create", methods=["POST"])
def create() -> tuple[Quiz, int]:
    body = request.get_json()
    try:
        json_quiz = body["new_quiz"]
    except KeyError:
        abort(400)
    quiz = Quiz.from_json(json_quiz)
    quiz.to_database()
    return quiz, 200

@quiz_bp.route("/delete", methods=["DELETE"])
def delete() -> int:
    body = request.get_json()
    try:
        quiz_id = body["quiz_id"]
    except KeyError:
        abort(400) 
    db = DBWrapper() 
    quiz = Quiz.from_database(id = quiz_id)
    for question in quiz.questions:
        db.delete(Answer, id=question.answer.id)
        db.delete(TextQuestion, id=question.id)
    db.delete(Quiz, id=quiz_id)
    return 200

@quiz_bp.route("/change", methods=["POST"])
def change() -> int:
    changed_json = request.get_json()
    try:
        changed_quiz = Quiz.from_json(changed_json)
    except:
        abort(400)
    old_quiz = Quiz.from_database(id=changed_quiz.id)
    db = DBWrapper()
    for question in old_quiz.questions:
        db.delete(Answer, id=question.answer.id)
        db.delete(TextQuestion, id=old_quiz.id)
    db.delete(Quiz, id=old_quiz.id)
    changed_quiz.to_database()
    return 200

@quiz_bp.route("/search", methods=["GET"])
def search() -> tuple[list[Quiz], int]:
    try:
        quiz_name = request.args["quiz_name"]
    except:
        abort(400)
    quizes = []
    db = DBWrapper()
    result = db.select(Quiz, quiz_name = quiz_name)
    for part in result:
        questions = [
            TextQuestion.from_tuple(q)
            for q in db.select(TextQuestion, quiz_id=part[0])
        ]
        quizes.append(Quiz(part[0], part[1], part[2], questions=questions))
    return quizes, 200