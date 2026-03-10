from api.auth import auth

from flask import Flask
from pathlib import Path
import tomllib


def create_app(
    config_path: Path = Path("config.toml"), blueprints=[auth]
) -> Flask:
    with open(config_path, "rb") as file:
        config = tomllib.load(file)

    app = Flask(__name__)
    app.config.from_mapping(**config["general"]["flask_config"])

    for bp in blueprints:
        app.register_blueprint(bp)

    return app
