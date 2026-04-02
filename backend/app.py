"""Flask application entrypoint."""

from __future__ import annotations

from flask import Flask, jsonify

from backend.api.chat import chat_bp
from backend.config import settings


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["ENV"] = settings.flask_env
    app.config["DEBUG"] = settings.flask_debug

    @app.get("/health")
    def healthcheck():
        return jsonify(
            {
                "status": "ok",
                "service": "julius-caesAIr-backend",
                "index_path": str(settings.vector_index_dir),
            }
        )

    app.register_blueprint(chat_bp, url_prefix="/api")
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=settings.flask_host, port=settings.flask_port)
