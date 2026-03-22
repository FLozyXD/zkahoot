
# Table of Contents

1.  [API](#org7f0e097)
    1.  [Авторизация](#orgc96a197)
    2.  [Endpoints](#orgbda4c05)
        1.  [lobby](#org65d1de7)
        2.  [auth](#org52d8d93)


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

В этом разлеле необходима авторизация пользователя.

-   `/api/lobby/search`
    -   Методы: `GET`
    -   Принимает:
        -   q - параметр ссылки. Строка, которая является частью названия квиза, что сейчас в лобби.
    -   Выдает:
        
            [
              {
                "{lobby scheme}"
              },
              {
                "{lobby scheme}"
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
              "{lobby scheme}"
            }

-   `/api/lobby/poll-running/<token>`
    -   Методы: `GET`
    -   Принимает:
        -   <token> - это токен/идентификатор лобби
    -   Комментарий: вернет пустой ответ с кодом 200, когда запуск все же состоится.

-   `/api/lobby/compare`
    -   Методы: `POST`
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
    -   Выдает:
        
            "200"
            {
              "status": "OK"
            }
            
            "403"
            {
              "status": "Forbidden",
              "cause": "User with login {login} already exists."
            }

-   `/api/auth/get-token`, `/api/auth/make-token`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "login": "{login}",
              "password": "{password}"
            }
    -   Комментарий: `/api/auth/make-token` указывает на то же самое место, что и get-token. Последний оставил ради совместимости.
    -   Выдает:
        
            "200"
            {
              "status": "OK",
              "token": "{token}"
            }
            
            "403"
            {
              "status": "Forbidden",
              "cause": "Invalid credentials."
            }
            
            "403"
            {
              "status": "Forbidden",
              "cause": "User with login {login} does not exist."
            }

-   `/api/auth/revoke-token`
    -   Методы: `POST`
    -   Принимает:
        
            {
              "login": "{login}",
              "password": "{password}"
            }
    -   Выдает:
        
            "200"
            {
              "status": "OK",
            }
            
            "403"
            {
              "status": "Forbidden",
              "cause": "Invalid credentials."
            }
            
            "403"
            {
              "status": "Forbidden",
              "cause": "User with login {login} does not exist."
            }

