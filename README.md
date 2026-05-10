# Movies & Shows tracker (school-style mini project)

A tiny desktop app: **Tkinter** for the window and **SQLite** for saving your list.

## Files

| File | What it does |
|------|----------------|
| `main.py` | The GUI (buttons, table, search) and validation before saving. |
| `database.py` | Opens `media_tracker.db`, creates the table if needed, and runs SQL insert/update/delete/select. |

## Run

```bash
python main.py
```

Uses only the Python standard library (no `pip install` needed). First run creates **`media_tracker.db`** next to the scripts.

## How it works

1. **`database.init_db()`** runs when you open the app so the `media` table exists.
2. The big table is a **`ttk.Treeview`**. Each row’s **`iid`** is the same as the **`id`** column in SQLite so we know what to update or delete.
3. **`Save`** either **`INSERT`**s (new row, form cleared / nothing selected) or **`UPDATE`**s (you clicked a row first).
4. **Notes** are stored in the database but only shown in the text box when you select a row (the table columns stay simple).

See the **docstrings** inside `main.py` and `database.py` for more step-by-step comments.
