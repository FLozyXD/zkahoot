class AuthError(Exception):
    message = "Authentification error!"

    def __init__(self) -> None:
        super().__init__(self.message)


class LoginError(AuthError):
    message = "Invalid credentials!"
