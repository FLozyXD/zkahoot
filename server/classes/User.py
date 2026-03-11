import hashlib

from exceptions import UserNotExistsError
from classes.DBWrapper import DBWrapper


class User:
    # Attribute __slots__ is declared and often used in these methods
    # because it guarantees an immutable set of properties.
    # Reference: https://docs.python.org/3/reference/datamodel.html#object.__slots__
    __slots__ = "id", "login", "password"

    def __init__(
        self, id_: int | None, login: str, password: str, /, *, do_hash: bool = True
    ) -> None:
        # It's critical that no empty arguments make their way here.
        # Arguments are also assumed to be sanitized.
        self.id = id_
        self.login = login
        self.password = self._hash(password) if do_hash else password

    @staticmethod
    def _hash(data: str) -> str:
        # TODO: Consider moving this to an external class?
        return hashlib.blake2b(data.encode()).hexdigest()

    def __str__(self) -> str:
        return self.login

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        for slot in User.__slots__:
            yield getattr(self, slot)

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        # TODO: Since ID is a primary key, do we have to compare _every_ property?
        return all(getattr(self, s) == getattr(other, s) for s in User.__slots__)

    def to_database(self) -> None:
        db = DBWrapper()
        db.insert(self)

    def modify_database(self) -> None:
        db = DBWrapper()
        db.modify(self)

    @staticmethod
    def from_database(**query) -> Optional[None]:
        db = DBWrapper()
        if not (users := db.select(User, **query)):
            raise UserNotExistsError(query["login"])
        params = [users[0][s] for s in User.__slots__]
        # Database stores a hashsum. Don't hash it again.
        return User(*params, do_hash=False)

    def to_json(self) -> dict:
        return {s: getattr(self, s) for s in User.__slots__}

    @staticmethod
    def from_json(user: dict, /) -> User:
        params = [user[s] for s in User.__slots__]
        return User(*params)
