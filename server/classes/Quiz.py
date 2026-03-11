from classes.Question import TextQuestion
from classes.Answer import Answer
from classes.DBWrapper import DBWrapper

class Quiz:
    def __init__(self, id: int | None, quiz_name: str, creator_id: int) -> None:
        self.db = DBWrapper()
        self.id = id
        self.quiz_name = quiz_name
        self.creator_id = creator_id
        self.questions = [TextQuestion.from_tuple(q) for q in self.db.select(TextQuestion, quiz_id=self.id)]

    def __str__(self) -> str:
        return self.quiz_name

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter([self.id, self.quiz_name, self.creator_id])
    
    def check(self, answers: list[Answer]) -> list[bool]:
        return [str(self.questions[i].answer).lower() == str(answers[i]).lower() for i in range(len(answers))]
    
    def immediate_check(self, answer: Answer, question_index: int) -> bool:  # whynot
        return str(self.questions[question_index].answer).lower() == str(answer).lower()

    def to_database(self) -> None:
        self.db.insert(self)

    def modify_database(self) -> None:
        self.db.modify(self, id=self.id)

    @staticmethod
    def from_database(**query) -> Quiz:
        db = DBWrapper()
        result = db.select(Quiz, **query)[0]
        return Quiz(result[0], result[1], result[2])

    def to_json(self) -> dict:
        return {"id": self.id, "quiz_name": self.quiz_name, "creator_id": self.creator_id, "questions": self.questions}

    @staticmethod
    def from_json(quiz: dict) -> Quiz:
        return Quiz(quiz["id"], quiz["quiz_name"], quiz["creator_id"])