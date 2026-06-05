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
        users: list[User] | None = None,
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
        self.users = users if users is not None else []
        self.quiz = quiz
        self.running = False
        self.results = {}

    def join(self, user: User) -> None:
        if not self.running and not len([u for u in self.users if u == user]):
            self.users.append(user)

    def kick(self, user: User) -> None:
        users_matching = [u for u in self.users if u == user]
        if not len(users_matching):
            return
        for u in users_matching:
            self.users.remove(u)

    def run(self) -> None:
        self.running = True

    def compare(self, answers: list[Answer]) -> list[bool]:
        if self.running:
            return self.quiz.check(answers)
        raise ValueError

    def save_result(self, user: User, answers: list[Answer]) -> list[bool]:
        compared = self.compare(answers)
        self.results[user.login] = {
            "login": user.login,
            "correct": sum(compared),
            "total": len(compared),
            "results": compared,
        }
        return compared

    def scoreboard(self) -> list[dict]:
        rows = []
        for user in self.users:
            result = self.results.get(user.login)
            if result is None:
                rows.append(
                    {
                        "login": user.login,
                        "correct": 0,
                        "total": len(self.quiz.questions),
                        "submitted": False,
                    }
                )
            else:
                rows.append(
                    {
                        "login": user.login,
                        "correct": result["correct"],
                        "total": result["total"],
                        "submitted": True,
                    }
                )
        return sorted(
            rows,
            key=lambda row: (row["submitted"], row["correct"]),
            reverse=True,
        )

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
        json = {
            "token": self.token,
            "name": self.name,
            "owner_id": self.owner_id,
            "users": [p.to_json()["login"] for p in self.users],
            "quiz": self.quiz.to_json(),
            "scoreboard": self.scoreboard(),
        }
        for q in json["quiz"]["questions"]:
            del q["answer"]
        return json

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
