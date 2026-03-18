from src.classes.Quiz import Quiz
from src.classes.User import User
from src.classes.Answer import Answer
from secrets import token_hex


class Lobby:
    def __init__(
        self,
        owner_id: int | None = None,
        users: list[User] = [],
        quiz: Quiz = None,
    ) -> None:
        self.owner_id = owner_id
        self.users = users
        self.quiz = quiz
        self.running = False

    def join(self, user: User) -> None:
        if not self.running and not len([u for u in self.users if u == user]):
            self.users.append(user)

    def kick(self, user: User) -> None:
        users_matching = [u for u in self.users if u == user]
        if not len(users_matching):
            raise ValueError
        for u in users_matching:
            self.users.remove(u)

    def run(self) -> None:
        self.running = True

    def check(self, answers: list[Answer]) -> list[bool]:
        return self.quiz.check(answers)

    def to_json(self) -> dict:
        return {
            "owner_id": self.owner_id,
            "users": [p.to_json() for p in self.users],
            "quiz": self.quiz.to_json(),
        }

    @staticmethod
    def from_json(lobby: dict):
        return Lobby(
            quiz=Quiz.from_json(lobby["quiz"]),
            users=[User.from_json(p) for p in lobby["users"]],
            owner_id=lobby["owner_id"],
        )
