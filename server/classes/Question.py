from abc import ABC, abstractmethod
from classes.DBWrapper import DBWrapper
from classes.Answer import Answer, TextAnswer


class AbstractQuestion(ABC):
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

    @abstractmethod
    @staticmethod
    def from_database(**query): ...

    @abstractmethod
    def to_json(self) -> dict: ...

    @abstractmethod
    @staticmethod
    def from_json(question: dict): ...


class Question(AbstractQuestion):
    def __init__(
        self, id: int, quiz_id: int, question: str, answer: Answer
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
        )

    @staticmethod
    def from_database(**query) -> AbstractQuestion:
        db = DBWrapper()
        question = db.select(Question, **query)[0]
        answer = TextAnswer.from_database(question["answer_id"])
        return Question(question[0], question[1], question[2], answer)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "quiz_id": self.quiz_id,
            "answer": self.answer.to_json(),
        }

    @staticmethod
    def from_json(question: dict) -> AbstractQuestion:
        return Question(
            question["id"],
            question["question"],
            question["quiz_id"],
            TextAnswer.from_json(question["answer"]),
        )
