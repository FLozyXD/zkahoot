from abc import ABC, abstractmethod
from classes.DBWrapper import DBWrapper


class Answer(ABC):
    "Answer abstract class."

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
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
    def from_database(**query):
        pass

    @abstractmethod
    def to_json(self) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def from_json(answer: dict):
        pass


class TextAnswer(Answer):
    def __init__(self, id: int, answer: str) -> None:
        self.id = id
        self.answer = answer
        self.answer_type = "text"

    def __str__(self) -> str:
        return self.answer

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter([self.id, self.answer, self.answer_type])

    def to_database(self) -> None:
        db = DBWrapper()
        db.insert(self)

    def modify_database(self) -> None:
        db = DBWrapper()
        db.modify(self, id=self.id)

    @staticmethod
    def from_database(**query):
        db = DBWrapper()
        result = db.select(TextAnswer, **query)
        return TextAnswer(result[0], result[1])

    def to_json(self) -> dict:
        return {"id": self.id, "answer": self.answer, "type": self.answer_type}

    @staticmethod
    def from_json(answer: dict):
        return TextAnswer(answer["id"], answer["answer"])
