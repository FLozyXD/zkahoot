class DBWrapper:
    instance = None
    initialised = False

    def __new__(cls, *args, **kwargs) -> None:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, dsn: str) -> None:
        if not self.initialised:
            self.db = Postgres(dsn)
            self.initialised = True

    def search_id(self, obj):
        if hasattr(obj, "id") and obj.id is not None:
            return obj.id

        params = None
        sql = ""

        match obj:
            case User():
                sql = "SELECT id FROM Users WHERE login = %s"
                params = (obj.login,)
            case Quiz():
                sql = "SELECT id FROM Quizzes WHERE creator_id = %s AND creation_date = %s"
                params = (obj.creator_id, obj.creation_date)
            case Answer():
                sql = "SELECT id FROM Answers WHERE answer = %s"
                params = (obj.answer,)
            case Question():
                sql = "SELECT id FROM Questions WHERE quiz_id = %s AND question = %s"
                params = (obj.quiz_id, obj.question)

        if sql:
            found_id = self.db.one(sql, params)
            if found_id:
                obj.id = found_id
                return found_id
        raise ValueError(f"Не удалось найти ID для {obj.__class__.__name__}.")

    def insert(self, obj) -> None:
        match obj:
            case User():
                sql = "INSERT INTO Users (login, password_hash) VALUES (%s, %s) RETURNING id"
            case Quiz():
                sql = "INSERT INTO Quizzes (creator_id, creation_date, deletion_date) VALUES (%s, %s, %s) RETURNING id"
            case Answer():
                sql = "INSERT INTO Answers (answer) VALUES (%s) RETURNING id"
            case Question():
                sql = "INSERT INTO Questions (quiz_id, question, question_type, answer_id) VALUES (%s, %s, %s, %s) RETURNING id"
            case _:
                raise TypeError("Unsupported object type for insert")
        obj.id = self.db.one(sql, tuple(obj))

    def delete(self, obj) -> None:
        obj.id = self.search_id(obj)

        match obj:
            case User():
                table = "Users"
            case Quiz():
                table = "Quizzes"
            case Answer():
                table = "Answers"
            case Question():
                table = "Questions"
            case _:
                raise TypeError("Unsupported object type for delete")

        sql = f"DELETE FROM {table} WHERE id = %s"
        self.db.run(sql, (obj.id,))
        obj.id = None

    def select(self, cls_type, **query) -> list:
        match cls_type:
            case _ if cls_type is User:
                table = "Users"
            case _ if cls_type is Quiz:
                table = "Quizzes"
            case _ if cls_type is Answer:
                table = "Answers"
            case _ if cls_type is Question:
                table = "Questions"
            case _:
                raise TypeError("Unsupported type for select")

        if not query:
            sql = f"SELECT * FROM {table}"
            return self.db.all(sql)
        else:
            where_clause = " AND ".join([f"{key} = %s" for key in query.keys()])
            sql = f"SELECT * FROM {table} WHERE {where_clause}"
            return self.db.all(sql, tuple(query.values()))

    def modify(self, obj, **query) -> None:

        if not query:
            return

        obj.id = self.search_id(obj)

        match obj:
            case User():
                table = "Users"
            case Quiz():
                table = "Quizzes"
            case Answer():
                table = "Answers"
            case Question():
                table = "Questions"
            case _:
                raise TypeError("Unsupported object type for modify")

        set_clause = ", ".join([f"{key} = %s" for key in query.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE id = %s"

        params = tuple(query.values()) + (obj.id,)

        self.db.run(sql, params)

        for key, value in query.items():
            setattr(obj, key, value)
