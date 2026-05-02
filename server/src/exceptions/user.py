class UserError(Exception):
    message = 'A problem with user "{login}" occured!'

    def __init__(self, login: str) -> None:
        self.login = login
        super().__init__(self.message.format(login=self.login))


class UserExistsError(UserError):
    message = 'User "{login}" already exists!'


class UserNotExistsError(UserError):
    message = 'User "{login}" does not exist!'
