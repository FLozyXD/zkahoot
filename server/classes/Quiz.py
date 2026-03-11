from classes.Question import TextQuestion
from classes.Answer import Answer
from classes.DBWrapper import DBWrapper

class Quiz:
    def __init__(self, id: int | None, quiz_name: str, creator_id: int | None, questions: list[TextQuestion] = []) -> None:
        self.db = DBWrapper()
        self.id = id
        self.quiz_name = quiz_name
        self.creator_id = creator_id
        self.questions = questions

    def __str__(self) -> str:
        return self.quiz_name

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter([self.id, self.quiz_name, self.creator_id])
    
    def check(self, answers: list[Answer]) -> list[bool]:
        return [self.questions[i].answer == answers[i] for i in range(len(answers))]
    
    def immediate_check(self, answer: Answer, question_index: int) -> bool:  # whynot
        return self.questions[question_index].answer == answer

    def to_database(self) -> None:
        self.db.insert(self)
        for question in self.questions:
            question.quiz_id = self.id
            question.to_database()

    def modify_database(self) -> None:
        self.db.modify(self, id=self.id)

    @staticmethod
    def from_database(**query) -> Quiz:
        db = DBWrapper()
        result = db.select(Quiz, **query)[0]
        questions = [TextQuestion.from_tuple(q) for q in db.select(TextQuestion, quiz_id=result[0])]
        return Quiz(result[0], result[1], result[2], questions=questions)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "quiz_name": self.quiz_name,
            "creator_id": self.creator_id,
            "questions": [question.to_json() for question in self.questions]
        }

    @staticmethod
    def from_json(quiz: dict) -> Quiz:
        return Quiz(
            quiz["id"],
            quiz["quiz_name"],
            quiz["creator_id"],
            questions=[TextQuestion.from_json(q) for q in quiz["questions"]])