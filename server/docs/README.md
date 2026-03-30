# Table of Contents

1.  [API](#org7f0e097)
    1.  [Авторизация](#orgc96a197)
    2.  [Endpoints](#orgbda4c05)
        1.  [lobby](#org65d1de7)
        2.  [auth](#org52d8d93)
        3.  [quiz](#org1234abc)


<a id="org7f0e097"></a>

# API

Ниже приведена документация endpoint'ов, их методов.


<a id="orgc96a197"></a>

## Авторизация

Авторизация производится с помощью токена, который генерируется с помощью endpoint'а `/api/auth/get-token`. Токен помещается в заголовок `Authorization` и проверяется во всех endpoint'ах, где нужна авторизация. По нему же и производится идентификация пользователя на backend'е.


<a id="orgbda4c05"></a>

## Endpoints


<a id="org65d1de7"></a>

### lobby

В этом разделе необходима авторизация пользователя.

-   `/api/lobby/search`
    -   Методы: `GET`
    -   Принимает:
        -   query - параметр ссылки. Строка, которая является частью названия квиза, что сейчас в лобби.
    -   Выдает:
        
            [
              {
				"token": "a1b2c3d4e5f6...",
				"name": "Моё Лобби",
				"owner_id": 123,
				"users": [
				  "user_001",
				  "user_002",
				  "admin_user"
				],
				"quiz": {
				  "id": 456,
				  "quiz_name": "Тест №1",
				  "creator_id": 789,
				  "questions": [
					{
					  "id": null,
					  "question": "Как работает JSON?",
					  "quiz_id": 0,
					  "answer": {
						"id": null,
						"answer": "..."
					  },
					  "type_dependent": ""
					}
				  ],
				  "type_dependent": "",
				  "question_type": "text"
				}
              },
              {
				"token": "a1b2c3d4e5f6...",
				"name": "Моё Лобби",
				"owner_id": 123,
				"users": [
				  "user_001",
				  "user_002",
				  "admin_user"
				],
				"quiz": {
				  "id": 456,
				  "quiz_name": "Тест №1",
				  "creator_id": 789,
				  "questions": [
					{
					  "id": null,
					  "question": "Как работает JSON?",
					  "quiz_id": 0,
					  "answer": {
						"id": null,
						"answer": "..."
					  },
					  "type_dependent": ""
					}
				  ],
				  "type_dependent": "",
				  "question_type": "text"
				}
              }
            ]

-   `/api/lobby/create`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "name": "{lobby name}",
              "quiz_id": {integer}
            }
    -   Выдает:
        
            {
              "token": "{token}"
            }

-   `/api/lobby/join/<token>`
    -   Методы: `POST`
    -   Принимает:
        -   <token> - это токен/идентификатор лобби

-   `/api/lobby/exit`
    -   Методы: `POST`

-   `/api/lobby/run`
    -   Методы: `POST`
    -   Комментарий: это метод, который запускает игру. Запустить игру может ЛИШЬ ТОЛЬКО обладатель лобби.

-   `/api/lobby/get-info`
    -   Методы: `GET`
    -   Выдает:
        
			{
			  "token": "a1b2c3d4e5f6...",
			  "name": "Моё Лобби",
			  "owner_id": 123,
			  "users": [
				"user_001",
				"user_002",
				"admin_user"
			  ],
			  "quiz": {
				"id": 456,
				"quiz_name": "Тест №1",
				"creator_id": 789,
				"questions": [
				  {
					"id": null,
					"question": "Как работает JSON?",
					"quiz_id": 0,
					"answer": {
					  "id": null,
					  "answer": "..."
					},
					"type_dependent": ""
				  }
				],
				"type_dependent": "",
				"question_type": "text"
			  }
			}

-   `/api/lobby/poll-running/<token>`
    -   Методы: `GET`
    -   Принимает:
        -   <token> - это токен/идентификатор лобби
    -   Комментарий: вернет пустой ответ с кодом 200, когда запуск все же состоится.

-   `/api/lobby/compare`
    -   Методы: `PUT`
    -   Принимает:
        
            {
              "answers": [
                "answer1",
                "answer2",
                "answer3",
                ...
              ]
            }
    -   Выдает:
        
            [
              true,
              false,
              ...
            ]
    -   Комментарий: это метод сверки ответов. Пользователь и квиз после запуска лобби уже связаны.


<a id="org52d8d93"></a>

### auth

-   `/api/auth/register`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "login": "{login}",
              "password": "{password}"
            }
    -   Коды: 200, 403, 418

-   `/api/auth/change-login`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "login": "{login}",
              "password": "{password}",
              "new_login": "{new_login}"
            }
    -   Коды: 200, 403, 404

-   `/api/auth/change-password`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "login": "{login}",
              "password": "{password}",
              "new_password": "{new_password}"
            }
    -   Коды: 200, 403, 404

-   `/api/auth/get-token`, `/api/auth/make-token`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "login": "{login}",
              "password": "{password}"
            }
    -   Комментарий: `/api/auth/make-token` указывает на то же самое место, что и get-token. Последний оставил ради совместимости.
    -   Выдает:
        
            {
              "token": "{token}"
            }
    -   Коды: 200, 403, 404

-   `/api/auth/revoke-token`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "login": "{login}",
              "password": "{password}"
            }
    -   Коды: 200, 403, 404

<a id="org1234abc"></a>

### quiz

В этом разделе необходима авторизация пользователя.

-   `/api/quiz/create`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "name": "{quiz name}",
              "questions": [
                {
                  "text": "{question text}",
                  "answer": "{correct answer}"
                },
                ...
              ]
            }
    -   Выдает:
        
            {
              "id": {integer},
              "name": "{quiz name}",
              "creator_id": {integer},
              "questions": [
                {
                  "id": {integer},
                  "text": "{question text}",
                  "answer": {
                    "id": {integer},
                    "text": "{correct answer}"
                  }
                },
                ...
              ]
            }
    -   Комментарий: создает новый квиз. `creator_id` подставляется автоматически из токена авторизации.

-   `/api/quiz/delete`
    -   Методы: `DELETE`
    -   Принимает:
        
            {
              "quiz_id": {integer}
            }
    -   Коды: 200, 403
    -   Комментарий: удаляет квиз и все связанные с ним вопросы и ответы.

-   `/api/quiz/change`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "id": {integer},
              "name": "{new quiz name}",
              "questions": [
                {
                  "text": "{new question text}",
                  "answer": "{new correct answer}"
                },
                ...
              ]
            }
    -   Коды: 200, 403
    -   Комментарий: полностью заменяет существующий квиз новым содержимым. Старые вопросы и ответы удаляются, создаются новые.

-   `/api/quiz/search`
    -   Методы: `GET`
    -   Принимает:
        -   query - параметр ссылки. Строка, которая является частью названия квиза.
        -   creator_id - параметр ссылки (опционально). Целое число, идентификатор создателя.
    -   Выдает:
        
            [
              {
                "id": {integer},
                "name": "{quiz name}",
                "creator_id": {integer},
                "questions": [
                  {
                    "id": {integer},
                    "text": "{question text}",
                    "answer": {
                      "id": {integer},
                      "text": "{correct answer}"
                    }
                  },
                  ...
                ]
              },
              ...
            ]
    -   Комментарий: поиск квизов по названию (частичное совпадение) и/или по идентификатору создателя. Если параметры не указаны, возвращает ошибку 400.
