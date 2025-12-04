from flask import Flask, request, redirect, url_for

app = Flask(__name__)

# In-memory task list (resets when server restarts)
tasks = []
next_id = 1


def render_page():
    """Return full HTML for the page with current tasks."""
    task_items = []
    for t in tasks:
        status_badge = (
            '<span class="badge badge-done">Done</span>'
            if t["completed"]
            else '<span class="badge badge-pending">In progress</span>'
        )
        title_class = "task-title completed" if t["completed"] else "task-title"

        actions = []
        if not t["completed"]:
            actions.append(
                f'<a href="/complete/{t["id"]}" class="btn btn-success btn-sm">✓</a>'
            )
        actions.append(
            f'<a href="/delete/{t["id"]}" class="btn btn-danger btn-sm">🗑</a>'
        )

        task_items.append(f"""
        <li class="task-item">
            <div class="task-left">
                <span class="status-dot {'complete' if t['completed'] else 'pending'}"></span>
                <div class="task-text">
                    <div class="{title_class}">{t["title"]}</div>
                    {status_badge}
                </div>
            </div>
            <div class="task-actions">
                {' '.join(actions)}
            </div>
        </li>
        """)

    task_list_html = (
        "<ul class='task-list'>" + "".join(task_items) + "</ul>"
        if task_items
        else """
        <div class="empty-state">
            <div class="empty-icon">📭</div>
            <p>No tasks yet.</p>
            <p class="hint">Add your first task using the box above 🚀</p>
        </div>
        """
    )

    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    pending = total - completed

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TaskFlow – Stylish Task Manager</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    body {{
      min-height: 100vh;
      background: radial-gradient(circle at top left, #3b82f6 0, #1e293b 40%, #020617 100%);
      color: #f9fafb;
      display: flex;
      justify-content: center;
      padding: 40px 16px;
    }}
    .app {{
      width: 100%;
      max-width: 900px;
    }}
    .navbar {{
      background: rgba(15, 23, 42, 0.9);
      border-radius: 16px;
      padding: 14px 20px;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.35);
      backdrop-filter: blur(18px);
    }}
    .navbar-title {{
      font-weight: 600;
      font-size: 1.1rem;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .navbar-icon {{
      background: linear-gradient(135deg, #22c55e, #16a34a);
      border-radius: 10px;
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      box-shadow: 0 0 12px rgba(34,197,94,0.7);
    }}

    .stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }}
    .stat-card {{
      border-radius: 14px;
      padding: 12px 14px;
      background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,64,175,0.7));
      border: 1px solid rgba(148,163,184,0.4);
    }}
    .stat-label {{
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.7rem;
      opacity: 0.75;
      margin-bottom: 4px;
    }}
    .stat-value {{
      font-size: 1.4rem;
      font-weight: 700;
    }}
    .stat-total {{ border-color: rgba(129,140,248,0.8); }}
    .stat-pending {{ border-color: rgba(251,191,36,0.8); }}
    .stat-completed {{ border-color: rgba(34,197,94,0.9); }}

    .card {{
      background: rgba(15,23,42,0.96);
      border-radius: 20px;
      padding: 24px 22px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      backdrop-filter: blur(20px);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}
    .card-header h2 {{
      font-size: 1.3rem;
      font-weight: 600;
    }}
    .card-header p {{
      font-size: 0.85rem;
      color: #9ca3af;
    }}

    .add-form {{
      display: flex;
      gap: 8px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }}
    .add-input {{
      flex: 1 1 200px;
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.5);
      padding: 10px 14px;
      background: rgba(15,23,42,0.9);
      color: #f9fafb;
      outline: none;
      font-size: 0.95rem;
    }}
    .add-input::placeholder {{
      color: #6b7280;
    }}
    .btn {{
      border-radius: 999px;
      padding: 9px 16px;
      border: none;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: transform 0.08s ease, box-shadow 0.08s ease, background 0.15s ease;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, #3b82f6, #2563eb);
      color: #f9fafb;
      box-shadow: 0 10px 25px rgba(37,99,235,0.5);
    }}
    .btn-primary:hover {{
      transform: translateY(-1px);
      box-shadow: 0 14px 35px rgba(37,99,235,0.7);
    }}
    .btn-ghost {{
      background: transparent;
      color: #e5e7eb;
      border: 1px solid rgba(148,163,184,0.5);
    }}
    .btn-ghost:hover {{
      background: rgba(15,23,42,0.7);
    }}
    .btn-sm {{
      font-size: 0.8rem;
      padding: 6px 10px;
    }}
    .btn-success {{
      background: rgba(22,163,74,0.12);
      border: 1px solid rgba(34,197,94,0.8);
      color: #4ade80;
    }}
    .btn-danger {{
      background: rgba(220,38,38,0.12);
      border: 1px solid rgba(248,113,113,0.85);
      color: #fca5a5;
    }}
    .btn-success:hover {{
      background: rgba(22,163,74,0.25);
    }}
    .btn-danger:hover {{
      background: rgba(220,38,38,0.25);
    }}

    .task-list {{
      list-style: none;
      margin-top: 8px;
    }}
    .task-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid rgba(31,41,55,0.9);
    }}
    .task-item:last-child {{
      border-bottom: none;
    }}
    .task-left {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 1 1 auto;
    }}
    .status-dot {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      flex-shrink: 0;
    }}
    .status-dot.pending {{
      background: linear-gradient(135deg, #facc15, #f97316);
      box-shadow: 0 0 10px rgba(249,115,22,0.8);
    }}
    .status-dot.complete {{
      background: linear-gradient(135deg, #22c55e, #16a34a);
      box-shadow: 0 0 10px rgba(34,197,94,0.8);
    }}
    .task-text {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .task-title {{
      font-size: 0.95rem;
    }}
    .task-title.completed {{
      text-decoration: line-through;
      opacity: 0.6;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      font-size: 0.7rem;
      border-radius: 999px;
    }}
    .badge-pending {{
      background: rgba(250,204,21,0.12);
      color: #facc15;
      border: 1px solid rgba(250,204,21,0.7);
    }}
    .badge-done {{
      background: rgba(22,163,74,0.12);
      color: #4ade80;
      border: 1px solid rgba(34,197,94,0.7);
    }}
    .task-actions {{
      display: flex;
      gap: 6px;
      margin-left: 10px;
    }}

    .empty-state {{
      text-align: center;
      padding: 24px 10px 8px;
      color: #9ca3af;
    }}
    .empty-icon {{
      font-size: 2.3rem;
      margin-bottom: 6px;
    }}
    .hint {{
      font-size: 0.8rem;
      opacity: 0.8;
    }}

    @media (max-width: 640px) {{
      .card {{
        padding: 18px 16px;
      }}
      .stats {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
      }}
      .task-actions {{
        flex-direction: row;
      }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <div class="navbar">
      <div class="navbar-icon">✔</div>
      <div class="navbar-title">TaskFlow · Minimal Backend, Fancy UI</div>
    </div>

    <div class="stats">
      <div class="stat-card stat-total">
        <div class="stat-label">Total</div>
        <div class="stat-value">{total}</div>
      </div>
      <div class="stat-card stat-pending">
        <div class="stat-label">Pending</div>
        <div class="stat-value">{pending}</div>
      </div>
      <div class="stat-card stat-completed">
        <div class="stat-label">Completed</div>
        <div class="stat-value">{completed}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div>
          <h2>Your Tasks</h2>
          <p>Capture what matters, focus on what’s left.</p>
        </div>
        {"<a href='/clear-completed' class='btn btn-ghost btn-sm'>Clear completed</a>" if completed else ""}
      </div>

      <form method="POST" action="/add" class="add-form">
        <input
          type="text"
          name="title"
          class="add-input"
          placeholder="Add a new task (e.g., Finish Flask project)…"
          required
        >
        <button type="submit" class="btn btn-primary">Add task</button>
      </form>

      {task_list_html}
    </div>
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    return render_page()


@app.route("/add", methods=["POST"])
def add_task():
    global next_id
    title = request.form.get("title", "").strip()
    if title:
        tasks.append({"id": next_id, "title": title, "completed": False})
        next_id += 1
    return redirect(url_for("home"))


@app.route("/complete/<int:task_id>")
def complete(task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = True
            break
    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>")
def delete(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return redirect(url_for("home"))


@app.route("/clear-completed")
def clear_completed():
    global tasks
    tasks = [t for t in tasks if not t["completed"]]
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
