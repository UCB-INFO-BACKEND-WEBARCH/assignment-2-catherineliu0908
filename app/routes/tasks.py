from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app import db, task_queue
from app.models import Task
from app.schemas import TaskCreateSchema, TaskUpdateSchema
from app.jobs import send_due_soon_notification

tasks_bp = Blueprint("tasks", __name__)

task_create_schema = TaskCreateSchema()
task_update_schema = TaskUpdateSchema()


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    completed = request.args.get("completed")
    query = Task.query

    if completed is not None:
        if completed.lower() == "true":
            query = query.filter_by(completed=True)
        elif completed.lower() == "false":
            query = query.filter_by(completed=False)

    tasks = query.all()
    return jsonify({"tasks": [task.to_dict() for task in tasks]}), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task.to_dict()), 200


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    try:
        data = task_create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    task = Task(
        title=data["title"],
        description=data.get("description"),
        due_date=data.get("due_date"),
        category_id=data.get("category_id"),
    )

    db.session.add(task)
    db.session.commit()

    notification_queued = False
    now = datetime.utcnow()

    if task.due_date and now < task.due_date <= now + timedelta(hours=24):
        task_queue.enqueue(send_due_soon_notification, task.title)
        notification_queued = True

    return jsonify({
        "task": task.to_dict(),
        "notification_queued": notification_queued
    }), 201


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    try:
        data = task_update_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for key, value in data.items():
        setattr(task, key, value)

    db.session.commit()
    return jsonify({"task": task.to_dict()}), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200