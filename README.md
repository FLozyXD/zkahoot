# zkahoot — API платформы квизов

Серверная часть Kahoot-подобной платформы: регистрация пользователей,
создание квизов, лобби и проведение игры в реальном времени.

Проект демонстрирует проектирование REST API на Flask, работу с PostgreSQL
без ORM и разделение слоёв «HTTP → бизнес-логика → БД».

## Возможности

- Регистрация, смена логина и пароля.
- Выдача и отзыв Bearer-токенов.
- CRUD квизов и вопросов (текстовые ответы и вопросы с вариантами).
- Поиск квизов и лобби.
- Создание лобби, присоединение по токену, выход, запуск игры.
- Опрос состояния лобби и сравнение ответов.
- Документированное API с примерами запросов и ответов.

## Стек

- Python 3.11+
- Flask 3.1, blueprints
- PostgreSQL, `psycopg2`, SQL без ORM
- Gunicorn + gevent
- `unittest`-тесты API

## Архитектура

```text
server/
  __main__.py             запуск dev-сервера
  example_config.toml     шаблон конфигурации
  src/
    scheme.sql            схема PostgreSQL
    api/
      __init__.py         create_app(), регистрация blueprints
      auth.py             регистрация, токены, смена данных
      quiz.py             CRUD квизов
      lobby.py            лобби и игровой процесс
    classes/              Answer, Question, Quiz, User, Lobby
    utils/
      DBWrapper.py        обёртка psycopg2 и SQL-запросы
      UnifiedDict.py      двусторонний словарь для токенов
    exceptions/           доменные исключения
  tests/api/              тесты auth и quiz
  docs/README.md          описание API
media/uml.png             UML-диаграмма
```

Токены и состояние лобби хранятся в памяти процесса. Это осознанное
упрощение: для нескольких воркеров нужен Redis или другая общая шина.

## UML

![UML-диаграмма](media/uml.png)

## Запуск

1. Создайте базу и примените схему:

```bash
createdb zkahoot
psql -d zkahoot -f server/src/scheme.sql
```

2. Установите зависимости и создайте конфигурацию:

```bash
python -m venv .venv
# активируйте venv
pip install -r server/requirements.txt
cp server/example_config.toml server/config.toml
```

В `server/config.toml` замените `SECRET_KEY` на случайное значение:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

3. Укажите DSN (по умолчанию `postgresql://localhost/zkahoot`):

```bash
# Windows PowerShell
$env:ZKAHOOT_DSN="postgresql://postgres:password@localhost:5432/zkahoot"
# Linux/macOS
export ZKAHOOT_DSN="postgresql://postgres:password@localhost:5432/zkahoot"
```

4. Запуск:

```bash
cd server
python __main__.py
```

Или через Gunicorn:

```bash
cd server
gunicorn 'src.api:create_app("config.toml")'
```

API доступно по адресу `http://localhost:5000/api`.

## API

Полное описание с JSON-примерами — [`server/docs/README.md`](server/docs/README.md).

Основные группы:

| Группа | Эндпоинты |
|---|---|
| Auth | `/api/auth/register`, `/change-login`, `/change-password`, `/get-token`, `/revoke-token` |
| Quiz | `/api/quiz/create`, `/delete`, `/change`, `/search` |
| Lobby | `/api/lobby/create`, `/search`, `/join/<token>`, `/exit`, `/run`, `/get-info`, `/poll-running/<token>`, `/compare` |

Авторизация — заголовок `Authorization: Bearer <token>`.

## Тесты

```bash
cd server
python -m unittest discover -s tests -v
```

Тестам нужна доступная PostgreSQL с применённой схемой.

## Ограничения

- Нет клиентской части, хотя ранняя версия README упоминала Vue-клиент.
- Нет миграций: схема применяется вручную.
- Состояние лобби не переживает перезапуск и не разделяется между воркерами.

## Лицензия

MIT.
