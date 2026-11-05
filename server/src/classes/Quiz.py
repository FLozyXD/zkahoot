from src.classes.Question import TextQuestion
from src.classes.Answer import Answer


class Quiz:
    def __init__(
        self,
        id: int | None,
        quiz_name: str,
        creator_id: int | None,
        questions: list[TextQuestion] = [],
    ) -> None:
        self.id = id
        self.quiz_name = quiz_name
        self.creator_id = creator_id
        self.questions = questions

    def __str__(self) -> str:
        return self.quiz_name

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter(
            [
                self.id,
                self.quiz_name,
                self.creator_id,
            ]
        )

    @staticmethod
    def _normalize(answer: Answer) -> str:
        return answer.answer.strip().casefold()

    def check(self, answers: list[Answer]) -> list[bool]:
        return [
            self._normalize(self.questions[i].answer)
            == self._normalize(answers[i])
            for i in range(len(answers))
        ]

    def immediate_check(
        self, answer: Answer, question_index: int
    ) -> bool:  # whynot
        return self._normalize(
            self.questions[question_index].answer
        ) == self._normalize(answer)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "quiz_name": self.quiz_name,
            "creator_id": self.creator_id,
            "questions": [question.to_json() for question in self.questions],
        }

    @staticmethod
    def from_json(quiz: dict):
        return Quiz(
            quiz["id"],
            quiz["quiz_name"],
            quiz["creator_id"],
            questions=[TextQuestion.from_json(q) for q in quiz["questions"]],
        )
