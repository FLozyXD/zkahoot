class AuthError(Exception):
    message = "Authentification error!"

    def __init__(self) -> None:
        super().__init__(self.message)


class UserExistsError(Exception):
    message = "User {login} already exists!"

    def __init__(self, login: str) -> None:
        super().__init__(self.message.format(login=login))


class UserNotExistsError(Exception):
    message = "User {login} does not exist!"

    def __init__(self, login: str) -> None:
        super().__init__(self.message.format(login=login))


class LoginError(AuthError):
    message = "Invalid credentials!"
