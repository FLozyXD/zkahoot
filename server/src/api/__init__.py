from .auth import auth_bp
from .lobby import lobby_bp
from .quiz import quiz_bp

from flask import Flask, Blueprint
from pathlib import Path
import tomllib


def create_app(
    config_path: Path = Path("config.toml"), blueprints=[auth_bp]
) -> Flask:
    with open(config_path, "rb") as file:
        config = tomllib.load(file)

    app = Flask(__name__)
    app.config.from_mapping(**config["general"]["flask_config"])

    api_bp = Blueprint("api", __name__, url_prefix="/api")

    for bp in blueprints:
        api_bp.register_blueprint(bp)

    app.register_blueprint(api_bp)

    return app
