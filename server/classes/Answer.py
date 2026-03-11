from abc import ABC, abstractmethod
from classes.DBWrapper import DBWrapper


class AbstractAnswer(ABC):
    "Answer abstract class."

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
    def from_json(answer: dict): ...

    @staticmethod
    @abstractmethod
    def from_tuple(answer: tuple): ...


class Answer(AbstractAnswer):
    def __init__(self, id: int | None, answer: str) -> None:
        self.id = id
        self.answer = answer

    def __str__(self) -> str:
        return self.answer

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter([self.id, self.answer])

    def to_database(self) -> None:
        db = DBWrapper()
        db.insert(self)

    def modify_database(self) -> None:
        db = DBWrapper()
        db.modify(self, id=self.id)

    @staticmethod
    def from_database(**query):
        db = DBWrapper()
        result = db.select(Answer, **query)[0]
        return Answer(result[0], result[1])

    def to_json(self) -> dict:
        return {"id": self.id, "answer": self.answer}

    @staticmethod
    def from_json(answer: dict):
        return Answer(answer["id"], answer["answer"])

    @staticmethod
    def from_tuple(answer: tuple):
        return Answer(answer[0], answer[1])
