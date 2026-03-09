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
        obj.id = self.db.one(sql, tuple(obj)[1:])

    def delete(self, obj) -> None:

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
