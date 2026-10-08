import sqlite3
from fastapi import FastAPI

app = FastAPI()


def get_db():
    db = sqlite3.connect("sql_app.db")
    db.row_factory = sqlite3.Row

    try:
        yield db
    finally:
        db.close()


@app.get("/users")
def get_users():

    db = get_db()

    cursor = db.cursor()

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()
    
    users['name']

    return [dict(user) for user in users]