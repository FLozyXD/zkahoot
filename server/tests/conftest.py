import pytest
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import api
from src.utils import UnifiedDict


@pytest.fixture(scope="function")
def app():
    """Создание Flask приложения для тестирования"""
    app = api.create_app()
    app.config.update({"TESTING": True, "SECRET_KEY": "test-secret-key"})

    # Очищаем данные перед тестом
    for d in UnifiedDict.objects.values():
        d.clear()

    yield app

    # Очищаем после теста
    for d in UnifiedDict.objects.values():
        d.clear()


@pytest.fixture(scope="function")
def client(app):
    """Тестовый клиент"""
    return app.test_client()
