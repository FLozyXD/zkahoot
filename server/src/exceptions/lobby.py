class LobbyError(Exception):
    message = "A problem with lobby {token} occured!"

    def __init__(self, token: str) -> None:
        super().__init__(self.message.format(token=token))


class LobbyNotExistsError(LobbyError):
    msg = "Lobby with token {token} does not exist!"
