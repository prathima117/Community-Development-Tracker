import os
import re
import secrets
from functools import wraps

import click
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from database import (
    initialize_database, get_projects, get_summary, add_project, get_project,
    delete_project, get_user_by_email, create_user,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_email" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_email" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)
        if user is None or len(password) > 128 or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
        else:
            session.clear()
            session["user_email"] = user["email"]
            return redirect(url_for("index"))
    return render_template("auth.html")


@app.cli.command("create-user")
@click.argument("email")
def create_user_command(email):
    """Create an account that can access the private tracker."""
    email = email.strip().lower()
    if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise click.ClickException("Enter a valid email address.")

    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    if len(password) < 8 or len(password) > 128:
        raise click.ClickException("Password must be between 8 and 128 characters.")

    initialize_database()
    if not create_user(email, generate_password_hash(password)):
        raise click.ClickException(f"An account for {email} already exists.")
    click.echo(f"Account created for {email}.")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "All categories")
    projects = get_projects(search, category)
    summary = get_summary()
    return render_template("index.html", projects=projects, summary=summary,
                           search=search, selected_category=category,
                           categories=["Education", "Water & Sanitation", "Healthcare",
                                       "Environment", "Livelihoods", "Housing", "Other"])

@app.route("/projects/add", methods=["POST"])
@login_required
def add():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    location = request.form.get("location", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", "Planning").strip()
    try:
        progress = int(request.form.get("progress", "0"))
        budget = float(request.form.get("budget", "0"))
        raised = float(request.form.get("raised", "0"))
        if not 0 <= progress <= 100 or budget < 0 or raised < 0:
            raise ValueError
    except ValueError:
        flash("Enter valid numbers. Progress must be 0–100 and amounts cannot be negative.", "error")
        return redirect(url_for("index") + "#add-project")
    if not name or not category or not location or not description:
        flash("Please fill in all required project fields.", "error")
        return redirect(url_for("index") + "#add-project")
    add_project((name, category, location, description, progress, budget, raised, status))
    flash(f'Project “{name}” was added successfully.', "success")
    return redirect(url_for("index"))

@app.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    project = get_project(project_id)
    if project is None:
        flash("Project not found.", "error")
        return redirect(url_for("index"))
    return render_template("project.html", project=project)

@app.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete(project_id):
    delete_project(project_id)
    flash("Project deleted.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
