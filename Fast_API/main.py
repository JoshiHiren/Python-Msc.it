
from datetime import datetime
from pathlib import Path
import os
import secrets

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'tasks.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)
Base = declarative_base()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get(
        "SESSION_SECRET_KEY", secrets.token_hex(32)
    ),
    same_site="lax",
    https_only=os.environ.get("COOKIE_SECURE", "false").lower() == "true"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(300), default="")
    priority = Column(String(20), default="Medium", nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

Base.metadata.create_all(bind=engine)

def get_current_user(request: Request):
    username = request.session.get("username")
    if not username:
        return None
    return username


def login_required(request: Request):
    username = get_current_user(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    return username


def get_owned_task(db, task_id: int, username: str):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.created_by == username)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/")
def home(request: Request):
    username = login_required(request)
    if isinstance(username, RedirectResponse):
        return username

    theme = request.cookies.get("theme", "light")
    if theme not in ("light", "dark"):
        theme = "light"

    db = SessionLocal()
    try:
        pending_tasks = (
            db.query(Task)
            .filter(
                Task.created_by == username,
                Task.is_completed.is_(False)
            )
            .order_by(Task.created_at.desc())
            .all()
        )

        completed_tasks = (
            db.query(Task)
            .filter(
                Task.created_by == username,
                Task.is_completed.is_(True)
            )
            .order_by(Task.created_at.desc())
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "username": username,
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks,
                "theme": theme,
            },
        )
    finally:
        db.close()

@app.get("/login")
def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"theme": request.cookies.get("theme", "light")},
    )

@app.post("/login")
def login(request: Request, username: str = Form(...)):
    username = username.strip()

    if not username or len(username) > 100:
        raise HTTPException(
            status_code=400,
            detail="Name must contain 1 to 100 characters"
        )

    request.session.clear()
    request.session["username"] = username

    return RedirectResponse("/", status_code=303)
    
@app.post("/add")
def add_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
):
    username = login_required(request)
    if isinstance(username, RedirectResponse):
        return username

    title = title.strip()
    description = description.strip()

    if not title or len(title) > 150:
        raise HTTPException(
            status_code=400,
            detail="Title must contain 1 to 150 characters"
        )

    if len(description) > 300:
        raise HTTPException(
            status_code=400,
            detail="Description cannot exceed 300 characters"
        )

    if priority not in ("High", "Medium", "Low"):
        raise HTTPException(status_code=400, detail="Invalid priority")

    db = SessionLocal()
    try:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            is_completed=False,
            created_by=username,
            created_at=datetime.now(),
        )
        db.add(task)
        db.commit()
        return RedirectResponse("/", status_code=303)
    finally:
        db.close()

@app.get("/toggle/{id}")
def toggle_task(request: Request, id: int):
    username = login_required(request)
    if isinstance(username, RedirectResponse):
        return username

    db = SessionLocal()
    try:
        task = get_owned_task(db, id, username)
        task.is_completed = not task.is_completed
        db.commit()
        return RedirectResponse("/", status_code=303)
    finally:
        db.close()

@app.get("/edit/{id}")
def edit_task_page(request: Request, id: int):
    username = login_required(request)
    if isinstance(username, RedirectResponse):
        return username

    db = SessionLocal()
    try:
        task = get_owned_task(db, id, username)
        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={"task": task, "username": username},
        )
    finally:
        db.close()

@app.post("/update/{id}")
def update_task(
    request: Request,
    id: int,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
):
    username = login_required(request)
    if isinstance(username, RedirectResponse):
        return username

    title = title.strip()
    description = description.strip()

    if not title or len(title) > 150:
        raise HTTPException(status_code=400, detail="Invalid task title")
    if len(description) > 300:
        raise HTTPException(status_code=400, detail="Description too long")
    if priority not in ("High", "Medium", "Low"):
        raise HTTPException(status_code=400, detail="Invalid priority")

    db = SessionLocal()
    try:
        task = get_owned_task(db, id, username)
        task.title = title
        task.description = description
        task.priority = priority
        db.commit()
        return RedirectResponse("/", status_code=303)
    finally:
        db.close()

@app.post("/delete/{id}")
def delete_task(request: Request, id: int):
    username = login_required(request)
    if isinstance(username, RedirectResponse):
        return username

    db = SessionLocal()
    try:
        task = get_owned_task(db, id, username)
        db.delete(task)
        db.commit()
        return RedirectResponse("/", status_code=303)
    finally:
        db.close()

@app.get("/set-theme/{theme}")
def set_theme(request: Request, theme: str):
    username = login_required(request)
    if isinstance(username, RedirectResponse):
        return username

    if theme not in ("light", "dark"):
        raise HTTPException(status_code=400, detail="Invalid theme")

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key="theme",
        value=theme,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        samesite="lax",
        secure=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
    )
    return response

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
