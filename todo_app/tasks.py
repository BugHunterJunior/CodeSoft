from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, jsonify,
)
from models import (
    create_task, get_tasks, get_task,
    update_task, delete_task, toggle_complete,
)
from helpers import login_required, validate_task_form

tasks = Blueprint("tasks", __name__)


@tasks.route("/")
@login_required
def dashboard():
    user_id   = session["user_id"]
    filter_by = request.args.get("filter", "all")
    sort_by   = request.args.get("sort", "created_at")
    search    = request.args.get("search", "").strip()

    task_list = get_tasks(
        user_id,
        filter_by=None if filter_by == "all" else filter_by,
        sort_by=sort_by,
        search=search or None,
    )

    return render_template(
        "dashboard.html",
        tasks=task_list,
        filter_by=filter_by,
        sort_by=sort_by,
        search=search,
    )


@tasks.route("/add", methods=["POST"])
@login_required
def add():
    valid, errors = validate_task_form(request.form)
    if not valid:
        for err in errors:
            flash(err, "error")
        return redirect(url_for("tasks.dashboard"))

    create_task(
        user_id     = session["user_id"],
        title       = request.form["title"].strip(),
        description = request.form.get("description", "").strip(),
        priority    = request.form.get("priority", "medium"),
        due_date    = request.form.get("due_date") or None,
    )
    flash("Task added!", "success")
    return redirect(url_for("tasks.dashboard"))


@tasks.route("/update/<int:task_id>", methods=["GET", "POST"])
@login_required
def update(task_id):
    user_id = session["user_id"]
    task    = get_task(task_id, user_id)

    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.dashboard"))

    if request.method == "POST":
        valid, errors = validate_task_form(request.form)
        if not valid:
            for err in errors:
                flash(err, "error")
            return render_template("edit_task.html", task=task)

        update_task(
            task_id     = task_id,
            user_id     = user_id,
            title       = request.form["title"].strip(),
            description = request.form.get("description", "").strip(),
            priority    = request.form.get("priority", "medium"),
            due_date    = request.form.get("due_date") or None,
        )
        flash("Task updated!", "success")
        return redirect(url_for("tasks.dashboard"))

    return render_template("edit_task.html", task=task)


@tasks.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete(task_id):
    delete_task(task_id, session["user_id"])
    flash("Task deleted.", "info")
    return redirect(url_for("tasks.dashboard"))


@tasks.route("/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle(task_id):
    toggle_complete(task_id, session["user_id"])
    # Support both AJAX and normal form submission
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        task = get_task(task_id, session["user_id"])
        return jsonify({"is_complete": task["is_complete"]})
    return redirect(url_for("tasks.dashboard"))
