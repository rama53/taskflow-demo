# TaskFlow

A simple task management app built with Flask and PostgreSQL.

## Technologies

* Python and Flask
* PostgreSQL
* Docker
* HTML, CSS, and JavaScript

# Part 1: Running PostgreSQL in Docker

In this step, PostgreSQL runs in a Docker container, while Flask runs locally.

### 1. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Run PostgreSQL

```bash
docker run --name taskflow-db -e POSTGRES_USER=taskflow -e POSTGRES_PASSWORD=taskflow -e POSTGRES_DB=taskflow -p 5432:5432 -d postgres:16
```

If the container already exists, start it:

```bash
docker start taskflow-db
```

### 3. Run the Flask app

```bash
python app.py
```

### 4. Open the app

Visit http://127.0.0.1:5000 in your browser.

---

# Part 2: Dockerizing the Application Using a Dockerfile

In this step, we create a Docker image for the Flask application and run it in a container.

### 1. Create a Dockerfile

Create a file named `Dockerfile` in the project root:

```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY frontend/ ./frontend/

EXPOSE 5000

CMD ["python", "app.py"]
```

### 2. Build the application image

Run this command in the project directory:

```bash
docker build -t taskflow-app .
```

### 3. Create a Docker network

The network allows the application container to communicate with PostgreSQL.

```bash
docker network create taskflow-network
```

If the network already exists, skip this command.

### 4. Connect PostgreSQL to the network

```bash
docker network connect taskflow-network taskflow-db
```

If the database is already connected, skip this command.

Make sure PostgreSQL is running:

```bash
docker start taskflow-db
```

### 5. Run the application container

```bash
docker run --name taskflow-app --network taskflow-network -e DATABASE_URL=postgresql://taskflow:taskflow@taskflow-db:5432/taskflow -p 5000:5000 -d taskflow-app
```

If the container already exists, start it instead:

```bash
docker start taskflow-app
```

### 6. Open the application

Visit http://localhost:5000 in your browser.

### 7. Check running containers

```bash
docker ps
```

To view application logs:

```bash
docker logs taskflow-app
```

## Current Setup

* The frontend and Flask backend run in one application container.
* PostgreSQL runs in a separate container.
* Both containers communicate through a Docker network.
* The application is accessible at http://localhost:5000.

## Next Step

Use Docker Compose to define and start the application and database together with one command.
