import sys
from pathlib import Path
from flask import Flask
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api import create_app
from src.utils.DBWrapper import DBWrapper
from src.utils.UnifiedDict import UnifiedDict


@pytest.fixture()
def app():
    config_path = Path(__file__).parent.parent.parent / "example_config.toml"
    app = create_app(config_path=config_path)
    app.config.update({"TESTING": True})
    yield app
    # очистка после всех тестов
    dw = DBWrapper(dsn="postgresql://localhost/zkahoot")
    dw.truncate_tables(["answers", "questions", "quizzes", "users"])
    for d in UnifiedDict.objects.values():
        d.clear()


@pytest.fixture()
def client(app):
    return app.test_client()
