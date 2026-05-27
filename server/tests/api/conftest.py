# Относительный импорт (поднимаемся на 2 уровня вверх до корня)
import sys
from pathlib import Path
from flask import Flask
import pytest

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api import create_app
from src.utils.DBWrapper import DBWrapper
from src.utils.UnifiedDict import UnifiedDict


@pytest.fixture()
def app():
    config_path = Path(__file__).parent.parent.parent / "example_config.toml"
    app = create_app(config_path=config_path)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    dw = DBWrapper(dsn="postgresql://localhost/zkahoot")
    dw.truncate_tables(["answers", "questions", "quizzes", "users"])

    for d in UnifiedDict.objects.values():
        d.clear()

    yield app

    dw.truncate_tables(["answers", "questions", "quizzes", "users"])

    for d in UnifiedDict.objects.values():
        d.clear()


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


# ---------- Фикстуры пользователей ----------
@pytest.fixture
def valid_user():
    """Валидный пользователь (логин и пароль)"""
    return {"login": "client0", "password": "test_password"}


@pytest.fixture
def another_user():
    """Другой валидный пользователь"""
    return {"login": "client1", "password": "87654321"}


# ---------- Фикстуры для смены логина ----------
@pytest.fixture
def new_valid_login():
    """Новый валидный логин (не занят)"""
    return "client_new"


@pytest.fixture
def empty_login():
    """Пустой логин (невалидный)"""
    return ""


@pytest.fixture
def nonexistent_login():
    """Логин несуществующего пользователя"""
    return "ghost"


@pytest.fixture
def dummy_new_login():
    """Любой новый логин для теста с несуществующим пользователем"""
    return "anything"


# ---------- Фикстуры для смены пароля ----------
@pytest.fixture
def new_valid_password():
    """Новый валидный пароль (длина >= 8)"""
    return "newsecurepass123"


@pytest.fixture
def wrong_password():
    """Неверный пароль (не совпадает с паролем valid_user)"""
    return "wrongpassword"


@pytest.fixture
def short_password():
    """Слишком короткий пароль для регистрации (7 символов)"""
    return "1234567"


@pytest.fixture
def short_new_password():
    """Слишком короткий пароль для смены (5 символов)"""
    return "short"


@pytest.fixture
def another_new_password():
    """Другой валидный пароль для теста с несуществующим пользователем"""
    return "newpass123"
