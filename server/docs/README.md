# zkahoot API

HTTP API сервера zkahoot: аутентификация, квизы и игровые лобби.
Базовый префикс — `/api`. Формат данных — JSON.

## Аутентификация

Токен передаётся в заголовке:

```http
Authorization: Bearer <token>
```

Токены и состояние лобби хранятся в памяти процесса. После перезапуска сервера
выданные токены и активные лобби исчезают.

### `POST /api/auth/register`

Регистрация пользователя.

```json
{"login": "alice", "password": "password123"}
```

Успех — `200` с пустым телом. Пароль должен быть не короче 8 символов.
Занятый логин — `418`.

### `POST /api/auth/get-token`

Вход и выдача токена. То же тело, что у регистрации.

```json
{"token": "...", "user_id": 1, "login": "alice"}
```

### `POST /api/auth/make-token`

Синоним `/get-token` с тем же контрактом.

### `POST /api/auth/revoke-token`

Отзыв токена. Тело: `{"login": "...", "password": "..."}`.
Успех — `200` с пустым телом.

### `GET /api/auth/me`

Требует `Authorization`. Возвращает:

```json
{"user_id": 1, "login": "alice"}
```

### `POST /api/auth/change-login`

```json
{"login": "alice", "password": "password123", "new_login": "alice2"}
```

Успех — `200` с пустым телом.

### `POST /api/auth/change-password`

```json
{"login": "alice", "password": "password123", "new_password": "newpassword123"}
```

Успех — `200` с пустым телом.

## Квизы

Все методы требуют Bearer-токен. Владелец квиза определяется по токену.

### `POST /api/quiz/register`

Создание квиза.

```json
{
  "name": "Мой квиз",
  "questions": [
    {"text": "Столица Франции?", "answer": "Париж"},
    {"text": "2 + 2?", "answer": "4"}
  ]
}
```

Успех — `200` с пустым телом. `name` и `questions` обязательны; список
вопросов может быть пустым. Ошибки валидации — `400`.

### `DELETE /api/quiz/delete`

Удаление своего квиза.

```json
{"quiz_id": 1}
```

Успех — `200` с пустым телом. Чужой квиз — `403`, отсутствующий — `404`.

### `POST /api/quiz/change`

Изменение названия и/или вопросов своего квиза.

```json
{
  "quiz_id": 1,
  "quiz_name": "Новое название",
  "questions": [
    {
      "id": 10,
      "quiz_id": 1,
      "question": "Столица Франции?",
      "answer": {"id": 5, "answer": "Париж"},
      "type_dependent": null
    }
  ]
}
```

Успех — `200` с пустым телом.

### `GET /api/quiz/search?query=&creator_id=`

Поиск по названию. `query` обязателен, но может быть пустым — тогда
возвращаются все квизы. `creator_id` необязателен.

```json
[
  {
    "id": 1,
    "quiz_name": "Мой квиз",
    "creator_id": 1,
    "questions": [
      {
        "id": 10,
        "question": "Столица Франции?",
        "quiz_id": 1,
        "answer": {"id": 5, "answer": "Париж"},
        "type_dependent": null,
        "question_type": "prompt"
      }
    ]
  }
]
```

## Лобби

Все методы требуют Bearer-токен.

### `POST /api/lobby/create`

```json
{"name": "Игра 1", "quiz_id": 1}
```

Ответ: `{"token": "<lobby-token>"}`.

### `POST /api/lobby/join/<lobby_token>`

Присоединение к лобби. Успех — `200` с пустым телом.

### `POST /api/lobby/exit`

Выход из текущего лобби. Успех — `200` с пустым телом.

### `POST /api/lobby/run`

Запуск лобби. Доступен только владельцу. После запуска новые участники
не подключаются.

### `GET /api/lobby/get-info`

Информация о текущем лобби:

```json
{
  "token": "<lobby-token>",
  "name": "Игра 1",
  "owner_id": 1,
  "users": ["alice", "bob"],
  "quiz": {"id": 1, "quiz_name": "Мой квиз", "questions": []},
  "scoreboard": []
}
```

Ответы на вопросы в объекте `quiz` не раскрываются.

### `GET /api/lobby/poll-running/<lobby_token>`

`200`, если лобби запущено; `202`, если ещё нет.

### `PUT /api/lobby/compare`

Проверка ответов текущего участника.

```json
{"answers": ["Париж", "4"]}
```

Ответ:

```json
{
  "results": [true, true],
  "scoreboard": [
    {"login": "alice", "correct": 2, "total": 2, "submitted": true}
  ]
}
```

Сравнение регистронезависимое, пробелы по краям отбрасываются.
Если лобби не запущено — `403`; неверное число ответов — `400`.

### `GET /api/lobby/scoreboard`

Таблица результатов текущего лобби. Сортировка: сначала сдавшие, затем по
числу правильных ответов.

```json
[
  {"login": "alice", "correct": 2, "total": 2, "submitted": true},
  {"login": "bob", "correct": 1, "total": 2, "submitted": true}
]
```

### `GET /api/lobby/search?query=`

Поиск лобби по названию. Возвращает список объектов в формате
`get-info`.

## Коды ошибок

| Код | Значение |
|---|---|
| `400` | неверное тело запроса или параметры |
| `401` | отсутствует или недействителен токен |
| `403` | действие запрещено (чужой квиз, запуск не владельцем, лобби не запущено) |
| `404` | квиз или лобби не найдены |
| `418` | логин уже занят |

## Запуск и тесты

Инструкции по запуску сервера, клиента и тестов — в
[корневом README проекта](../../README.md).
