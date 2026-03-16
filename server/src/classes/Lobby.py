from src.classes.Quiz import Quiz
from src.classes.User import User
from src.classes.Answer import Answer
from secrets import token_hex


class Lobby:
    def __init__(
        self,
        quiz: Quiz,
        id: str = token_hex(),
        users: list[User] = [],
        owner_id: int | None = None,
    ) -> None:
        self.id = id
        self.owner_id = owner_id
        self.users = users
        self.quiz = quiz
        self.running = False

    def join(self, user: User) -> None:
        self.users.append(user)

    def run(self) -> None:
        self.running = True

    def check(self, answers: list[Answer]) -> list[bool]:
        return self.quiz.check(answers)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "users": [p.to_json() for p in self.users],
            "quiz": self.quiz.to_json(),
        }

    @staticmethod
    def from_json(lobby: dict) -> Lobby:
        return Lobby(
            quiz=Quiz.from_json(lobby["quiz"]),
            id=lobby["id"],
            users=[User.from_json(p) for p in lobby["users"]],
            owner_id=lobby["owner_id"],
        )
