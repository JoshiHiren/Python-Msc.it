
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Task database model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300))
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    due_date = db.Column(db.Date, nullable=True)


# Home page: show pending and completed tasks
@app.route("/")
def index():
    pending_tasks = Task.query.filter_by(
        is_completed=False
    ).order_by(Task.due_date.asc()).all()

    completed_tasks = Task.query.filter_by(
        is_completed=True
    ).order_by(Task.id.desc()).all()

    return render_template(
        "index.html",
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


# Add a new task
@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")
    due_date_str = request.form.get("due_date", "").strip()

    if not title or len(title) > 150:
        return "Title is required and must be at most 150 characters.", 400

    if len(description) > 300:
        return "Description must be at most 300 characters.", 400

    if priority not in ["High", "Medium", "Low"]:
        return "Invalid priority.", 400

    try:
        due_date = (
            datetime.strptime(due_date_str, "%Y-%m-%d").date()
            if due_date_str else None
        )
    except ValueError:
        return "Invalid due date.", 400

    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date
    )

    db.session.add(task)
    db.session.commit()

    return redirect(url_for("index"))


# Toggle pending/completed status
@app.route("/toggle/<int:id>")
def toggle(id):
    task = db.get_or_404(Task, id)
    task.is_completed = not task.is_completed

    db.session.commit()
    return redirect(url_for("index"))


# Display the edit form
@app.route("/edit/<int:id>")
def edit(id):
    task = db.get_or_404(Task, id)
    return render_template("edit.html", task=task)


# Update an existing task
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    task = db.get_or_404(Task, id)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "")
    due_date_str = request.form.get("due_date", "").strip()

    if not title or len(title) > 150:
        return "Title is required and must be at most 150 characters.", 400

    if len(description) > 300:
        return "Description must be at most 300 characters.", 400

    if priority not in ["High", "Medium", "Low"]:
        return "Invalid priority.", 400

    try:
        due_date = (
            datetime.strptime(due_date_str, "%Y-%m-%d").date()
            if due_date_str else None
        )
    except ValueError:
        return "Invalid due date.", 400

    task.title = title
    task.description = description
    task.priority = priority
    task.due_date = due_date

    db.session.commit()
    return redirect(url_for("index"))


# Delete a task
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    task = db.get_or_404(Task, id)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for("index"))


# Create the database and start the application
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)