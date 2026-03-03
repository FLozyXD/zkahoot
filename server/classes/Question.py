from abc import ABC, abstractmethod
from classes.DBWrapper import DBWrapper
from classes.Answer import Answer, TextAnswer


class Question(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass
@abstractmethod def __repr__(self) -> str: pass @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def to_database(self) -> None:
        pass

    @abstractmethod
    def modify_database(self) -> None:
        pass

    @staticmethod
    @abstractmethod
    def from_database(**query) -> Question:
        pass

    @abstractmethod
    def to_json(self) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def from_json(question: dict) -> Question:
        pass


class TextQuestion(Question):
    def __init__(
        self, id: int, quiz_id: int, question: str, answer: TextAnswer
    ) -> None:
        self.id = id
        self.quiz_id = quiz_id
        self.question = question
        self.answer = answer

    def __str__(self) -> str:
        return self.question

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter([self.id, self.quiz_id, self.question, self.answer.id])

    def to_database(self) -> None:
        db = DBWrapper()
        db.insert(self)

    def modify_database(self) -> None:
        db = DBWrapper()
        db.modify(
            self,
            id=self.id,
            text=self.question,
            quiz_id=self.quiz_id,
            answer_id=self.answer.id,
        )

    @staticmethod
    def from_database(**query) -> Question:
        db = DBWrapper()
        queston = db.select(TextQuestion, **query)
        answer = TextAnswer.from_database(question["answer_id"])
        return TextQuestion(question[0], question[1], question[2], answer)

    def to_json(self) -> dict:
        result = {
            "id": self.id,
            "question": self.question,
            "quiz_id": self.quiz_id,
            "answer": self.answer.to_json(),
            "answer_type": self.answer_type,
        }

    @staticmethod
    def from_json(question: dict) -> Question:
        return TextQuestion(
            question["id"],
            question["question"],
            question["quiz_id"],
            TextAnswer.from_json(question["answer"]),
        )
