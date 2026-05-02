from abc import ABC, abstractmethod
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
    def to_json(self) -> dict: ...

    @staticmethod
    @abstractmethod
    def from_json(question: dict): ...


class TextQuestion(AbstractQuestion):
    question_type = "text"

    def __init__(
        self,
        id: int | None,
        quiz_id: int,
        question: str,
        answer: Answer,
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
        return iter(
            [
                self.id,
                self.quiz_id,
                self.question,
                self.question_type,
                self.answer.id,
            ]
        )

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "quiz_id": self.quiz_id,
            "answer": self.answer.to_json(),
            "question_type": self.question_type,
        }

    @staticmethod
    def from_json(question: dict) -> AbstractQuestion:
        return TextQuestion(
            question["id"],
            question["quiz_id"],
            question["question"],
            Answer.from_json(question["answer"]),
        )
