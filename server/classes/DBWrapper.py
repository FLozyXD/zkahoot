from postgres import Postgres


class DBWrapper:
    instance = None
    initialised = False

    def __new__(cls, *args, **kwargs) -> None:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, dsn: str = "postgresql://localhost/zkahoot") -> None:
        if not self.initialised:
            self.db = Postgres(dsn)
            self.initialised = True

    def insert(self, obj) -> None:
        match obj.__class__.__name__:
            case "User":
                sql = "INSERT INTO Users (login, password_hash) VALUES (%s, %s) RETURNING id"
            case "Quiz":
                sql = "INSERT INTO Quizzes (creator_id, creation_date, deletion_date) VALUES (%s, %s, %s) RETURNING id"
            case "Answer":
                sql = "INSERT INTO Answers (answer) VALUES (%s) RETURNING id"
            case "Question" | "TextQuestion":
                sql = "INSERT INTO Questions (quiz_id, question, question_type, answer_id, type_dependent) VALUES (%s, %s, %s, %s, %s) RETURNING id"
            case _:
                raise TypeError("Unsupported object type for insert")
        obj.id = self.db.one(sql, tuple(obj)[1:])

    def delete(self, cls_type, **query) -> None:
        match cls_type.__name__:
            case "User":
                table = "Users"
            case "Quiz":
                table = "Quizzes"
            case "Answer":
                table = "Answers"
            case "Question" | "TextQuestion":
                table = "Questions"
            case _:
                raise TypeError("Unsupported type for delete")
        if not query:
            raise ValueError(f"Attempted to delete ALL records from '{table}'")
        else:
            where_clause = " AND ".join([f"{key} = %s" for key in query.keys()])
            sql = f"DELETE FROM {table} WHERE {where_clause}"
            self.db.run(sql, tuple(query.values()))

    def select(self, cls_type, **query) -> list:
        match cls_type.__name__:
            case "User":
                table = "Users"
            case "Quiz":
                table = "Quizzes"
            case "Answer":
                table = "Answers"
            case "Question" | "TextQuestion":
                table = "Questions"
            case _:
                raise TypeError("Unsupported type for select")
        if not query:
            sql = f"SELECT * FROM {table}"
            result = [tuple(r) for r in self.db.all(sql)]
            return result
        else:
            where_clause = " AND ".join([f"{key} = %s" for key in query.keys()])
            sql = f"SELECT * FROM {table} WHERE {where_clause}"
            result = [tuple(r) for r in self.db.all(sql, tuple(query.values()))]
            return result

    def modify(self, obj, **query) -> None:
        match obj.__class__.__name__:
            case "User":
                table = "Users"
            case "Quiz":
                table = "Quizzes"
            case "Answer":
                table = "Answers"
            case "Question" | "TextQuestion":
                table = "Questions"
            case _:
                raise TypeError("Unsupported object type for modify")
        if not query:
            raise ValueError(f"Attempted to update ALL records from '{table}'")
        else:
            set_clause = ", ".join([f"{key} = %s" for key in query.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE id = %s"
            params = tuple(query.values()) + (obj.id,)
            self.db.run(sql, params)
            for key, value in query.items():
                setattr(obj, key, value)
