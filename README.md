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
    networks:
      - taskflow-network

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
    networks:
      - taskflow-network

networks:
  taskflow-network:
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


### 5. Confirm the tasks disappear after recreating the containers

Use a disposable Part 3 database for this exercise. Add a few test tasks in
the app and refresh the page to confirm they were saved. Then run these
commands from the project directory:

```bash
docker compose down
docker compose up -d
```

Once the app is running again, refresh http://localhost:5000. The task list
should be empty. PostgreSQL 16 creates an anonymous volume for its data
directory when you omit a mount. After `docker compose down`, the replacement
database container gets a new anonymous volume. With `docker compose stop`
and `docker compose start`, Compose reuses the same containers and mounts.

### 6. Keep tasks with a named volume

A named volume gives PostgreSQL a stable place to store its data across container
recreations. For the `postgres:16` image used here, mount it at
`/var/lib/postgresql/data`.

In the `compose.yaml` from Part 3, add this under the existing `db` service:

```yaml
    volumes:
      - taskflow-data:/var/lib/postgresql/data
```

Declare the named volume at the top level of the same file, alongside
`services` and `networks`:

```yaml
volumes:
  taskflow-data:
```

The left side of the mount is the Docker volume name. The right side is the
directory PostgreSQL writes to inside the container. Compose creates the volume
on first use. If you previously ran PostgreSQL
without this named volume, switching mounts starts with a fresh database.
Export any tasks you want to keep from the old database before switching.

To verify that tasks survive container replacement, repeat the exercise with the named volume.

1. Run `docker compose up -d` to apply the new mount.
2. Open http://localhost:5000 and add a task.
3. From the same project directory, run:

   ```bash
   docker compose down
   docker compose up -d
   ```

4. Refresh the app and check that the task is still there.
5. Run `docker volume ls`. Compose normally prefixes the volume name with the
   project name, so look for a name such as `taskflow-demo_taskflow-data`.

`docker compose down` keeps the named volume. Running `docker compose down -v` removes it
and deletes the database stored in it.

**What we learned:** A named volume lets replacement containers reuse the same
database files.

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
# Part 4: Deploy TaskFlow on AWS EC2

This walkthrough runs Flask and PostgreSQL in Docker on one EC2 instance. It is a learning deployment using Flask's development server over HTTP. Use a production WSGI server, HTTPS, and managed secrets before hosting real users or sensitive data.

## 1. Create an EC2 instance

In the AWS Console, select your region, then open **EC2 → Instances → Launch instances**.

* **Name:** `taskflow-server`
* **AMI:** Ubuntu Server 24.04 LTS, **64-bit x86**
* **Instance type:** `t3.micro` for this small demo; check current regional pricing and your account's free-tier eligibility.
* **Key pair:** Create an RSA key pair. Download the `.pem` file and keep it private; AWS does not let you download it again.

Create a security group with these inbound rules:

| Type | Port | Source | Purpose |
| --- | --- | --- | --- |
| SSH | 22 | My IP | Connect from your computer |
| Custom TCP | 5000 | My IP | Open the demo application from your computer |

Keep the default outbound access so the instance can install packages and download images. **Do not add an inbound rule for PostgreSQL port 5432.** If your public IP changes, update both inbound rules. Allowing application access only from your IP keeps this demo private to you.

Click **Launch instance**. Wait until the instance is running and its status checks pass. Copy its **Public IPv4 address**.

## 2. Connect to the server

On your computer, open a terminal in the directory containing your downloaded key. Replace the example key name and `EC2_PUBLIC_IP` below:

```bash
chmod 400 taskflow-key.pem
ssh -i taskflow-key.pem ubuntu@EC2_PUBLIC_IP
```

On Windows, use OpenSSH in PowerShell or follow the instance's **Connect → SSH client** instructions to restrict key-file permissions. The Ubuntu AMI uses the username `ubuntu`.

All commands below run **inside the SSH session on EC2** unless stated otherwise.

## 3. Install Docker, Compose, and Git

Use Ubuntu's package repositories:

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git curl
sudo systemctl enable --now docker
sudo docker version
sudo docker compose version
```

These instructions use `sudo docker`, so adding your login user to the Docker group is unnecessary.

## 4. Download the application

```bash
git clone https://github.com/rama53/taskflow-demo.git
cd taskflow-demo
```

If the repository is private, use your organization's supported Git authentication or securely copy the checkout from your computer. Never put access tokens in clone URLs or commit credentials.

## 5. Create the Docker configuration

The repository describes Dockerfile and Compose files as exercises. If you have already created them, review and reuse them; the commands below write those files.

Create the application image definition:

```bash
cat > Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY frontend/ ./frontend/
EXPOSE 5000
CMD ["python", "app.py"]
EOF
```

Create a local environment file with a randomly generated database password. Run this only when `.env` does not already exist; keep the same password when reusing an initialized database volume.

```bash
if [ ! -e .env ]; then
  (umask 077; python3 -c 'import secrets; print("POSTGRES_PASSWORD=" + secrets.token_hex(24))' > .env)
fi
```

Keep `.env` private and out of Git. To exclude it locally without changing the repository's shared ignore rules:

```bash
grep -qxF '/.env' .git/info/exclude || echo '/.env' >> .git/info/exclude
```

Create the Compose configuration:

```bash
cat > compose.yaml <<'EOF'
services:
  app:
    build: .
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://taskflow:${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}@db:5432/taskflow
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: taskflow
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}
      POSTGRES_DB: taskflow
    volumes:
      - taskflow-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskflow -d taskflow"]
      interval: 5s
      timeout: 3s
      retries: 20

volumes:
  taskflow-data:
EOF
```

Compose gives the services a shared network. Flask connects to PostgreSQL using the service name `db`. The database has no published host port, and the named volume retains tasks when containers are recreated. This volume is local storage, not a backup.

## 6. Start and verify the application

```bash
sudo docker compose up -d --build
sudo docker compose ps
sudo docker compose logs --tail=50 app db
curl --fail http://localhost:5000/api/tasks
```

The first build can take several minutes. Confirm the database is healthy and the app is running. On a new database, the API returns `[]`.

On **your computer**, open:

```text
http://EC2_PUBLIC_IP:5000
```

Use **HTTP**, and include port **5000**: the current frontend sends API requests to that port. Add a task, click its title to complete it, refresh to confirm it persists, and click **remove** to delete it.

If the page does not load:

* Confirm you used the instance's current public IP and port 5000.
* Check the security group's port 5000 source matches your computer's current public IP.
* Run the local `curl` check above. If that fails, inspect `sudo docker compose logs --tail=100 app db`.
* If SSH also fails, check the port 22 rule, username, key pair, public subnet route, and instance status checks.
* If the database reports a password mismatch, check whether `.env` was changed after the volume was initialized. Restore the original password or deliberately rotate the database role's password; editing `.env` alone does not update an existing database.

## 7. Update, stop, and clean up

To deploy later application changes, from `~/taskflow-demo`:

```bash
git pull --ff-only
sudo docker compose up -d --build
sudo docker compose ps
```

To stop and remove the containers while retaining database data:

```bash
sudo docker compose down
```

Start them again with `sudo docker compose up -d`. Docker starts automatically after a reboot, and the configured restart policies restart existing containers.

When finished with the demo, **terminate the EC2 instance** in the AWS Console. Termination is destructive: back up any data you need first. Review and delete any remaining EBS volumes, snapshots, or Elastic IP allocations that you no longer need. Stopping an instance does not remove its storage charges, and public IPv4 addresses can incur charges. The auto-assigned public IP can change after a stop/start.
