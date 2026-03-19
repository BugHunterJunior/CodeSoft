from flask import Blueprint, jsonify, request, session
from models import get_tasks, get_task, create_task, update_task, delete_task, toggle_complete
from helpers import login_required, validate_task_form

api = Blueprint("api", __name__, url_prefix="/api")


def task_to_dict(task):
    return {
        "id":          task["id"],
        "title":       task["title"],
        "description": task["description"],
        "priority":    task["priority"],
        "due_date":    task["due_date"],
        "is_complete": bool(task["is_complete"]),
        "created_at":  task["created_at"],
    }


@api.route("/tasks", methods=["GET"])
@login_required
def list_tasks():
    filter_by = request.args.get("filter")
    sort_by   = request.args.get("sort", "created_at")
    search    = request.args.get("search")
    task_list = get_tasks(session["user_id"], filter_by=filter_by, sort_by=sort_by, search=search)
    return jsonify([task_to_dict(t) for t in task_list])


@api.route("/tasks", methods=["POST"])
@login_required
def create_task_api():
    data  = request.get_json(force=True) or {}
    valid, errors = validate_task_form(data)
    if not valid:
        return jsonify({"errors": errors}), 400

    create_task(
        user_id     = session["user_id"],
        title       = data["title"].strip(),
        description = data.get("description", "").strip(),
        priority    = data.get("priority", "medium"),
        due_date    = data.get("due_date") or None,
    )
    return jsonify({"message": "Task created."}), 201


@api.route("/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task_api(task_id):
    task = get_task(task_id, session["user_id"])
    if not task:
        return jsonify({"error": "Not found."}), 404
    return jsonify(task_to_dict(task))


@api.route("/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task_api(task_id):
    task = get_task(task_id, session["user_id"])
    if not task:
        return jsonify({"error": "Not found."}), 404

    data  = request.get_json(force=True) or {}
    valid, errors = validate_task_form(data)
    if not valid:
        return jsonify({"errors": errors}), 400

    update_task(
        task_id     = task_id,
        user_id     = session["user_id"],
        title       = data["title"].strip(),
        description = data.get("description", "").strip(),
        priority    = data.get("priority", "medium"),
        due_date    = data.get("due_date") or None,
    )
    return jsonify({"message": "Task updated."})


@api.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task_api(task_id):
    task = get_task(task_id, session["user_id"])
    if not task:
        return jsonify({"error": "Not found."}), 404
    delete_task(task_id, session["user_id"])
    return jsonify({"message": "Task deleted."})


@api.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task_api(task_id):
    task = get_task(task_id, session["user_id"])
    if not task:
        return jsonify({"error": "Not found."}), 404
    toggle_complete(task_id, session["user_id"])
    updated = get_task(task_id, session["user_id"])
    return jsonify({"is_complete": bool(updated["is_complete"])})
