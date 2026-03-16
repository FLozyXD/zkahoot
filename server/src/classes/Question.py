from abc import ABC, abstractmethod
from src.classes.DBWrapper import DBWrapper
from src.classes.Answer import Answer


class AbstractQuestion(ABC):
    "Question abstract class."

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __iter__(self): ...

    @abstractmethod
    def to_database(self) -> None: ...

    @abstractmethod
    def modify_database(self) -> None: ...

    @staticmethod
    @abstractmethod
    def from_database(**query): ...

    @abstractmethod
    def to_json(self) -> dict: ...

    @staticmethod
    @abstractmethod
    def from_json(question: dict): ...

    @staticmethod
    @abstractmethod
    def from_tuple(question: tuple): ...


class TextQuestion(AbstractQuestion):
    question_type = "text"

    def __init__(
        self,
        id: int | None,
        quiz_id: int,
        question: str,
        answer: Answer,
        type_dependent: str,
    ) -> None:
        self.id = id
        self.quiz_id = quiz_id
        self.question = question
        self.answer = answer
        self.type_dependent = type_dependent

    def __str__(self) -> str:
        return self.question

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter(
            [
                self.id,
                self.quiz_id,
                self.question,
                self.question_type,
                self.answer.id,
                self.type_dependent,
            ]
        )

    def to_database(self) -> None:
        db = DBWrapper()
        db.insert(self)

    def modify_database(self) -> None:
        db = DBWrapper()
        db.modify(
            self,
            id=self.id,
        )

    @staticmethod
    def from_database(**query) -> AbstractQuestion:
        db = DBWrapper()
        question = db.select(TextQuestion, **query)[0]
        answer = Answer.from_database(question["answer_id"])
        return TextQuestion(
            question[0],
            question[1],
            question[2],
            question[3],
            answer,
            question[4],
        )

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "quiz_id": self.quiz_id,
            "answer": self.answer.to_json(),
            "type_dependent": self.type_dependent,
            "question_type": self.question_type,
        }

    @staticmethod
    def from_json(question: dict) -> AbstractQuestion:
        return TextQuestion(
            question["id"],
            question["quiz_id"],
            question["question"],
            Answer.from_json(question["answer"]),
            question["type_dependent"],
        )

    @staticmethod
    def from_tuple(question: tuple):
        answer = Answer.from_database(question[4])
        return TextQuestion(
            question[0],
            question[1],
            question[2],
            answer,
            question[5],
        )
