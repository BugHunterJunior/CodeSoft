from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_text):
    return generate_password_hash(plain_text)


def verify_password(plain_text, hashed):
    return check_password_hash(hashed, plain_text)


def login_required(f):
    """Decorator — redirects to /login if no active session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def validate_task_form(form):
    """
    Validate the add/edit task form.
    Returns (is_valid: bool, errors: list[str]).
    """
    errors = []
    title = form.get("title", "").strip()
    priority = form.get("priority", "medium")
    due_date = form.get("due_date", "").strip()

    if not title:
        errors.append("Task title is required.")
    if len(title) > 200:
        errors.append("Title must be 200 characters or fewer.")
    if priority not in ("low", "medium", "high"):
        errors.append("Invalid priority value.")
    if due_date:
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", due_date):
            errors.append("Due date must be in YYYY-MM-DD format.")

    return (len(errors) == 0), errors


def validate_register_form(form):
    """Basic server-side validation for registration."""
    errors = []
    username = form.get("username", "").strip()
    email    = form.get("email", "").strip()
    password = form.get("password", "")
    confirm  = form.get("confirm_password", "")

    if len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    if len(username) > 50:
        errors.append("Username must be 50 characters or fewer.")
    if "@" not in email or "." not in email:
        errors.append("Please enter a valid email address.")
    if len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")

    return (len(errors) == 0), errors
