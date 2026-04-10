import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
from rq import Queue

db = SQLAlchemy()
migrate = Migrate()
redis_conn = None
task_queue = None


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/taskdb"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["REDIS_URL"] = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    db.init_app(app)
    migrate.init_app(app, db)

    global redis_conn, task_queue
    redis_conn = Redis.from_url(app.config["REDIS_URL"])
    task_queue = Queue("default", connection=redis_conn)

    from app.routes.tasks import tasks_bp
    from app.routes.categories import categories_bp

    app.register_blueprint(tasks_bp)
    app.register_blueprint(categories_bp)

    @app.route("/")
    def home():
        return {"message": "Task Manager API is running"}

    return app