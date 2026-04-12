from src.classes.Quiz import Quiz
from src.classes.User import User
from src.classes.Answer import Answer
from typing import Iterator
import secrets


class Lobby:
    def __init__(
        self,
        token: str | None = None,
        name: str | None = None,
        owner_id: int | None = None,
        users: list[User] = [],
        quiz: Quiz = None,
    ) -> None:
        if token is None:
            self.token = secrets.token_hex()
        else:
            self.token = token
        if name is None:
            self.name = self.token
        else:
            self.name = name
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

    def compare(self, answers: list[Answer]) -> list[bool]:
        if self.running:
            return self.quiz.check(answers)
        raise ValueError

    def __iter__(self) -> Iterator:
        return iter(
            [
                self.token,
                self.name,
                self.owner_id,
                self.quiz.id,
                self.running,
            ]
        )

    def to_json(self) -> dict:
        return {
            "token": self.token,
            "name": self.name,
            "owner_id": self.owner_id,
            "users": [p.to_json()["login"] for p in self.users],
            "quiz": self.quiz.to_json(),
        }

    @staticmethod
    def from_json(lobby: dict):
        return Lobby(
            token=lobby["token"],
            name=lobby["name"],
            quiz=Quiz.from_json(lobby["quiz"]),
            users=[
                User.from_database(login=p["login"]) for p in lobby["users"]
            ],
            owner_id=lobby["owner_id"],
        )
