// The frontend and backend are separate containers on separate ports.
// The browser calls the backend directly at the same host, port 5000
// (works the same on localhost and on a real server's public IP).
const API = `http://${window.location.hostname}:5000/api/tasks`;

const form = document.getElementById("task-form");
const input = document.getElementById("task-input");
const list = document.getElementById("task-list");

async function loadTasks() {
  const res = await fetch(API);
  const tasks = await res.json();
  render(tasks);
}

function render(tasks) {
  list.innerHTML = "";
  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = "task" + (task.done ? " done" : "");

    const title = document.createElement("span");
    title.className = "task-title";
    title.textContent = task.title;
    title.addEventListener("click", () => toggleTask(task.id));

    const del = document.createElement("button");
    del.textContent = "remove";
    del.addEventListener("click", () => deleteTask(task.id));

    li.append(title, del);
    list.appendChild(li);
  }
}

async function addTask(title) {
  await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  loadTasks();
}

async function toggleTask(id) {
  await fetch(`${API}/${id}`, { method: "PATCH" });
  loadTasks();
}

async function deleteTask(id) {
  await fetch(`${API}/${id}`, { method: "DELETE" });
  loadTasks();
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const title = input.value.trim();
  if (!title) return;
  input.value = "";
  addTask(title);
});

loadTasks();
