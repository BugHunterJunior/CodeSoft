from database import get_db


# ─── User helpers ────────────────────────────────────────────────────────────

def create_user(username, email, password_hash):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash),
    )
    db.commit()


def get_user_by_email(email):
    return get_db().execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()


def get_user_by_username(username):
    return get_db().execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def get_user_by_id(user_id):
    return get_db().execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()


# ─── Task helpers ─────────────────────────────────────────────────────────────

def create_task(user_id, title, description, priority, due_date):
    db = get_db()
    db.execute(
        """INSERT INTO tasks (user_id, title, description, priority, due_date)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, title, description or "", priority, due_date or None),
    )
    db.commit()


def get_tasks(user_id, filter_by=None, sort_by=None, search=None):
    """
    Return tasks for a user with optional filtering, sorting and search.
    filter_by : 'pending' | 'completed' | None (all)
    sort_by   : 'priority' | 'due_date' | 'created_at' (default)
    search    : substring matched against title + description
    """
    params = [user_id]
    where  = "WHERE t.user_id = ?"

    if filter_by == "pending":
        where += " AND t.is_complete = 0"
    elif filter_by == "completed":
        where += " AND t.is_complete = 1"

    if search:
        where += " AND (t.title LIKE ? OR t.description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]

    priority_order = "CASE t.priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END"

    if sort_by == "priority":
        order = priority_order
    elif sort_by == "due_date":
        order = "CASE WHEN t.due_date IS NULL THEN 1 ELSE 0 END, t.due_date ASC"
    else:
        order = "t.created_at DESC"

    sql = f"""
        SELECT t.*, u.username
        FROM   tasks t
        JOIN   users u ON u.id = t.user_id
        {where}
        ORDER BY t.is_complete ASC, {order}
    """
    return get_db().execute(sql, params).fetchall()


def get_task(task_id, user_id):
    """Fetch a single task — always scoped to the owner."""
    return get_db().execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    ).fetchone()


def update_task(task_id, user_id, title, description, priority, due_date):
    db = get_db()
    db.execute(
        """UPDATE tasks
           SET title = ?, description = ?, priority = ?, due_date = ?
           WHERE id = ? AND user_id = ?""",
        (title, description or "", priority, due_date or None, task_id, user_id),
    )
    db.commit()


def delete_task(task_id, user_id):
    db = get_db()
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    )
    db.commit()


def toggle_complete(task_id, user_id):
    db = get_db()
    db.execute(
        """UPDATE tasks
           SET is_complete = CASE WHEN is_complete = 0 THEN 1 ELSE 0 END
           WHERE id = ? AND user_id = ?""",
        (task_id, user_id),
    )
    db.commit()
