
import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "tasks.db"

SECRET_KEY = os.environ.get(
    "TASK_TRACKER_SECRET",
    "change-this-development-secret-before-deployment"
)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(150) NOT NULL,
                description VARCHAR(300) DEFAULT '',
                priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
                is_completed BOOLEAN NOT NULL DEFAULT 0,
                created_by VARCHAR(100) NOT NULL,
                created_at DATETIME NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Personal Task Tracker", lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    same_site="lax",
    https_only=False,  
    max_age=60 * 60 * 24
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

PRIORITIES = {"High", "Medium", "Low"}


def current_user(request: Request):
    return request.session.get("user")


def get_owned_task(task_id: int, username: str):
    with get_db() as conn:
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND created_by = ?",
            (task_id, username)
        ).fetchone()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


def validate_task(title, description, priority):
    title = title.strip()
    description = description.strip()

    if not title or len(title) > 150:
        raise HTTPException(
            status_code=400,
            detail="Title must contain 1 to 150 characters."
        )

    if len(description) > 300:
        raise HTTPException(
            status_code=400,
            detail="Description cannot exceed 300 characters."
        )

    if priority not in PRIORITIES:
        raise HTTPException(status_code=400, detail="Invalid priority")

    return title, description


@app.get("/login", name="login_page")
def login_page(request: Request):
    if current_user(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"theme": request.cookies.get("theme", "light")}
    )


@app.post("/login")
def login(request: Request, username: str = Form(...)):
    username = username.strip()

    if not username or len(username) > 100:
        raise HTTPException(
            status_code=400,
            detail="Enter a name of 1 to 100 characters."
        )

    request.session.clear()
    request.session["user"] = username

    return RedirectResponse("/", status_code=303)


@app.get("/")
def home(request: Request):
    username = current_user(request)

    if not username:
        return RedirectResponse("/login", status_code=303)

    with get_db() as conn:
        pending = conn.execute("""
            SELECT * FROM tasks
            WHERE created_by = ? AND is_completed = 0
            ORDER BY created_at DESC, id DESC
        """, (username,)).fetchall()

        completed = conn.execute("""
            SELECT * FROM tasks
            WHERE created_by = ? AND is_completed = 1
            ORDER BY created_at DESC, id DESC
        """, (username,)).fetchall()

    theme = request.cookies.get("theme", "light")
    if theme not in {"light", "dark"}:
        theme = "light"

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "username": username,
            "pending_tasks": pending,
            "completed_tasks": completed,
            "theme": theme
        }
    )


@app.post("/add")
def add_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium")
):
    username = current_user(request)

    if not username:
        return RedirectResponse("/login", status_code=303)

    title, description = validate_task(title, description, priority)

    with get_db() as conn:
        conn.execute("""
            INSERT INTO tasks
                (title, description, priority, is_completed,
                 created_by, created_at)
            VALUES (?, ?, ?, 0, ?, ?)
        """, (
            title,
            description,
            priority,
            username,
            datetime.now().isoformat(timespec="seconds")
        ))

    return RedirectResponse("/", status_code=303)


@app.get("/toggle/{task_id}")
def toggle_task(request: Request, task_id: int):
    username = current_user(request)

    if not username:
        return RedirectResponse("/login", status_code=303)

    with get_db() as conn:
        task = conn.execute("""
            SELECT is_completed FROM tasks
            WHERE id = ? AND created_by = ?
        """, (task_id, username)).fetchone()

        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        conn.execute("""
            UPDATE tasks
            SET is_completed = ?
            WHERE id = ? AND created_by = ?
        """, (1 - task["is_completed"], task_id, username))

    return RedirectResponse("/", status_code=303)


@app.get("/edit/{task_id}")
def edit_page(request: Request, task_id: int):
    username = current_user(request)

    if not username:
        return RedirectResponse("/login", status_code=303)

    task = get_owned_task(task_id, username)
    theme = request.cookies.get("theme", "light")

    if theme not in {"light", "dark"}:
        theme = "light"

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={"task": task, "theme": theme}
    )


@app.post("/update/{task_id}")
def update_task(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium")
):
    username = current_user(request)

    if not username:
        return RedirectResponse("/login", status_code=303)

    title, description = validate_task(title, description, priority)

    get_owned_task(task_id, username)

    with get_db() as conn:
        conn.execute("""
            UPDATE tasks
            SET title = ?, description = ?, priority = ?
            WHERE id = ? AND created_by = ?
        """, (title, description, priority, task_id, username))

    return RedirectResponse("/", status_code=303)


@app.post("/delete/{task_id}")
def delete_task(request: Request, task_id: int):
    username = current_user(request)

    if not username:
        return RedirectResponse("/login", status_code=303)

    get_owned_task(task_id, username)

    with get_db() as conn:
        conn.execute("""
            DELETE FROM tasks
            WHERE id = ? AND created_by = ?
        """, (task_id, username))

    return RedirectResponse("/", status_code=303)


@app.get("/set-theme/{theme}")
def set_theme(request: Request, theme: str):
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)

    if theme not in {"light", "dark"}:
        raise HTTPException(status_code=400, detail="Invalid theme")

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key="theme",
        value=theme,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        samesite="lax",
        secure=False  
    )
    return response


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
