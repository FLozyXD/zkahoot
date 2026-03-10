import api


def main() -> None:
    app = api.create_app()
    app.run()


if __name__ == "__main__":
    main()
