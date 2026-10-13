# TaskFlow — Learning Docker Step by Step

A simple task management application built with Flask, PostgreSQL, HTML, CSS, and JavaScript. This project demonstrates three ways to run an application using Docker.

## Technologies

* Python and Flask
* PostgreSQL
* HTML, CSS, and JavaScript
* Docker and Docker Compose

---

# Part 1: Run PostgreSQL in Docker

In this part, the Flask application runs directly on the host machine, while PostgreSQL runs inside a Docker container.

### 1. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Start PostgreSQL

```bash
docker run --name taskflow-db -e POSTGRES_USER=taskflow -e POSTGRES_PASSWORD=taskflow -e POSTGRES_DB=taskflow -p 5432:5432 -d postgres:16
```

If the `taskflow-db` container already exists and is stopped, start it with:

```bash
docker start taskflow-db
```

### 3. Run the Flask application

```bash
python app.py
```

### 4. Open the application

Visit http://localhost:5000 in your browser.

**What we learned:** Docker can run a database without requiring us to install PostgreSQL directly on our computer.

---

# Part 2: Dockerize the Flask Application

In this part, both Flask and PostgreSQL run in separate containers.

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

```bash
docker build -t taskflow-app .
```

### 3. Create a Docker network

```bash
docker network create taskflow-network
```

Connect the database container to the network:

```bash
docker network connect taskflow-network taskflow-db
```

If the network or connection already exists, skip the corresponding command.

### 4. Start the database

```bash
docker start taskflow-db
```

If it is already running, you can skip this command.

### 5. Run the application container

```bash
docker run --name taskflow-app --network taskflow-network -e DATABASE_URL=postgresql://taskflow:taskflow@taskflow-db:5432/taskflow -p 5000:5000 -d taskflow-app
```

### 6. Open the application

Visit http://localhost:5000.

**What we learned:** A Dockerfile defines how to build an image, and containers can communicate through a shared user-defined network.

---

# Part 3: Use Docker Compose

Docker Compose lets us define and manage multiple services using one YAML file instead of manually running several Docker commands.

### 1. Create `compose.yaml`

Create this file in the project root, next to the Dockerfile:

```yaml
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://taskflow:taskflow@db:5432/taskflow
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: taskflow
      POSTGRES_PASSWORD: taskflow
      POSTGRES_DB: taskflow
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskflow -d taskflow"]
      interval: 5s
      timeout: 3s
      retries: 5
```

### 2. Start the application

If the containers are still running, stop the old containers first.
```bash
docker stop taskflow-app taskflow-db
```

Then run:

```bash
docker compose up --build
```

Docker Compose will:

* Build the Flask application image.
* Create and start the application and database containers.
* Create a shared network automatically.
* Wait for PostgreSQL's health check to pass before starting Flask.

### 3. Open the application

Visit http://localhost:5000.

### 4. Check the running services

Open another terminal and run:

```bash
docker compose ps
```

### 5. View application logs

```bash
docker compose logs app
```

### 6. Stop the application

Press `Ctrl+C` in the attached terminal, then run:

```bash
docker compose down
```

**Note:** This configuration does not define a named database volume. Removing the database container can therefore remove its stored data. A named volume can be added to preserve database data across container recreation.

**What we learned:** Docker Compose simplifies multi-container applications by managing their configuration, networking, startup order, and lifecycle in one place.

---

## Project Structure

```text
docker-demo-day1/
├── app.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

## Key Takeaways

| Concept          | Purpose                                                  |
| ---------------- | -------------------------------------------------------- |
| Docker image     | A template used to create containers                     |
| Docker container | A running instance of an image                           |
| Dockerfile       | Defines how to build an application image                |
| Docker network   | Allows containers to communicate                         |
| Docker Compose   | Defines and manages multiple services together           |
| Port mapping     | Makes a container service accessible through a host port |
| Health check     | Checks whether a service is ready to respond             |

## Next Steps

* Add a named volume to persist PostgreSQL data.
* Explore environment variables and `.env` files.
* Learn about Docker Compose service dependencies and health checks.
* Learn how to rebuild and update application containers.
