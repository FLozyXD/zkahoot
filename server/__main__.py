from src import api
import tomllib


def main() -> None:
    with open("config.toml", "rb") as file:
        config = tomllib.load(file)
    app = api.create_app()
    app.run(port=config["general"]["port"])


if __name__ == "__main__":
    main()
