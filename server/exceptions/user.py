class UserError(Exception):
    message = 'A problem with user "{login}" occured!'

    def __init__(self, login: str) -> None:
        super().__init__(self.message.format(login=login))


class UserExistsError(UserError):
    message = 'User "{login}" already exists!'


class UserNotExistsError(UserError):
    message = 'User "{login}" does not exist!'
