from .blueprints import auth

from flask import Flask, Blueprint
from pathlib import Path
import tomllib


def create_app(
    config_path: Path = Path("config.toml"), blueprints=[auth]
) -> Flask:
    with open(config_path, "rb") as file:
        config = tomllib.load(file)

    app = Flask(__name__)
    app.config.from_mapping(**config["general"]["flask_config"])

    api = Blueprint("api", __name__, "/api")

    for bp in blueprints:
        api.register_blueprint(bp)

    app.register_blueprint(api)

    return app
