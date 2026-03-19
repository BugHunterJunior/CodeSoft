from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash,
)
from models import create_user, get_user_by_email, get_user_by_username
from helpers import hash_password, verify_password, validate_register_form

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("tasks.dashboard"))

    if request.method == "POST":
        valid, errors = validate_register_form(request.form)
        if not valid:
            for err in errors:
                flash(err, "error")
            return render_template("register.html", form=request.form)

        username = request.form["username"].strip()
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

        if get_user_by_email(email):
            flash("An account with that email already exists.", "error")
            return render_template("register.html", form=request.form)

        if get_user_by_username(username):
            flash("That username is already taken.", "error")
            return render_template("register.html", form=request.form)

        create_user(username, email, hash_password(password))
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form={})


@auth.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("tasks.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_user_by_email(email)
        if not user or not verify_password(password, user["password_hash"]):
            flash("Incorrect email or password.", "error")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"]  = user["id"]
        session["username"] = user["username"]
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for("tasks.dashboard"))

    return render_template("login.html", email="")


@auth.route("/logout")
def logout():
    username = session.get("username", "")
    session.clear()
    flash(f"Goodbye, {username}. See you soon!", "info")
    return redirect(url_for("auth.login"))
