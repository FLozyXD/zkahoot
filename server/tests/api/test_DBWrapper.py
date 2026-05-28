import unittest
import psycopg2
from src.classes import Answer, TextQuestion, User, Quiz
from src.utils.DBWrapper import DBWrapper


class TestDBWrapper(unittest.TestCase):
    def setUp(self):
        self.dsn = "postgresql://localhost/zkahoot-test"
        self.conn = psycopg2.connect(self.dsn)
        self.conn.autocommit = True
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                login VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS quizzes (
                id SERIAL PRIMARY KEY,
                quiz_name VARCHAR(255) NOT NULL,
                creator_id INTEGER REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS answers (
                id SERIAL PRIMARY KEY,
                answer TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS questions (
                id SERIAL PRIMARY KEY,
                quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
                question TEXT NOT NULL,
                question_type VARCHAR(50) NOT NULL,
                answer_id INTEGER REFERENCES answers(id) ON DELETE CASCADE,
                type_dependent JSONB
            );
        """)

        cur.execute(
            "TRUNCATE users, quizzes, answers, questions RESTART IDENTITY CASCADE"
        )
        cur.close()

    def tearDown(self):
        self.conn.close()

    def _create_user(self, login, password) -> User:
        user = User(None, login, password, do_hash=True)
        with DBWrapper(self.dsn) as dw:
            dw.insert(user)
        return user

    def _create_quiz(self, name, creator_id, questions=None) -> Quiz:
        quiz = Quiz(None, name, creator_id, questions or [])
        with DBWrapper(self.dsn) as dw:
            dw.insert(quiz)
        return quiz

    def test_insert_user(self):
        user = User(None, "test_user", "password123", do_hash=True)
        with DBWrapper(self.dsn) as dw:
            dw.insert(user)
        self.assertIsNotNone(user.id)

        with DBWrapper(self.dsn) as dw:
            selected = dw.select(User, login="test_user")
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].login, "test_user")
        self.assertEqual(selected[0].password_hash, user.password_hash)

    def test_insert_answer(self):
        answer = Answer(None, "Test answer")
        with DBWrapper(self.dsn) as dw:
            dw.insert(answer)
        self.assertIsNotNone(answer.id)

        with DBWrapper(self.dsn) as dw:
            selected = dw.select(Answer, id=answer.id)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].answer, "Test answer")

    def test_insert_question(self):
        answer = Answer(None, "Q1 answer")
        quiz = Quiz(None, "Quiz for question", None, [])
        with DBWrapper(self.dsn) as dw:
            dw.insert(answer)
            dw.insert(quiz)
        question = TextQuestion(None, quiz.id, "Question text?", answer, None)
        with DBWrapper(self.dsn) as dw:
            dw.insert(question)
        self.assertIsNotNone(question.id)

        with DBWrapper(self.dsn) as dw:
            selected = dw.select(TextQuestion, id=question.id)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].question, "Question text?")
        self.assertEqual(selected[0].answer.answer, "Q1 answer")

    def test_insert_quiz_with_questions(self):
        user = self._create_user("quiz_creator", "pass")
        answer = Answer(None, "Quiz answer")
        with DBWrapper(self.dsn) as dw:
            dw.insert(answer)
        q1 = TextQuestion(None, None, "Q1", answer, None)
        quiz = Quiz(None, "Test Quiz", user.id, [q1])
        with DBWrapper(self.dsn) as dw:
            dw.insert(quiz)
        self.assertIsNotNone(quiz.id)
        self.assertIsNotNone(q1.id)
        self.assertEqual(q1.quiz_id, quiz.id)

        with DBWrapper(self.dsn) as dw:
            selected = dw.select(Quiz, id=quiz.id)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].quiz_name, "Test Quiz")
        self.assertEqual(len(selected[0].questions), 1)
        self.assertEqual(selected[0].questions[0].question, "Q1")

    def test_delete_user(self):
        user = self._create_user("to_delete", "pass")
        user_id = user.id
        with DBWrapper(self.dsn) as dw:
            dw.delete(user)
            selected = dw.select(User, id=user_id)
        self.assertEqual(len(selected), 0)

    def test_delete_quiz_cascade(self):
        user = self._create_user("quiz_owner", "pass")
        answer = Answer(None, "Answer")
        with DBWrapper(self.dsn) as dw:
            dw.insert(answer)
        q1 = TextQuestion(None, None, "Question", answer, None)
        quiz = Quiz(None, "Cascade Quiz", user.id, [q1])
        with DBWrapper(self.dsn) as dw:
            dw.insert(quiz)
        quiz_id = quiz.id
        q1_id = q1.id
        answer_id = answer.id

        with DBWrapper(self.dsn) as dw:
            dw.delete(quiz)
            self.assertEqual(len(dw.select(Quiz, id=quiz_id)), 0)
            self.assertEqual(len(dw.select(TextQuestion, id=q1_id)), 0)
            self.assertEqual(len(dw.select(Answer, id=answer_id)), 0)

    def test_update_user(self):
        user = self._create_user("old_login", "old_pass")
        new_user = User(user.id, "new_login", user.password_hash, do_hash=False)
        with DBWrapper(self.dsn) as dw:
            dw.update(new_user)
            selected = dw.select(User, id=user.id)
        self.assertEqual(selected[0].login, "new_login")
        self.assertEqual(selected[0].password_hash, user.password_hash)

    def test_update_quiz_only_name(self):
        user = self._create_user("updater", "pass")
        answer = Answer(None, "Answer")
        with DBWrapper(self.dsn) as dw:
            dw.insert(answer)
        q1 = TextQuestion(None, None, "Question", answer, None)
        quiz = Quiz(None, "Old name", user.id, [q1])
        with DBWrapper(self.dsn) as dw:
            dw.insert(quiz)
        quiz_id = quiz.id

        updated_quiz = Quiz(quiz_id, "New name", user.id, [q1])
        with DBWrapper(self.dsn) as dw:
            dw.update(updated_quiz)
            selected = dw.select(Quiz, id=quiz_id)
        self.assertEqual(selected[0].quiz_name, "New name")
        self.assertEqual(len(selected[0].questions), 1)

    def test_update_quiz_with_new_question_requires_delete(self):
        user = self._create_user("updater", "pass")
        old_answer = Answer(None, "Old answer")
        with DBWrapper(self.dsn) as dw:
            dw.insert(old_answer)
        old_question = TextQuestion(None, None, "Old question", old_answer, None)
        quiz = Quiz(None, "Quiz", user.id, [old_question])
        with DBWrapper(self.dsn) as dw:
            dw.insert(quiz)
        quiz_id = quiz.id
        old_question_id = old_question.id

        new_answer = Answer(None, "New answer")
        with DBWrapper(self.dsn) as dw:
            dw.insert(new_answer)
        new_question = TextQuestion(None, quiz_id, "New question", new_answer, None)

        with DBWrapper(self.dsn) as dw:
            dw.delete(old_question)
            dw.insert(new_question)
            updated_quiz = Quiz(quiz_id, "New name", user.id, [new_question])
            dw.update(updated_quiz)
            selected = dw.select(Quiz, id=quiz_id)

        self.assertEqual(selected[0].quiz_name, "New name")
        self.assertEqual(len(selected[0].questions), 1)
        self.assertEqual(selected[0].questions[0].question, "New question")
        self.assertEqual(selected[0].questions[0].answer.answer, "New answer")

    def test_select_user_by_login(self):
        user = self._create_user("select_me", "pass")
        with DBWrapper(self.dsn) as dw:
            selected = dw.select(User, login="select_me")
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].id, user.id)

    def test_select_quiz_by_name(self):
        user = self._create_user("owner", "pass")
        quiz = self._create_quiz("UniqueQuiz", user.id)
        with DBWrapper(self.dsn) as dw:
            selected = dw.select(Quiz, quiz_name="UniqueQuiz")
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].id, quiz.id)

    def test_select_question_by_quiz_id(self):
        user = self._create_user("q_owner", "pass")
        answer = Answer(None, "A")
        with DBWrapper(self.dsn) as dw:
            dw.insert(answer)
        q1 = TextQuestion(None, None, "Q1", answer, None)
        q2 = TextQuestion(None, None, "Q2", answer, None)
        quiz = Quiz(None, "MultiQuest", user.id, [q1, q2])
        with DBWrapper(self.dsn) as dw:
            dw.insert(quiz)
        with DBWrapper(self.dsn) as dw:
            selected = dw.select(TextQuestion, quiz_id=quiz.id)
        self.assertEqual(len(selected), 2)
        self.assertEqual({s.question for s in selected}, {"Q1", "Q2"})

    def test_insert_duplicate_user_raises(self):
        user1 = User(None, "duplicate", "pass1", do_hash=True)
        user2 = User(None, "duplicate", "pass2", do_hash=True)
        with DBWrapper(self.dsn) as dw:
            dw.insert(user1)
            with self.assertRaises(psycopg2.errors.UniqueViolation):
                dw.insert(user2)

    def test_select_empty_result(self):
        with DBWrapper(self.dsn) as dw:
            selected = dw.select(User, login="nonexistent")
        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
