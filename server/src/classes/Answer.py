from abc import ABC, abstractmethod


class AbstractAnswer(ABC):
    "Answer abstract class."

    @abstractmethod
    def __eq__(self, other) -> bool: ...

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __iter__(self): ...

    @abstractmethod
    def to_json(self) -> dict: ...

    @staticmethod
    @abstractmethod
    def from_json(answer: dict): ...

    @staticmethod
    @abstractmethod
    def from_tuple(answer: tuple): ...


class Answer(AbstractAnswer):
    def __eq__(self, other) -> bool:
        if not isinstance(other, Answer):
            return False
        return self.answer == other.answer

    def __init__(self, id: int | None, answer: str) -> None:
        self.id = id
        self.answer = answer

    def __str__(self) -> str:
        return self.answer

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter([self.id, self.answer])

    def to_json(self) -> dict:
        return {"id": self.id, "answer": self.answer}

    @staticmethod
    def from_json(answer: dict):
        return Answer(answer["id"], answer["answer"])

    @staticmethod
    def from_tuple(answer: tuple):
        return Answer(answer[0], answer[1])
