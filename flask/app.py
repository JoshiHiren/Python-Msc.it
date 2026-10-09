from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Todo Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)


# Home - Show all tasks
@app.route("/")
def root():

    todos = Todo.query.all()

    return render_template(
        "index.html",
        todos=todos
    )


# Add Task
@app.route("/add", methods=["POST"])
def add_todo():

    task_name = request.form.get("task_name")
    task_date = request.form.get("task_date")
    task_status = request.form.get("task_status")

    if not task_name or not task_date or not task_status:
        return "All fields are required!"

    due_date = datetime.strptime(
        task_date,
        "%Y-%m-%d"
    ).date()

    todo = Todo(
        name=task_name,
        status=task_status,
        due_date=due_date
    )

    db.session.add(todo)
    db.session.commit()

    return redirect("/")


# Edit Task
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_todo(id):

    todo = Todo.query.get_or_404(id)

    if request.method == "POST":

        todo.name = request.form.get("task_name")
        todo.status = request.form.get("task_status")

        task_date = request.form.get("task_date")

        todo.due_date = datetime.strptime(
            task_date,
            "%Y-%m-%d"
        ).date()

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit.html",
        todo=todo
    )


# Delete Task
@app.route("/delete/<int:id>")
def delete_todo(id):

    todo = Todo.query.get_or_404(id)

    db.session.delete(todo)
    db.session.commit()

    return redirect("/")


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        port=5001,
        debug=True
    )