from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import func

from app import db
from app.models import Category, Task
from app.schemas import CategoryCreateSchema

categories_bp = Blueprint("categories", __name__)
category_create_schema = CategoryCreateSchema()


@categories_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()

    result = []
    for category in categories:
        result.append({
            "id": category.id,
            "name": category.name,
            "color": category.color,
            "task_count": len(category.tasks)
        })

    return jsonify({"categories": result}), 200


@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify({
        "id": category.id,
        "name": category.name,
        "color": category.color,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "completed": task.completed
            }
            for task in category.tasks
        ]
    }), 200


@categories_bp.route("/categories", methods=["POST"])
def create_category():
    try:
        data = category_create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    existing = Category.query.filter_by(name=data["name"]).first()
    if existing:
        return jsonify({"errors": {"name": ["Category with this name already exists."]}}), 400

    category = Category(
        name=data["name"],
        color=data.get("color")
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        "category": {
            "id": category.id,
            "name": category.name,
            "color": category.color
        }
    }), 201


@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    if len(category.tasks) > 0:
        return jsonify({
            "error": "Cannot delete category with existing tasks. Move or delete tasks first."
        }), 400

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 200