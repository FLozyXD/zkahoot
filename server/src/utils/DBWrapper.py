from src.classes import Answer, TextQuestion, User, Quiz

from typing import Iterable
import psycopg2


class DBWrapper:
    def __init__(self, dsn: str = "postgresql://localhost/zkahoot") -> None:
        self.dsn = dsn
        self.conn = psycopg2.connect(self.dsn)
        self.cur = self.conn.cursor()

    def __enter__(self) -> None:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.commit()
        self.close()

    def _make_clause(self, **query) -> str:
        items = list(query.items())
        sql = " AND ".join([f"{item[0]} = %s" for item in items])
        clause = self.cur.mogrify(sql, tuple([item[1] for item in items]))
        return clause.decode()

    def _insert_obj_setting_id(self, sql: str, obj: Iterable) -> None:
        obj_t = tuple(obj)
        self.cur.execute(sql + " RETURNING id", obj_t[1:])
        id = self.cur.fetchone()[0]
        setattr(obj, "id", id)

    def _delete_from_table(self, table: str, **query) -> None:
        clause = self._make_clause(**query)
        self.cur.execute(
            f"delete from {table} where {clause}",
        )

    def _select_from_table(self, table: str, **query) -> list[Iterable]:
        clause = self._make_clause(**query)
        self.cur.execute(f"select * from {table} where {clause}")
        iterables = self.cur.fetchall()
        return iterables

    def _insert_answer(self, obj) -> None:
        self._insert_obj_setting_id(
            "INSERT INTO answers (answer) VALUES (%s)",
            obj,
        )

    def _insert_question(self, obj) -> None:
        self._insert_answer(obj.answer)
        self._insert_obj_setting_id(
            """INSERT INTO questions
            (quiz_id, question, question_type, answer_id, type_dependent)
            VALUES (%s, %s, %s, %s, %s)""",
            obj,
        )

    def _insert_quiz(self, obj) -> None:
        self._insert_obj_setting_id(
            "INSERT INTO quizzes (quiz_name, creator_id) VALUES (%s, %s)",
            obj,
        )
        for q in obj.questions:
            setattr(q, "quiz_id", obj.id)
            self._insert_question(q)

    def _insert_user(self, obj) -> None:
        self._insert_obj_setting_id(
            "INSERT INTO users (login, password_hash) VALUES (%s, %s)", obj
        )

    def _delete_answer(self, obj) -> None:
        self._delete_from_table("answers", id=obj.id)

    def _delete_question(self, obj) -> None:
        self._delete_from_table("questions", id=obj.id)
        self._delete_answer(obj.answer)

    def _delete_quiz(self, obj) -> None:
        for question in obj.questions:
            self._delete_question(question)
        self._delete_from_table("quizzes", id=obj.id)

    def _delete_user(self, obj) -> None:
        quizzes = self._select_quiz(creator_id=obj.id)
        for quiz in quizzes:
            self._delete_quiz(quiz)
        self._delete_from_table("users", id=obj.id)

    def _update_answer(self, obj) -> None:
        obj_t = tuple(obj)[1:] + (obj.id,)
        self.cur.execute("UPDATE answers SET answer = %s WHERE id = %s", obj_t)

    def _update_question(self, obj) -> None:
        self._update_answer(obj.answer)
        obj_t = (obj.question, obj.question_type, obj.type_dependent, obj.id)
        self.cur.execute(
            """UPDATE questions
            SET question = %s,
            question_type = %s,
            type_dependent = %s
            WHERE id = %s""",
            obj_t,
        )

    def _update_quiz(self, obj) -> None:
        for q in obj.questions:
            self._update_question(q)
        obj_t = (obj.quiz_name, obj.id)
        self.cur.execute(
            "UPDATE quizzes SET quiz_name = %s WHERE id = %s",
            obj_t,
        )

    def _update_user(self, obj) -> None:
        obj_t = tuple(obj)[1:] + (obj.id,)
        self.cur.execute(
            "UPDATE users SET login = %s, password_hash = %s WHERE id = %s",
            obj_t,
        )

    def _select_answer(self, **query) -> list[Answer]:
        return [
            Answer(*obj_t)
            for obj_t in self._select_from_table("answers", **query)
        ]

    def _select_question(self, **query) -> list[Iterable]:
        questions = []
        for obj_t in self._select_from_table("questions", **query):
            answer = self._select_answer(id=obj_t[4])[0]
            question = TextQuestion(
                obj_t[0], obj_t[1], obj_t[2], answer, obj_t[5]
            )
            questions.append(question)
        return questions

    def _select_quiz(self, **query) -> list[Iterable]:
        quizzes = []
        for obj_t in self._select_from_table("quizzes", **query):
            questions = self._select_question(quiz_id=obj_t[0])
            quiz = Quiz(*obj_t[:3], questions)
            quizzes.append(quiz)
        return quizzes

    def _select_user(self, **query) -> list[Iterable]:
        return [
            User(*obj_t, do_hash=False)
            for obj_t in self._select_from_table("users", **query)
        ]

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()

    def close(self) -> None:
        self.cur.close()
        self.conn.close()

    def insert(self, obj: Answer | TextQuestion | User | Quiz) -> None:
        match obj.__class__.__name__:
            case "Answer":
                self._insert_answer(obj)
            case "TextQuestion":
                self._insert_question(obj)
            case "User":
                self._insert_user(obj)
            case "Quiz":
                self._insert_quiz(obj)
            case _:
                raise TypeError("Invalid class!")

    def delete(self, obj: Answer | TextQuestion | User | Quiz) -> None:
        match obj.__class__.__name__:
            case "Answer":
                self._delete_answer(obj)
            case "TextQuestion":
                self._delete_question(obj)
            case "User":
                self._delete_user(obj)
            case "Quiz":
                self._delete_quiz(obj)
            case _:
                raise TypeError("Invalid class!")

    def update(self, obj: Answer | TextQuestion | User | Quiz) -> None:
        match obj.__class__.__name__:
            case "Answer":
                self._update_answer(obj)
            case "TextQuestion":
                self._update_question(obj)
            case "User":
                self._update_user(obj)
            case "Quiz":
                self._update_quiz(obj)
            case _:
                raise TypeError("Invalid class!")

    def select(
        self, cls: Answer | TextQuestion | User | Quiz, **query
    ) -> list[Answer | TextQuestion | User | Quiz]:
        match cls.__name__:
            case "Answer":
                return self._select_answer(**query)
            case "TextQuestion":
                return self._select_question(**query)
            case "User":
                return self._select_user(**query)
            case "Quiz":
                return self._select_quiz(**query)
            case _:
                raise TypeError("Invalid class!")
