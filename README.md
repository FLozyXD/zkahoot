# zkahoot — платформа квизов

Kahoot-подобная платформа: Vue-клиент, REST API на Flask, PostgreSQL для
пользователей и квизов, лобби для игры в реальном времени.

Проект демонстрирует полный цикл «клиент → HTTP API → бизнес-логика → БД»:
аутентификацию по Bearer-токенам, CRUD квизов, лобби, подсчёт ответов и
таблицу результатов.

## Возможности

- Регистрация, смена логина и пароля.
- Выдача и отзыв Bearer-токенов.
- Создание, редактирование, удаление и поиск квизов.
- Вопросы с текстовым ответом; проверка ответов без учёта регистра.
- Создание лобби, присоединение по токену, выход, запуск игры.
- Опрос состояния лобби и сравнение ответов.
- Таблица результатов (`scoreboard`) с числом правильных ответов.
- Vue-клиент: вход, настройки пользователя, редактор квизов, игра и результаты.

## Стек

**Сервер**

- Python 3.11+
- Flask 3.1, blueprints, MethodView
- PostgreSQL, `psycopg2`, SQL без ORM
- Gunicorn + gevent
- `unittest`-тесты API

**Клиент**

- Vue 3, Vite, Pinia, Vue Router, Axios
- Node.js 20.19+ или 22.12+
- pnpm

## Структура

```text
client/                       Vue-приложение
  src/
    api/                      запросы к REST API
    views/                    экраны: вход, лобби, игра, результаты
    stores/                   Pinia-состояние
  package.json
  vite.config.js

server/
  __main__.py                 запуск dev-сервера
  example_config.toml         шаблон конфигурации
  requirements.txt
  src/
    schemas/
      main-schema.sql         пользователи, квизы, вопросы, ответы
      sessions-schema.sql     серверные сессии
      lobbies-schema.sql      SQLite-схема лобби
    api/
      __init__.py             create_app(), регистрация blueprints
      auth.py                 регистрация, токены, смена данных
      quiz.py                 CRUD квизов
      lobby.py                лобби, игра, результаты
    classes/                  Answer, Question, Quiz, User, Lobby
    utils/
      DBWrapper.py            обёртка psycopg2 и SQL-запросы
      Mgr.py                  менеджеры лобби
      UnifiedDict.py          двусторонний словарь для токенов
    exceptions/               доменные исключения
  tests/api/                  тесты auth, quiz и lobby
  docs/README.md              описание API
  docs/uml/                   PlantUML-диаграммы
```

Токены и состояние лобби по умолчанию хранятся в памяти процесса. Это
осознанное упрощение: для нескольких воркеров нужен Redis или другая общая
шина.

## Запуск сервера

1. Создайте базу и примените схемы:

```bash
createdb zkahoot
psql -d zkahoot -f server/src/schemas/main-schema.sql
psql -d zkahoot -f server/src/schemas/sessions-schema.sql
psql -d zkahoot -f server/src/schemas/lobbies-schema.sql
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

4. Запустите сервер:

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

## Запуск клиента

```bash
cd client
npm install -g pnpm   # если pnpm ещё не установлен
pnpm install
pnpm dev
```

Клиент ожидает запущенный сервер API. Адрес API задаётся в настройках клиента
(`client/src/api`).

## API

Полное описание с JSON-примерами — [`server/docs/README.md`](server/docs/README.md).

| Группа | Эндпоинты |
|---|---|
| Auth | `/api/auth/register`, `/make-token`, `/get-token`, `/revoke-token`, `/me`, `/change-login`, `/change-password` |
| Quiz | `/api/quiz/register`, `/delete`, `/change`, `/search` |
| Lobby | `/api/lobby/create`, `/search`, `/join/<token>`, `/exit`, `/run`, `/get-info`, `/poll-running/<token>`, `/compare`, `/scoreboard` |

Авторизация — заголовок `Authorization: Bearer <token>`.

`POST /api/quiz/register` принимает `{"name": "...", "questions": [{"text":
"...", "answer": "..."}]}`. `PUT /api/lobby/compare` возвращает
`{"results": [true, false], "scoreboard": [...]}`.

## Тесты

```bash
cd server
python -m unittest discover -s tests -v
```

Тестам нужна PostgreSQL с применённой схемой. DSN для тестов задаётся через
`ZKAHOOT_TEST_DSN`; по умолчанию используется
`postgresql://localhost/zkahoot-test`.

Проверено: 40 тестов, все проходят.

## Ограничения

- Нет миграций: схемы применяются вручную.
- Токены и лобби не переживают перезапуск и не разделяются между воркерами.
- Клиент не входит в автоматические тесты; проверяется вручную через Vite.
- Для production нужны HTTPS, внешнее хранилище сессий и нормальные миграции.

## Лицензия

MIT.
