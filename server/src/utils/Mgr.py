from src.classes import User, Lobby, Quiz
from src.utils import DBWrapper, UnifiedDict
from src.exceptions import LobbyNotExistsError

from typing import Self
from sqlite3 import connect, IntegrityError
from abc import ABC, abstractmethod
from pathlib import Path
from secrets import token_hex
from contextlib import suppress


class AbstractLobbyMgr(ABC):
    @abstractmethod
    def __enter__(self) -> Self: ...

    @abstractmethod
    def __exit__(self) -> None: ...

    @property
    @abstractmethod
    def nbytes(self) -> int: ...

    @abstractmethod
    def create(
        self,
        name: str,
        user: User,
        quiz: Quiz,
    ) -> Lobby: ...

    @abstractmethod
    def revoke(self, token: str) -> None: ...

    @abstractmethod
    def select_by_token(self, token: str) -> Lobby: ...

    @abstractmethod
    def select_by_user(self, user: User) -> Lobby: ...

    @abstractmethod
    def join(self, token: str, user: User) -> None: ...

    @abstractmethod
    def kick(self, token: str, user: User) -> None: ...


class DBMgr:
    nbytes = 4
    default_path = Path(f"helper_dbs/{token_hex(nbytes)}.sqlite3")

    def __init__(self, path: Path | None = None) -> None:
        database = path if path else self.default_path
        self.conn = connect(database)
        self.cur = self.conn.cursor()

    def __enter__(self) -> Self:
        return self

    def __exit__(self) -> None:
        self.cur.close()
        self.conn.close()

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()


class LobbyDBMgr(AbstractLobbyMgr, DBMgr):
    default_path = Path("helper_dbs/lobbies.sqlite3")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        with open(Path("src/schemas/lobbies-schema.sql")) as script:
            sql = script.read()
        self.cur.executescript(sql)

    def _select_lobby_users(self, token: str) -> list[User]:
        users_rec = self.cur.execute(
            "select login from lobbies_users where token = ?", (token,)
        )
        users_ids = [login[0] for login in users_rec]
        users = []
        with DBWrapper() as dbw:
            for login in users_ids:
                users.append(dbw.select(User, login=login)[0])
        return users

    def _select_lobby_quiz(self, id: int) -> Quiz:
        with DBWrapper() as dbw:
            quiz = dbw.select(Quiz, id=id)[0]
        return quiz

    def create(
        self,
        name: str | None,
        user: User,
        quiz: Quiz,
    ) -> Lobby:
        lobby = Lobby(
            token_hex(self.nbytes),
            name,
            user.id,
            [user],
            quiz,
        )
        self.cur.execute(
            "insert into lobbies (?, ?, ?, ?)",
            tuple(lobby),
        )
        self.cur.execute(
            "insert into lobbies_users (?, ?)",
            (lobby.token, user.login),
        )
        return lobby

    def revoke(self, token: str) -> None:
        self.cur.execute("delete from lobbies_users where token = ?", (token,))
        self.cur.execute("delete from lobbies where token = ?", (token,))

    def select_by_token(self, token: str) -> Lobby:
        lobby_rec = self.cur.execute(
            "select * from lobbies where token = ?", (token,)
        )
        lobby_t = lobby_rec.fetchone()
        if not lobby_t:
            raise LobbyNotExistsError(token)
        users = self._select_lobby_users(token)
        quiz = self._select_lobby_quiz(lobby_t[3])

        lobby = Lobby(lobby_t[0], lobby_t[1], lobby_t[2], users, quiz)
        lobby.running = bool(lobby_t[-1])
        return lobby

    def select_by_user(self, user: User) -> Lobby:
        token_rec = self.cur.execute(
            "select token from lobbies_users where login = ?", (user.login,)
        )
        token = token_rec.fetchone()
        if not token:
            raise LobbyNotExistsError("void")
        lobby = self.select_by_token(token[0])
        return lobby

    def join(self, token: str, user: User) -> None:
        try:
            self.cur.execute(
                "insert into lobbies_users values (?, ?)", (token, user.login)
            )
        except IntegrityError:
            raise LobbyNotExistsError(token)

    def kick(self, token: str, user: User) -> None:
        self.cur.execute(
            "delete from lobbies_users where token = ? and login = ?",
            (token, user.login),
        )
        ul = self.cur.execute(
            "select from lobbies_users where token = ?", (token,)
        )
        if not ul.fetchone():
            self.cur.execute("delete from lobbies where token = ?", (token,))


class LobbyDictMgr(AbstractLobbyMgr):
    nbytes = 4

    def __init__(self) -> None:
        self.user_lobby = UnifiedDict("user_lobby")
        self.token_lobby = UnifiedDict("token_lobby")

    def __enter__(self) -> Self:
        return self

    def __exit__(self) -> None:
        pass

    def create(
        self,
        name: str,
        user: User,
        quiz: Quiz,
    ) -> Lobby:
        lobby = Lobby(token_hex(self.nbytes), name, user.id, [user], quiz)
        self.user_lobby[user.login] = lobby
        self.token_lobby[lobby.token] = lobby
        return lobby

    def revoke(self, token: str) -> None:
        with suppress(KeyError):
            lobby = self.token_lobby[token]
            del self.token_lobby[token]
            for user in lobby.users:
                del self.user_lobby[user.login]

    def select_by_token(self, token: str) -> Lobby:
        try:
            lobby = self.token_lobby[token]
        except KeyError:
            raise LobbyNotExistsError(token)
        return lobby

    def select_by_user(self, user: User) -> Lobby:
        try:
            lobby = self.user_lobby[user.login]
        except KeyError:
            raise LobbyNotExistsError("void")
        return lobby

    def join(self, token: str, user: User) -> None:
        try:
            lobby = self.token_lobby[token]
        except KeyError:
            raise LobbyNotExistsError(token)
        lobby.join(user)

    def kick(self, token: str, user: User) -> None:
        with suppress(KeyError):
            lobby = self.token_lobby[token]
            lobby.kick(user)
