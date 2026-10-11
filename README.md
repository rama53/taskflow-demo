# TaskFlow

A simple task management app built with Flask and PostgreSQL.

## Technologies

* Python and Flask
* PostgreSQL
* Docker
* HTML, CSS, and JavaScript

## How to Run

### 1. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Run PostgreSQL in Docker

```bash
docker run --name taskflow-db -e POSTGRES_USER=taskflow -e POSTGRES_PASSWORD=taskflow -e POSTGRES_DB=taskflow -p 5432:5432 -d postgres:16
```

If the container already exists, run:

```bash
docker start taskflow-db
```

### 3. Run the Flask app

```bash
python app.py
```

### 4. Open the app

Visit http://127.0.0.1:5000 in your browser.

## Current Setup

* Flask runs on the local machine.
* PostgreSQL runs in a Docker container.
* The frontend is served by Flask.

## Next Step

Learn how to use Dockerfiles to run the application components in containers.
