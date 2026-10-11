
import os

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request, send_from_directory

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path="/static"
)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://taskflow:taskflow@localhost:5432/taskflow"
)


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )
    finally:
        conn.close()


# Serve the frontend homepage
@app.get("/")
def home():
    return send_from_directory("frontend", "index.html")


# Get all tasks
@app.get("/api/tasks")
def list_tasks():
    conn = get_connection()
    try:
        with conn, conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(
                "SELECT id, title, done FROM tasks ORDER BY id DESC"
            )
            tasks = cur.fetchall()
        return jsonify(tasks)
    finally:
        conn.close()


# Create a task
@app.post("/api/tasks")
def create_task():
    data = request.get_json()
    title = data["title"]

    conn = get_connection()
    try:
        with conn, conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(
                """
                INSERT INTO tasks (title)
                VALUES (%s)
                RETURNING id, title, done
                """,
                (title,),
            )
            task = cur.fetchone()
        return jsonify(task), 201
    finally:
        conn.close()


# Toggle a task's completed status
@app.patch("/api/tasks/<int:task_id>")
def toggle_task(task_id):
    conn = get_connection()
    try:
        with conn, conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(
                """
                UPDATE tasks
                SET done = NOT done
                WHERE id = %s
                RETURNING id, title, done
                """,
                (task_id,),
            )
            task = cur.fetchone()

        if task is None:
            return jsonify({"error": "Task not found"}), 404

        return jsonify(task)
    finally:
        conn.close()


# Delete a task
@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s",
                (task_id,),
            )
            deleted = cur.rowcount

        if deleted == 0:
            return jsonify({"error": "Task not found"}), 404

        return "", 204
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)