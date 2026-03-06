class AuthError(Exception):
    message = "Authentification error!"

    def __init__(self):
        super().__init__(self, message=self.message)


class UserExistsError(AuthError):
    message = "User {login} already exists!"

    def __init__(self, login: str) -> None:
        self.login = login
        self.message = self.message.format(login=self.login)
        super().__init__(self)


class UserNotExistsError(AuthError):
    message = "User {login} does not exist!"

    def __init__(self, login: str) -> None:
        self.login = login
        self.message = self.message.format(login=self.login)
        super().__init__(self)
